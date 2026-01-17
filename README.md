# Kubernetes-Clone

Simplified, in-memory Kubernetes-style orchestrator with implementations in both Python and Go for learning purposes.

## Layout
- `python/` — Python implementation with CLI, scheduler, services, persistence, and tests
- `go/` — Go implementation with Cobra CLI, scheduler, services, and replica management

## Python Quick Start
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

## Go Quick Start
- Build: `cd go && go build -o kclone ./cmd/kclone`
- Run help: `./kclone --help`
- Demo: `cd go && go run ./cmd/demo`

## Go Commands
Each CLI invocation is stateless. Use `go run ./cmd/demo` for a persistent demo session showing full orchestration.

- Add node: `go run ./cmd/kclone node-add node-a --cpu 4 --mem 4096`
- List nodes: `go run ./cmd/kclone nodes`
- Create pod: `go run ./cmd/kclone pod-create web-1 --image nginx:latest --labels app=web`
- List pods: `go run ./cmd/kclone pods`
- Delete pod: `go run ./cmd/kclone pod-delete pod-1`
- Create deployment: `go run ./cmd/kclone deploy-create web --image nginx:latest --replicas 3`
- Scale deployment: `go run ./cmd/kclone deploy-scale web --replicas 2`
- Create service: `go run ./cmd/kclone service-create web --selector app=web --port 80`
- Route request: `go run ./cmd/kclone service-route web`
- Cluster status: `go run ./cmd/kclone status`

## Implementation Details
Both implementations provide:
- **Pod scheduling** with resource-aware placement
- **Service abstraction** with virtual IPs and round-robin routing
- **Replica management** via deployments
- **Resource tracking** at node and cluster level
- **CLI** for managing the orchestrator
