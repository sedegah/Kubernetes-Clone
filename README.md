
# Kubernetes-Clone

Simplified, educational Kubernetes-style orchestrator implemented in both Go and Python. The project demonstrates core orchestration concepts such as scheduling, services, replica management, and state persistence with simple, readable code.

**Highlights:** lightweight scheduler (bin-packing), services with VIPs and round-robin routing, deployment controller, pluggable persistence (JSON/SQLite), and CLI tooling in both languages.

**Table of contents**
- Project overview
- Repository layout
- Quick start (Go / Python)
- Command reference (Go CLI & Python CLI)
- Makefile / targets
- Testing & development
- Contributing

## Project Overview

This repository contains two parallel implementations of the same simplified orchestrator:

- Go implementation: located under `go/`, CLI built with Cobra, optional SQLite-backed persistence.
- Python implementation: located under `python/`, CLI built with Click, optional SQLite-backed persistence and a small control loop.

Both implementations share the same conceptual features:

- Pod lifecycle: create/delete pods with resource requests
- Scheduling: resource-aware bin-packing to place pods on nodes
- Deployments: manage replica sets and reconcile desired state
- Services: virtual IP allocation and round-robin routing to pod endpoints
- State persistence: save/load cluster state to files or SQLite

## Repository Layout

Root files and folders:

- [go](go): Go source, commands, packages
- [python](python): Python source, CLI, and tests
- [Makefile](Makefile): helper targets for build, demo, test
- [README.md](README.md): this file

Go layout (high level):

- `go/cmd/kclone` — main CLI (`kclone`) and subcommands
- `go/cmd/demo` — demo runner that exercises features
- `go/pkg/*` — scheduler, controllers, persistence, models, service, etc.

Python layout (high level):

- `python/src/kclone` — package with CLI (`kclone`), controllers, scheduler, persistence, and modules
- `python/tests` — pytest test suite

## Quick Start

Prerequisites:

- Go 1.20+ to build/run the Go implementation
- Python 3.10+ and pip to install and run the Python implementation

Build and run (Go):

```bash
# Build the Go CLI (binary `kclone` in repo root)
make build-go

# Show help:
./kclone --help

# Bring cluster up with animated banner:
./kclone --up

# Or run the demo app (more end-to-end behavior):
make run-demo-go
```

Run (Python):

```bash
cd python
python -m venv .venv && source .venv/bin/activate
pip install -e .

# Show help:
python -m kclone --help

# Bring cluster up with banner:
python -m kclone --up

# Run the Python demonstration (alternate demo runner):
make run-demo-python
```

## Command Reference

Below are the commands available in each CLI. Examples show common flag usage.

Notes: both CLIs support a `--db` option to point to an SQLite DB (Python: `--db`, Go: `--db`). When a DB path is provided the implementations will attempt to load state and persist changes.

---

Go CLI (`kclone`)

Global flags (root):

- `--db <path>` — path to SQLite DB (default: `golang_cluster.db`)
- `--up` — show animated banner (equivalent to `kclone up`)

Commands:

- `node-add [name]` (aliases: `node`, `n`)
	- Flags: `--cpu/-c` (default 4), `--mem/-m` (default 4096), `--labels/-l` (key=value,comma-separated)
	- Example: `./kclone node-add node-a --cpu 4 --mem 4096`

- `nodes`
	- List nodes and resource usage

- `remove-node [name]` (aliases: `node-delete`, `node-rm`, `rm-node`)
	- Remove a node from cluster

- `pod-create [name]` (aliases: `pod`, `pod-add`, `p`)
	- Flags: `--image/-i` (required), `--cpu/-c` (default 1), `--mem/-m` (default 128), `--labels/-l`
	- Example: `./kclone pod-create mypod --image nginx:latest --cpu 1 --mem 128`

- `pods`
	- List pods with UID, image, phase and assigned node

- `pod-delete [uid]`
	- Delete pod by UID

- `deploy-create [name]`
	- Flags: `--image` (required), `--replicas` (default 1), `--selector`, `--labels`, `--cpu`, `--mem`
	- Example: `./kclone deploy-create web --image nginx:latest --replicas 3`

- `deploy-scale [name]`
	- Flags: `--replicas` (required)
	- Example: `./kclone deploy-scale web --replicas 5`

- `service-create [name]`
	- Flags: `--selector`, `--port` (default 80), `--target-port` (default 80)
	- Example: `./kclone service-create web --selector app=web --port 80`

- `services`
	- List services with VIP and endpoints

- `service-route [name]`
	- Simulate routing a request to the service; prints which pod handled it

- `status`
	- Show cluster-level CPU/MEM usage and totals

- `state-save [path]`
	- Persist cluster state to a file (JSON/same format used by persistence)

- `state-load [path]`
	- Load cluster state from a previously saved file

- `up`
	- Show the animated banner

Examples (Go):

```bash
./kclone --db my.db node-add node-a --cpu 4 --mem 4096
./kclone pod-create nginx-1 --image nginx:latest --cpu 1 --mem 128
./kclone deploy-create web --image nginx:latest --replicas 3
./kclone services
./kclone state-save state.json
```

---

Python CLI (`kclone` via `python -m kclone`)

Global options:

- `--db <path>` — path to SQLite DB (load/save state)
- `--up` — show animated banner

Commands:

- `node-add NAME` — add node
	- Options: `--cpu`, `--mem`, `--labels`

- `nodes` — list nodes

- `pod-create NAME` — create pod
	- Options: `--image` (required), `--cpu`, `--mem`, `--labels`

- `pods` — list pods

- `pod-delete UID` — delete pod by UID

- `deploy-create NAME` — create deployment
	- Options: `--image` (required), `--replicas`, `--selector`, `--labels`, `--cpu`, `--mem`

- `deploy-scale NAME --replicas N` — scale deployment

- `service-create NAME` — create service (`--selector`, `--port`, `--target-port`)

- `services` — list services

- `service-route NAME` — route a request through the named service

- `status` — show cluster capacity (tabulated)

- `state-save PATH` / `state-load PATH` — save/load JSON state

- `control-loop DB_PATH` — (Python-only) run a small control loop that reconciles deployments and schedules pods using SQLite as source-of-truth. Useful for background testing and simulated controllers.

Examples (Python):

```bash
python -m kclone --db my.db node-add node-a --cpu 4 --mem 4096
python -m kclone pod-create nginx --image nginx:latest --cpu 1 --mem 128
python -m kclone deploy-create web --image nginx:latest --replicas 3
python -m kclone service-create web --selector app=web --port 80
python -m kclone state-save state.json
python -m kclone control-loop my.db --interval 2
```

## Makefile Targets

Use `make help` to see available targets. Common targets:

- `make build-go` — build the Go `kclone` binary (placed in repo root)
- `make run-demo-go` — run Go demo (interactive demo that exercises features)
- `make install-python` — install Python package in editable mode
- `make run-demo-python` — run the Python demo
- `make test` — run both Go and Python tests
- `make clean` — remove built artifacts

## Testing & Development

Python tests are under `python/tests` and can be run with `pytest`:

```bash
cd python
pytest -v
```

Go package tests (if present) can be executed with:

```bash
cd go
go test ./...
```

For rapid development, the Makefile provides helpers to build and run demos.

## Contributing

If you want to extend or fix things:

1. Fork the repository and create a feature branch.
2. Run the relevant tests (Python `pytest`, Go `go test`).
3. Open a pull request with a clear description and tests where applicable.

## License & Notes

This repository is intended for educational use. See individual package READMEs in `go/` and `python/` for implementation details.
