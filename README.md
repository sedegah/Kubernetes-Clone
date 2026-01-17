# Kubernetes-Clone

Simplified, in-memory Kubernetes-style orchestrator built in Python for learning purposes.

## Features
- Pod lifecycle: create/delete pods with CPU/memory requests and labels.
- Scheduler: places pending pods onto nodes honoring resource capacity.
- Replica management: lightweight deployments that reconcile desired replica counts.
- Service abstraction: virtual IPs with label selectors and round-robin routing.
- Resource tracking: per-node and cluster-level resource usage.
- CLI: manage nodes, pods, deployments, and services from the terminal.

## Quick start
1) Create a virtual environment and install dependencies:
	- `python -m venv .venv`
	- `source .venv/bin/activate`
	- `pip install -r requirements.txt`

2) Run the CLI:
	- `python -m kclone --help`

## Common commands
- Add nodes: `python -m kclone node-add node-a --cpu 4 --mem 4096`
- List nodes: `python -m kclone nodes`
- Create a pod: `python -m kclone pod-create web-1 --image nginx:latest --labels app=web`
- List pods: `python -m kclone pods`
- Delete a pod: `python -m kclone pod-delete pod-1`
- Create a deployment: `python -m kclone deploy-create web --image nginx:latest --replicas 3 --labels app=web`
- Scale a deployment: `python -m kclone deploy-scale web --replicas 2`
- Create a service: `python -m kclone service-create web --selector app=web --port 80 --target-port 80`
- Route through a service: `python -m kclone service-route web`
- Cluster resource status: `python -m kclone status`
- Persist cluster state: `python -m kclone state-save state.json`
- Restore cluster state: `python -m kclone state-load state.json`

## Notes
- Everything runs in-memory; restarting the CLI resets state.
- Scheduling will mark pods as failed if no node has sufficient free CPU/memory.

## Tests
- Install dev dependency `pytest` from requirements.
- Run tests: `pytest`
