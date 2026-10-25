"""Execute the reporting notebook and export an HTML reading copy without code."""
import os
import argparse
from pathlib import Path
import sys
import tempfile
import nbformat
from nbclient import NotebookClient
from nbconvert import HTMLExporter
from jupyter_client import KernelManager

ROOT=Path(__file__).resolve().parent

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--notebook',default='notebooks/airline_resilience.ipynb')
    parser.add_argument('--output',default='reports/airline_resilience.html')
    args=parser.parse_args()
    path=ROOT/args.notebook
    notebook=nbformat.read(path,as_version=4)
    nbformat.validate(notebook)
    with tempfile.TemporaryDirectory() as temp:
        os.environ.setdefault('MPLCONFIGDIR',temp)
        os.environ.setdefault('IPYTHONDIR',temp)
        os.environ.setdefault('JUPYTER_RUNTIME_DIR',temp)
        manager=KernelManager(kernel_name='python3')
        manager.kernel_spec.argv=[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}']
        client=NotebookClient(notebook,km=manager,timeout=180,resources={'metadata':{'path':str(ROOT)}})
        try:
            client.execute()
        finally:
            if manager.has_kernel:manager.shutdown_kernel(now=True)
    nbformat.write(notebook,path)
    exporter=HTMLExporter(template_name='lab',exclude_input=True,exclude_input_prompt=True,exclude_output_prompt=True)
    body,_=exporter.from_notebook_node(notebook)
    dest=ROOT/args.output
    dest.parent.mkdir(exist_ok=True)
    dest.write_text(body)
    print(f'Executed {sum(c.cell_type=="code" for c in notebook.cells)} code cells; exported {dest.name}')

if __name__=='__main__':main()
