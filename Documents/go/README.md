````markdown
# Go Implementation

See [../README.md](../README.md) for full project documentation.

## Quick Start
```bash
# Build
go build -o kclone ./cmd/kclone

# Run help
./kclone --help

# Run demo
go run ./cmd/demo
```

## Features
- Pod scheduling with bin-packing algorithm
- Service abstraction with round-robin load balancing
- Deployment replica management
- Resource tracking per node and cluster-wide
- Cobra-based CLI for cluster management

## Build & Run
- Build: `cd go && go build -o kclone ./cmd/kclone`
- Run CLI: `./kclone --help`
- Demo: `go run ./cmd/demo`

## Example Usage
```bash
# Each command runs independently (stateless)
go run ./cmd/kclone node-add node-a --cpu 4 --mem 4096
go run ./cmd/kclone deploy-create web --image nginx:latest --replicas 3
go run ./cmd/kclone service-create web --selector app=web --port 80
go run ./cmd/kclone status

# For persistent state demo, run:
go run ./cmd/demo
```



````
