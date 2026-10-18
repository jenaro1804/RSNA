"""Prepara un subconjunto real y pequeño de RSNA para el baseline FF.

Lee por HTTP Range el índice ZIP remoto, nunca el archivo completo.
Descarga cinco DICOM por estudio de una única serie sagital seleccionada.
"""
from __future__ import annotations

import io
import json
from pathlib import Path
import time
import zipfile

import numpy as np
import pandas as pd
import pydicom
from pydicom.pixels import apply_modality_lut
from PIL import Image, ImageOps
import requests

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'datos_ff'
LABELS = ['ACL', 'MCL', 'Medial Meniscus', 'Lateral Meniscus', 'Medial OA',
          'Lateral OA', 'PF OA', 'Effusion', 'Synovitis', "Baker's", 'Contusion', 'Fracture']
COMPETITION = 'rsna-knee-abnormality-detection'
N_SLICES = 5
IMAGE_SIZE = 32


class RemoteZip(io.RawIOBase):
    """Archivo de solo lectura por rangos, con límites para evitar descargas completas."""
    def __init__(self, url):
        self.url = url
        self.session = requests.Session()
        with self.session.get(url, headers={'Range': 'bytes=-65536'}, stream=True, timeout=120) as r:
            if r.status_code != 206:
                raise RuntimeError('El servidor no admite rangos; se cancela la descarga.')
            self.size = int(r.headers['Content-Range'].split('/')[-1])
        self.position = 0
        self.received = 0

    def seek(self, offset, whence=0):
        self.position = offset if whence == 0 else (self.position if whence == 1 else self.size) + offset
        return self.position

    def tell(self):
        return self.position

    def read(self, size=-1):
        size = self.size - self.position if size < 0 else size
        size = min(size, self.size - self.position)
        if size <= 0:
            return b''
        if size > 400 * 1024**2 or self.received + size > 600 * 1024**2:
            raise RuntimeError('Rango excede el límite del índice remoto.')
        start = self.position
        with self.session.get(self.url, headers={'Range': f'bytes={start}-{start+size-1}'},
                              stream=True, timeout=180) as r:
            if r.status_code != 206:
                raise RuntimeError('Se exige respuesta parcial HTTP 206.')
            expected = f'bytes {start}-{start+size-1}/{self.size}'
            if r.headers.get('Content-Range') != expected:
                raise RuntimeError('Rango remoto inesperado.')
            content = r.content
        if len(content) != size:
            raise RuntimeError('Rango incompleto.')
        self.position += size
        self.received += size
        return content


def select_series():
    train = pd.read_csv(ROOT / 'muestra_rsna/datos/train.csv')
    series = pd.read_csv(ROOT / 'muestra_rsna/datos/train_series.csv')
    labeled = train.loc[train[LABELS].notna().all(axis=1)].copy()
    candidates = series.loc[series.StudyInstanceUID.isin(labeled.StudyInstanceUID)].copy()
    candidates['sagittal'] = candidates.Anatomical_Plane.eq('Sagittal').astype(int)
    for col in ['Fluid_Sensitive', 'Fat_Suppression']:
        candidates[col] = candidates[col].astype(str).str.lower().isin(['true', '1', '1.0']).astype(int)
    candidates = candidates.sort_values(
        ['StudyInstanceUID', 'sagittal', 'Fluid_Sensitive', 'Fat_Suppression', 'SeriesInstanceUID'],
        ascending=[True, False, False, False, True])
    chosen = candidates.drop_duplicates('StudyInstanceUID')
    return labeled.merge(chosen, on='StudyInstanceUID', validate='one_to_one')


def build_index(selected):
    from kaggle.api.kaggle_api_extended import KaggleApi
    from kagglesdk.competitions.types.competition_api_service import ApiDownloadDataFilesRequest
    api = KaggleApi()
    api.authenticate()
    with api.build_kaggle_client() as client:
        req = ApiDownloadDataFilesRequest()
        req.competition_name = COMPETITION
        response = client.competitions.competition_api_client.download_data_files(req)
        remote = RemoteZip(response.url)
        wanted = set(selected.SeriesInstanceUID)
        index = {uid: [] for uid in wanted}
        with zipfile.ZipFile(remote) as archive:
            for item in archive.infolist():
                parts = Path(item.filename).parts
                if len(parts) >= 4 and parts[-2] in wanted and item.filename.endswith('.dcm'):
                    index[parts[-2]].append(item.filename)
        print(f'Índice leído: {remote.received / 1024**2:.1f} MiB; series encontradas: '
              f'{sum(bool(v) for v in index.values())}/{len(index)}', flush=True)
    return index


def convert(path):
    ds = pydicom.dcmread(path)
    raw = ds.pixel_array
    if raw.ndim != 2 or int(getattr(ds, 'SamplesPerPixel', 1)) != 1:
        raise ValueError('Solo se admiten cortes monocromáticos 2D.')
    valid = np.ones(raw.shape, dtype=bool)
    if hasattr(ds, 'PixelPaddingValue'):
        low, high = sorted([ds.PixelPaddingValue, getattr(ds, 'PixelPaddingRangeLimit', ds.PixelPaddingValue)])
        valid &= ~((raw >= low) & (raw <= high))
    image = np.asarray(apply_modality_lut(raw, ds), dtype=np.float32)
    valid &= np.isfinite(image)
    if not valid.any():
        raise ValueError('Sin píxeles válidos.')
    low, high = np.percentile(image[valid], [1, 99])
    if high <= low:
        raise ValueError('Imagen sin contraste útil.')
    image = np.nan_to_num(np.clip((image-low)/(high-low), 0, 1))
    if ds.PhotometricInterpretation == 'MONOCHROME1':
        image = 1-image
    image[~valid] = 0
    pil = Image.fromarray((image*255).round().astype('uint8'))
    pil = ImageOps.pad(pil, (IMAGE_SIZE, IMAGE_SIZE), method=Image.Resampling.BILINEAR, color=0)
    # La posición sirve para ordenar SOLO los cinco cortes ya seleccionados.
    if hasattr(ds, 'ImagePositionPatient') and hasattr(ds, 'ImageOrientationPatient'):
        orient = np.asarray(ds.ImageOrientationPatient, dtype=float)
        position = float(np.dot(np.cross(orient[:3], orient[3:]), ds.ImagePositionPatient))
    else:
        raise ValueError('No hay geometría para ordenar los cortes seleccionados.')
    patient = str(getattr(ds, 'PatientID', '')).strip()
    return np.asarray(pil, dtype=np.float32)/255, position, patient


def main():
    import hashlib
    from kaggle.api.kaggle_api_extended import KaggleApi
    from extraer_corte import download_one
    DATA.mkdir(exist_ok=True)
    selected = select_series()
    index_path = DATA / 'indice_series.json'
    if index_path.exists():
        index = json.loads(index_path.read_text(encoding='utf-8'))
    else:
        index = build_index(selected)
        index_path.write_text(json.dumps(index), encoding='utf-8')
    api = KaggleApi(); api.authenticate()
    images, labels, studies, patients, manifest = [], [], [], [], []
    for i, row in enumerate(selected.itertuples(index=False), 1):
        uid = row.StudyInstanceUID
        series_uid = row.SeriesInstanceUID
        names = sorted(index.get(series_uid, []))
        if len(names) < N_SLICES:
            raise RuntimeError(f'Serie {i} sin cinco cortes; revisar antes de entrenar.')
        # Muestreo reproducible del listado por UID. NO representa posiciones anatómicas.
        chosen = [names[j] for j in np.linspace(0, len(names)-1, N_SLICES).round().astype(int)]
        converted = []
        for name in chosen:
            path = DATA / 'dicom' / Path(name).name
            if not path.exists():
                for attempt in range(3):
                    try:
                        path = download_one(api, name, DATA / 'dicom')
                        break
                    except Exception:
                        if attempt == 2:
                            raise RuntimeError('Fallo de descarga individual; reejecutar para reanudar.') from None
                        time.sleep(2)
            converted.append((*convert(path), name))
        converted.sort(key=lambda entry: entry[1])
        patient_ids = {c[2] for c in converted}
        if len(patient_ids) != 1:
            raise RuntimeError('Identificadores inconsistentes dentro del estudio.')
        patient = converted[0][2]
        group = hashlib.sha256(patient.encode()).hexdigest() if patient else f'study:{uid}'
        images.append(np.stack([c[0] for c in converted]))
        labels.append(selected.loc[selected.StudyInstanceUID.eq(uid), LABELS].iloc[0].to_numpy(dtype=np.float32))
        studies.append(uid); patients.append(group)
        manifest.append({'study': uid, 'series': series_uid, 'plane': row.Anatomical_Plane,
                         'files': [c[3] for c in converted], 'patient_identifiable': bool(patient)})
        print(f'Estudios preparados: {i}/{len(selected)}', flush=True)
    np.savez_compressed(DATA / 'estudios_ff.npz', X=np.stack(images), y=np.stack(labels),
                        studies=np.asarray(studies), groups=np.asarray(patients), labels=np.asarray(LABELS))
    (DATA / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print('Dataset listo:', np.stack(images).shape, flush=True)


if __name__ == '__main__':
    main()
