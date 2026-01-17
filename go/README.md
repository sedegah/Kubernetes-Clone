# kclone-go

Full Go implementation of the simplified Kubernetes clone with Cobra CLI.

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

## Common Commands
Note: Each CLI invocation starts fresh (in-memory state). For persistent sessions, use the demo or build a stateful server.

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

## Demo
Run `go run ./cmd/demo` to see a full orchestration flow with nodes, deployments, services, and routing.

