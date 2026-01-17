# Kubernetes-Clone

Simplified, in-memory Kubernetes-style orchestrator with implementations in both Python and Go for educational purposes.

## Project Overview

This project implements core Kubernetes concepts including:
- **Pod scheduling** with resource-aware bin-packing placement
- **Service abstraction** with virtual IPs and round-robin load balancing  
- **Replica management** via deployment controllers
- **Resource tracking** at node and cluster level
- **CLI tools** for cluster management

## Repository Structure

```
Kubernetes-Clone/
├── python/          # Python implementation
│   ├── src/         # Source code
│   ├── tests/       # Test suite
│   └── README.md    # Python-specific docs
├── go/              # Go implementation  
│   ├── cmd/         # CLI and demo apps
│   ├── pkg/         # Core packages
│   └── README.md    # Go-specific docs
└── README.md        # This file
```

## Quick Start

### Python Implementation
```bash
cd python
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
PYTHONPATH=src python -m kclone --help
```

### Go Implementation  
```bash
cd go
go run ./cmd/demo  # Run full demo
# OR
go run ./cmd/kclone --help  # CLI commands
```

## Common Workflows

### Python
### Python
```bash
cd python
PYTHONPATH=src python -m kclone node-add node-a --cpu 4 --mem 4096
PYTHONPATH=src python -m kclone deploy-create web --image nginx:latest --replicas 3 --labels app=web
PYTHONPATH=src python -m kclone service-create web --selector app=web --port 80
PYTHONPATH=src python -m kclone status
PYTHONPATH=src python -m kclone state-save state.json  # Persist state
```

### Go
```bash
cd go
go run ./cmd/demo  # Complete orchestration demo with persistent state
```

## Testing

### Python Tests
```bash
cd python
pytest
```

### Go Demo
```bash
cd go
go run ./cmd/demo
```

## Features Comparison

| Feature | Python | Go |
|---------|--------|-----|
| Pod Scheduling | ✓ | ✓ |
| Service Networking | ✓ | ✓ |
| Replica Management | ✓ | ✓ |
| Resource Tracking | ✓ | ✓ |
| CLI Interface | Click | Cobra |
| Persistence | JSON file | In-memory |
| Test Suite | pytest | Demo app |
| Concurrency | Single-threaded | Thread-safe (sync.RWMutex) |

## Documentation

- [Python Implementation Details](python/README.md)
- [Go Implementation Details](go/README.md)

## Notes
- Both implementations use in-memory state by default
- Python CLI supports state persistence via JSON
- Go CLI runs stateless; use the demo app for persistent sessions
- Scheduling uses bin-packing to optimize resource utilization
