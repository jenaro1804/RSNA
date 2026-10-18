"""Ejecuta y guarda todas las celdas con el Python actual, sin necesitar nbclient."""
from pathlib import Path
import sys
import time
import nbformat
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpec

path = Path(__file__).with_name('entrega3_feedforward.ipynb')
notebook = nbformat.read(path, as_version=4)
manager = KernelManager()
manager._kernel_spec = KernelSpec(argv=[sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'],
                                  display_name='Python redes', language='python')
manager.start_kernel(cwd=str(path.parent.parent))
client = manager.client()
client.start_channels()
try:
    client.wait_for_ready(timeout=120)
    for i, cell in enumerate(notebook.cells):
        if cell.cell_type != 'code':
            continue
        cell.outputs = []
        message_id = client.execute(cell.source)
        deadline = time.monotonic()+600
        error = None
        while time.monotonic() < deadline:
            message = client.get_iopub_msg(timeout=600)
            if message['parent_header'].get('msg_id') != message_id:
                continue
            kind, content = message['msg_type'], message['content']
            if kind == 'execute_input':
                cell.execution_count = content['execution_count']
            elif kind in ('stream', 'display_data', 'execute_result', 'error'):
                cell.outputs.append(nbformat.v4.output_from_msg(message))
                if kind == 'error':
                    error = f"{content['ename']}: {content['evalue']}"
            elif kind == 'status' and content['execution_state'] == 'idle':
                break
        else:
            raise TimeoutError(f'Celda {i+1} excedió diez minutos.')
        nbformat.write(notebook, path)
        print(f'Celda {i+1}: {"ERROR" if error else "OK"}', flush=True)
        if error:
            raise RuntimeError(error)
finally:
    client.stop_channels()
    manager.shutdown_kernel(now=True)
