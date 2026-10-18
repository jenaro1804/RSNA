# Un corte real de RSNA para el reporte

El proyecto se prepara en `C:\Users\jenar\proyectos\redes`.

No es necesario descargar los 569 GB para esta figura. `extraer_corte.py`
lista rutas en Kaggle, descarga **un DICOM individual** y los dos CSV de
entrenamiento. No utiliza la descarga del dataset completo.

## Autenticación y ejecución en PowerShell

Con tu cuenta, acepta las reglas de la competencia en Kaggle. Después:

```powershell
cd C:\Users\jenar\proyectos\redes
.\.venv\Scripts\kaggle.exe auth login
.\.venv\Scripts\python.exe .\extraer_corte.py
```

El primer comando de Kaggle solicita autenticación en el navegador.
Si prefieres un token, sigue las instrucciones oficiales:
https://github.com/Kaggle/kaggle-cli/blob/main/docs/README.md#authentication
No pegues credenciales en el notebook, código o chat.

Si la búsqueda no encuentra un archivo individual dentro del límite de páginas,
abre Data en la competencia, copia la ruta completa de un `.dcm` de
`train_series/` y úsala así:

```powershell
.\.venv\Scripts\python.exe .\extraer_corte.py --archivo "train_series/ESTUDIO/SERIE/IMAGEN.dcm"
```

`ESTUDIO/SERIE/IMAGEN` son marcadores: sustitúyelos por la ruta real.
También puedes convertir un archivo ya descargado sin conectarte a Kaggle:

```powershell
.\.venv\Scripts\python.exe .\extraer_corte.py --local "ruta\real\corte.dcm"
```

## Resultados

- `muestra_rsna/corte_rodilla.png`: imagen monocromática para el reporte.
- `muestra_rsna/figura_corte.tex`: figura y párrafo listos para la plantilla.
- `muestra_rsna/resumen_dataset.json`: dimensiones, procesamiento y conteos
  de etiquetas explícitas; no incluye textos de reportes ni identificación del paciente.
- `muestra_rsna/datos/`: el corte y los CSV descargados. Mantenerlos privados.

En Overtree, sube `corte_rodilla.png` y pega el bloque de `figura_corte.tex`
en III.c, Ejemplos y consideraciones. Usa la referencia `rsnadata` ya existente.
El script no sube automáticamente archivos a Overtree.

El ajuste de contraste es únicamente para visualización. No identifica una lesión
ni se interpreta el orden de los nombres de archivo como posición anatómica.
Los cortes de un estudio no son pacientes independientes.

## Para entrenar después

La descarga de un corte sirve para ilustrar el reporte, no para entrenar una CNN.
Para entrenar localmente se necesita descargar un subconjunto de estudios completos
(todas las series y cortes seleccionados) y sus etiquetas. También se puede trabajar
en Kaggle Notebooks con los datos de la competencia adjuntos, sin descargarlos al PC;
eso no requiere Colab. La separación de entrenamiento y validación debe mantener
cada estudio, y cada paciente identificable, dentro de una sola partición.

Fuentes oficiales:

- https://github.com/Kaggle/kaggle-cli/blob/main/docs/competitions.md
- https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/data

