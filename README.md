# Redes — Entrega 3

Primer experimento exploratorio de clasificación multietiqueta con una red
completamente conectada. Usa 58 estudios RSNA con etiquetas explícitas y tres
configuraciones. No usa convoluciones ni modelos preentrenados.

## En VS Code

1. `uv sync` para instalar las dependencias de `uv.lock`.
2. `uv run python preparar_ff.py` para preparar cinco DICOM por estudio.
   Requiere la autenticación existente de Kaggle y acceso a la competencia.
   Lee únicamente el índice remoto por rangos y descarga imágenes individuales.
   Las descargas existentes se reutilizan al reejecutar.
3. Abre `notebooks/entrega3_feedforward.ipynb` y selecciona el intérprete de `.venv`.
4. Ejecuta todas las celdas. No necesitas JupyterLab ni nbclient.

También puedes ejecutar y guardar sus salidas desde terminal:
`uv run python notebooks/ejecutar_notebook.py`.

El notebook contiene la arquitectura y entrenamiento completos, la partición fija,
las curvas, las métricas y una referencia constante basada en prevalencia.
`notebooks/construir_notebook.py` regenera la fuente del notebook y borra sus salidas;
no hace falta ejecutarlo para entrenar.

## Artefactos

- `datos_ff/`: DICOM, arreglo procesado, manifiesto y partición (datos privados,
  excluidos de Git).
- `resultados_ff/`: curvas PNG/PDF, historias y comparación CSV, observaciones,
  versiones y resumen JSON. Los pesos `.pt` se excluyen de Git.
- `muestra_rsna/`: extracción anterior para ilustrar el documento.

La selección por UID no representa posiciones anatómicas uniformes; la reducción
a 32 × 32 y el uso de una sola serie son simplificaciones del ejercicio.
Los 58 estudios dejan de ser una prueba independiente. La CNN requerirá un
protocolo posterior más formal. No se incorpora nada a Overtree antes de revisar
el código y los resultados.
