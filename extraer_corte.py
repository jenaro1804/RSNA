"""Descarga selectiva de un DICOM RSNA y conversión a PNG para el reporte.

Uso: python extraer_corte.py
     python extraer_corte.py --local ruta/al/corte.dcm
Nunca descarga el conjunto completo. Requiere acceso autorizado en Kaggle.
"""
from __future__ import annotations

import argparse
import csv
import json
import inspect
from pathlib import Path, PurePosixPath
import sys
import zipfile

COMPETITION = "rsna-knee-abnormality-detection"
MAX_DICOM_BYTES = 20 * 1024 * 1024


def download_one(api, name: str, folder: Path) -> Path:
    """Descarga solo la ruta solicitada; nunca usa download_files()."""
    remote = PurePosixPath(name)
    if remote.is_absolute() or ".." in remote.parts or ":" in name or "\\" in name:
        raise ValueError("Ruta remota no válida")
    folder.mkdir(parents=True, exist_ok=True)
    options = dict(file_name=name, path=str(folder), quiet=True)
    if "unzip" in inspect.signature(api.competition_download_file).parameters:
        options["unzip"] = True
    api.competition_download_file(COMPETITION, **options)
    candidates = [folder.joinpath(*remote.parts), folder / remote.name]
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    for candidate in candidates:
        archive = Path(str(candidate) + ".zip")
        if not archive.is_file():
            continue
        with zipfile.ZipFile(archive) as bundle:
            files = [m for m in bundle.infolist() if not m.is_dir()]
            if len(files) != 1 or PurePosixPath(files[0].filename).name != remote.name:
                raise RuntimeError("Se esperaba un ZIP de un solo archivo individual")
            if files[0].file_size > 50 * 1024 * 1024:
                raise RuntimeError("El archivo individual excede el límite de extracción")
            target = folder / remote.name
            target.write_bytes(bundle.read(files[0]))
            return target
    raise RuntimeError(f"No se encontró el archivo individual descargado: {name}")


def find_dicom(api, pages: int) -> str:
    """Solo lista metadatos; los cientos de archivos listados no se descargan."""
    token = None
    for page in range(pages):
        response = api.competition_list_files(
            COMPETITION, page_token=token, page_size=200
        )
        candidates = []
        for item in response.files:
            name = str(item.name)
            size = getattr(item, "total_bytes", None)
            if name.startswith("train_series/") and name.lower().endswith(".dcm"):
                if size is None or int(size) <= MAX_DICOM_BYTES:
                    candidates.append(name)
        if candidates:
            # No se interpreta el orden de UID como posición anatómica.
            return candidates[0]
        token = response.next_page_token
        if not token:
            break
    raise RuntimeError(
        "No apareció un DICOM individual en las páginas consultadas. "
        "Usa --archivo con una ruta exacta del explorador Data de Kaggle "
        "o aumenta --paginas. No se descargará un ZIP completo como alternativa."
    )


def inspect_csv(train_path: Path, series_path: Path, remote: str) -> dict:
    with train_path.open(encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    labels = ["ACL", "MCL", "Medial Meniscus", "Lateral Meniscus", "Medial OA",
              "Lateral OA", "PF OA", "Effusion", "Synovitis", "Baker's",
              "Contusion", "Fracture"]
    counts = {}
    for label in labels:
        values = [r.get(label, "").strip() for r in rows]
        positives = sum(v in ("1", "1.0") for v in values)
        negatives = sum(v in ("0", "0.0") for v in values)
        counts[label] = {
            "positivos_explicitos": positives,
            "negativos_explicitos": negatives,
            "sin_etiqueta_binaria": len(rows) - positives - negatives,
        }
    # El resumen no contiene textos de reportes ni datos personales.
    summary = {"estudios_entrenamiento": len(rows), "etiquetas": counts}
    parts = PurePosixPath(remote).parts
    if len(parts) >= 4:
        with series_path.open(encoding="utf-8-sig", newline="") as stream:
            for row in csv.DictReader(stream):
                if row.get("SeriesInstanceUID") == parts[-2]:
                    summary["plano_corte"] = row.get("Anatomical_Plane", "")
                    break
    return summary


def convert_to_png(source: Path, output: Path) -> dict:
    import numpy as np
    import pydicom
    from pydicom.pixels import apply_modality_lut, apply_voi_lut
    from PIL import Image

    ds = pydicom.dcmread(source)
    if int(getattr(ds, "SamplesPerPixel", 1)) != 1:
        raise ValueError("Se esperaba una imagen monocromática de resonancia")
    pixels = ds.pixel_array
    frame = None
    if pixels.ndim == 3:
        frame = len(pixels) // 2
        pixels = pixels[frame]
    if pixels.ndim != 2:
        raise ValueError(f"Dimensiones de imagen no soportadas: {pixels.shape}")
    mask = np.ones(pixels.shape, dtype=bool)
    if hasattr(ds, "PixelPaddingValue"):
        padding = ds.PixelPaddingValue
        other = getattr(ds, "PixelPaddingRangeLimit", padding)
        low_padding, high_padding = sorted((padding, other))
        mask &= ~((pixels >= low_padding) & (pixels <= high_padding))
    image = apply_modality_lut(pixels, ds)
    voi_applied = False
    if hasattr(ds, "VOILUTSequence") or (
        hasattr(ds, "WindowCenter") and hasattr(ds, "WindowWidth")
    ):
        image = apply_voi_lut(image, ds)
        voi_applied = True
    image = np.asarray(image, dtype=np.float64)
    mask &= np.isfinite(image)
    if not np.any(mask):
        raise ValueError("El corte no contiene píxeles válidos")
    low, high = np.percentile(image[mask], [1, 99])
    if high <= low:
        low, high = image[mask].min(), image[mask].max()
    if high <= low:
        raise ValueError("El corte es uniforme; selecciona otro archivo")
    normalized = np.nan_to_num(np.clip((image - low) / (high - low), 0, 1))
    if getattr(ds, "PhotometricInterpretation", "") == "MONOCHROME1":
        normalized = 1 - normalized
    normalized[~mask] = 0
    output.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray((normalized * 255).round().astype(np.uint8)).save(output)
    # No se imprimen ni exportan etiquetas de identificación del paciente.
    return {
        "filas": int(pixels.shape[0]), "columnas": int(pixels.shape[1]),
        "fotometria": str(getattr(ds, "PhotometricInterpretation", "")),
        "frame_multiframe": frame, "voi_aplicado": voi_applied,
        "contraste": "normalización visual con percentiles 1 y 99",
        "orientacion": "original del DICOM, sin giros ni volteos",
        "uso": "figura ilustrativa; no determina un diagnóstico",
    }


def write_figure(folder: Path, plane: str = "") -> None:
    planes = {"Sagittal": "sagital", "Coronal": "coronal", "Axial": "axial"}
    orientation = " " + planes[plane] if plane in planes else ""
    text = r"""\begin{figure}[htbp]
    \centering
    \includegraphics[width=\columnwidth]{corte_rodilla.png}
    \caption{Ejemplo de un corteORIENTACION de resonancia magnética de rodilla
    del conjunto RSNA Knee Abnormality Detection. Se ajustó el contraste
    para visualización \cite{rsnadata}.}
    \label{fig:corte-rodilla}
\end{figure}

La Fig.~\ref{fig:corte-rodilla} muestra una sección del interior de la rodilla.
Esta imagen es uno de los cortes que componen una serie del estudio;
no representa por sí sola el examen completo ni confirma un hallazgo clínico.
"""
    (folder / "figura_corte.tex").write_text(
        text.replace("ORIENTACION", orientation), encoding="utf-8"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--local", type=Path, help="Convierte un DICOM local sin Kaggle")
    parser.add_argument("--archivo", help="Ruta individual exacta dentro de Kaggle")
    parser.add_argument("--paginas", type=int, default=10, help="Máximo de páginas a listar")
    parser.add_argument("--salida", type=Path,
                        default=Path(__file__).resolve().parent / "muestra_rsna")
    args = parser.parse_args()
    if args.paginas < 1:
        parser.error("--paginas debe ser mayor que cero")
    args.salida.mkdir(parents=True, exist_ok=True)
    summary = {}
    remote = None
    if args.local:
        source = args.local.resolve(strict=True)
    else:
        # Kaggle autentica al importar; se retrasa para que --local y --help funcionen.
        from kaggle.api.kaggle_api_extended import KaggleApi
        api = KaggleApi()
        api.authenticate()
        remote = args.archivo or find_dicom(api, args.paginas)
        if not remote.startswith("train_series/") or not remote.lower().endswith(".dcm"):
            raise ValueError("--archivo debe señalar un .dcm individual de train_series/")
        print("Descargando un DICOM individual, no el dataset completo.")
        source = download_one(api, remote, args.salida / "datos")
        for name in ("train.csv", "train_series.csv"):
            download_one(api, name, args.salida / "datos")
        summary = inspect_csv(args.salida / "datos" / "train.csv",
                              args.salida / "datos" / "train_series.csv", remote)
    png = args.salida / "corte_rodilla.png"
    summary["visualizacion"] = convert_to_png(source, png)
    summary["competencia"] = COMPETITION
    summary["archivo_remoto"] = remote
    summary["procedencia"] = "DICOM local proporcionado" if args.local else "Kaggle oficial"
    (args.salida / "resumen_dataset.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    write_figure(args.salida, summary.get("plano_corte", ""))
    print(f"PNG generado: {png}")
    print(f"Bloque LaTeX: {args.salida / 'figura_corte.tex'}")
    if "estudios_entrenamiento" in summary:
        print(f"Estudios de entrenamiento: {summary['estudios_entrenamiento']}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        # Evita imprimir URLs firmadas, tokens o respuestas con información sensible.
        if error.__class__.__name__ in ("HTTPError", "ApiException", "KaggleApiError"):
            print("Kaggle rechazó la solicitud. Verifica autenticación, aceptación de "
                  "reglas y acceso a la competencia. No se descargó el conjunto completo.",
                  file=sys.stderr)
        elif isinstance(error, (ValueError, FileNotFoundError, ImportError, RuntimeError)):
            print(str(error), file=sys.stderr)
        else:
            print(f"La extracción falló ({type(error).__name__}). "
                  "Verifica acceso a Kaggle y dependencias DICOM.", file=sys.stderr)
        raise SystemExit(1)
