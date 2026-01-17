# Python README

See [../README.md](../README.md) for full project documentation.

## Quick Start
1) Create virtual environment and install:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2) Run CLI:
   ```bash
   PYTHONPATH=src python -m kclone --help
   ```

## Run Tests
```bash
pytest
```

## Example Usage
```bash
# Add nodes
PYTHONPATH=src python -m kclone node-add node-a --cpu 4 --mem 4096

# Create deployment
PYTHONPATH=src python -m kclone deploy-create web --image nginx:latest --replicas 3

# Create service
PYTHONPATH=src python -m kclone service-create web --selector app=web --port 80

# View status
PYTHONPATH=src python -m kclone status
```
