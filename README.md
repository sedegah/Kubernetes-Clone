# Kubernetes-Clone

Simplified, in-memory Kubernetes-style orchestrator built in Python for learning purposes. A Go scaffold lives alongside it for future work.

## Layout
- `python/` — full Python implementation (CLI, scheduler, services, persistence, tests)
- `go/` — Go scaffold (placeholder main, ready for expansion)

## Python quick start
1) Create a virtual environment inside `python/` and install deps:
	- `cd python`
	- `python -m venv .venv`
	- `source .venv/bin/activate`
	- `pip install -r requirements.txt`

2) Run the CLI (from `python/`):
	- `PYTHONPATH=src python -m kclone --help`

## Common Python commands
- Add nodes: `PYTHONPATH=src python -m kclone node-add node-a --cpu 4 --mem 4096`
- List nodes: `PYTHONPATH=src python -m kclone nodes`
- Create a pod: `PYTHONPATH=src python -m kclone pod-create web-1 --image nginx:latest --labels app=web`
- List pods: `PYTHONPATH=src python -m kclone pods`
- Delete a pod: `PYTHONPATH=src python -m kclone pod-delete pod-1`
- Create a deployment: `PYTHONPATH=src python -m kclone deploy-create web --image nginx:latest --replicas 3 --labels app=web`
- Scale a deployment: `PYTHONPATH=src python -m kclone deploy-scale web --replicas 2`
- Create a service: `PYTHONPATH=src python -m kclone service-create web --selector app=web --port 80 --target-port 80`
- Route through a service: `PYTHONPATH=src python -m kclone service-route web`
- Cluster resource status: `PYTHONPATH=src python -m kclone status`
- Persist cluster state: `PYTHONPATH=src python -m kclone state-save state.json`
- Restore cluster state: `PYTHONPATH=src python -m kclone state-load state.json`

## Notes
- Everything runs in-memory; restarting the CLI resets state.
- Scheduling will mark pods as failed if no node has sufficient free CPU/memory.

## Tests (Python)
- From `python/`, run: `pytest`

## Go scaffold
- Location: `go/`
- Build/run: `cd go && go run ./cmd/kclone`
- Currently a minimal placeholder to extend with a Go implementation of the orchestrator.
