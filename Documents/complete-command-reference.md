# K-Clone Complete Command Reference

## Quick Start Setup

### Go Implementation
```powershell
# Set up environment (run once per session)
$env:PATH="C:\Program Files\Go\bin;C:\msys64\mingw64\bin;" + $env:PATH
$env:CGO_ENABLED="1"

# Build the Go CLI
cd go
go build -o ../kclone.exe ./cmd/kclone

# Return to project root
cd ..
```

### Python Implementation
```powershell
# Activate virtual environment
cd python
. .\.venv\Scripts\Activate.ps1

# Install in development mode
pip install -e .

# Return to project root
cd ..
```

---

## Node Management

### Go Commands
```powershell
# Add a node
.\kclone.exe node-add <node-name> --cpu <cores> --mem <MB> --labels <key=value,key=value>

# Examples
.\kclone.exe node-add worker-1 --cpu 4 --mem 4096
.\kclone.exe node-add worker-2 --cpu 8 --mem 8192 --labels region=us-east,zone=1a

# List all nodes
.\kclone.exe nodes

# Remove a node
.\kclone.exe remove-node <node-name>
```

### Python Commands
```powershell
# Add a node
python -m kclone node-add <node-name> --cpu <cores> --mem <MB> --labels <key=value,key=value>

# Examples
python -m kclone node-add worker-1 --cpu 4 --mem 4096
python -m kclone node-add worker-2 --cpu 8 --mem 8192 --labels region=us-east,zone=1a

# List all nodes
python -m kclone nodes

# Remove a node (Python doesn't have remove-node command yet)
```

---

## Pod Management

### Go Commands
```powershell
# Create a pod
.\kclone.exe pod-create <pod-name> --image <image> --cpu <cores> --mem <MB> --labels <key=value,key=value>

# Examples
.\kclone.exe pod-create nginx-1 --image nginx:latest --cpu 1 --mem 128
.\kclone.exe pod-create web-app --image nginx:1.21 --cpu 2 --mem 256 --labels app=web,env=prod

# List all pods
.\kclone.exe pods

# Delete a pod by UID
.\kclone.exe pod-delete <pod-uid>
```

### Python Commands
```powershell
# Create a pod
python -m kclone pod-create <pod-name> --image <image> --cpu <cores> --mem <MB> --labels <key=value,key=value>

# Examples
python -m kclone pod-create nginx-1 --image nginx:latest --cpu 1 --mem 128
python -m kclone pod-create web-app --image nginx:1.21 --cpu 2 --mem 256 --labels app=web,env=prod

# List all pods
python -m kclone pods

# Delete a pod by UID
python -m kclone pod-delete <pod-uid>
```

---

## Deployment Management

### Go Commands
```powershell
# Create a deployment
.\kclone.exe deploy-create <deploy-name> --image <image> --replicas <count> --selector <key=value> --labels <key=value> --cpu <cores> --mem <MB>

# Examples
.\kclone.exe deploy-create web-servers --image nginx:latest --replicas 3 --selector app=web
.\kclone.exe deploy-create api-backend --image python:3.9 --replicas 2 --selector app=api --labels tier=backend

# Scale a deployment
.\kclone.exe deploy-scale <deploy-name> --replicas <new-count>

# Example
.\kclone.exe deploy-scale web-servers --replicas 5
```

### Python Commands
```powershell
# Create a deployment
python -m kclone deploy-create <deploy-name> --image <image> --replicas <count> --selector <key=value> --labels <key=value> --cpu <cores> --mem <MB>

# Examples
python -m kclone deploy-create web-servers --image nginx:latest --replicas 3 --selector app=web
python -m kclone deploy-create api-backend --image python:3.9 --replicas 2 --selector app=api --labels tier=backend

# Scale a deployment
python -m kclone deploy-scale <deploy-name> --replicas <new-count>

# Example
python -m kclone deploy-scale web-servers --replicas 5
```

---

## Service Management

### Go Commands
```powershell
# Create a service
.\kclone.exe service-create <service-name> --selector <key=value> --port <external-port> --target-port <container-port>

# Examples
.\kclone.exe service-create web-service --selector app=web --port 80 --target-port 8080
.\kclone.exe service-create api-service --selector app=api --port 443 --target-port 8443

# List all services
.\kclone.exe services

# Route a request through a service (for testing)
.\kclone.exe service-route <service-name>
```

### Python Commands
```powershell
# Create a service
python -m kclone service-create <service-name> --selector <key=value> --port <external-port> --target-port <container-port>

# Examples
python -m kclone service-create web-service --selector app=web --port 80 --target-port 8080
python -m kclone service-create api-service --selector app=api --port 443 --target-port 8443

# List all services
python -m kclone services

# Route a request through a service (for testing)
python -m kclone service-route <service-name>
```

---

## Database Persistence

### Go Commands
```powershell
# Use specific database file
.\kclone.exe --db <database-file.db> <command>

# Examples with database
.\kclone.exe --db production.db node-add prod-node --cpu 8 --mem 8192
.\kclone.exe --db production.db pod-create app-1 --image nginx:latest --cpu 2 --mem 256

# Save state to file
.\kclone.exe state-save <filename.json>

# Load state from file
.\kclone.exe state-load <filename.json>
```

### Python Commands
```powershell
# Use specific database file
python -m kclone --db <database-file.db> <command>

# Examples with database
python -m kclone --db production.db node-add prod-node --cpu 8 --mem 8192
python -m kclone --db production.db pod-create app-1 --image nginx:latest --cpu 2 --mem 256

# Save state to file
python -m kclone state-save <filename.json>

# Load state from file
python -m kclone state-load <filename.json>

# Run control loop (Python only)
python -m kclone control-loop <database-file.db> --interval <seconds>
```

---

## Cluster Status and Monitoring

### Go Commands
```powershell
# Show cluster resource status
.\kclone.exe status

# Show animated banner
.\kclone.exe up
# or
.\kclone.exe --up
```

### Python Commands
```powershell
# Show cluster resource status
python -m kclone status

# Show animated banner
python -m kclone up
# or
python -m kclone --up
```

---

## Complete Workflow Examples

### Example 1: Web Application Deployment
```powershell
# Go Implementation
.\kclone.exe --db webapp.db node-add web-node-1 --cpu 4 --mem 4096 --labels tier=web
.\kclone.exe --db webapp.db node-add web-node-2 --cpu 4 --mem 4096 --labels tier=web
.\kclone.exe --db webapp.db deploy-create frontend --image nginx:latest --replicas 4 --selector app=frontend --labels tier=web
.\kclone.exe --db webapp.db service-create frontend-svc --selector app=frontend --port 80 --target-port 80
.\kclone.exe --db webapp.db status
```

```powershell
# Python Implementation
python -m kclone --db webapp.db node-add web-node-1 --cpu 4 --mem 4096 --labels tier=web
python -m kclone --db webapp.db node-add web-node-2 --cpu 4 --mem 4096 --labels tier=web
python -m kclone --db webapp.db deploy-create frontend --image nginx:latest --replicas 4 --selector app=frontend --labels tier=web
python -m kclone --db webapp.db service-create frontend-svc --selector app=frontend --port 80 --target-port 80
python -m kclone --db webapp.db status
```

### Example 2: Multi-Tier Application
```powershell
# Go Implementation
.\kclone.exe --db multilayer.db node-add db-node --cpu 8 --mem 8192 --labels tier=database
.\kclone.exe --db multilayer.db node-add app-node-1 --cpu 4 --mem 4096 --labels tier=application
.\kclone.exe --db multilayer.db node-add app-node-2 --cpu 4 --mem 4096 --labels tier=application
.\kclone.exe --db multilayer.db deploy-create database --image postgres:13 --replicas 1 --selector app=db --labels tier=database
.\kclone.exe --db multilayer.db deploy-create backend --image python:3.9 --replicas 3 --selector app=backend --labels tier=application
.\kclone.exe --db multilayer.db service-create db-service --selector app=db --port 5432 --target-port 5432
.\kclone.exe --db multilayer.db service-create api-service --selector app=backend --port 8080 --target-port 8000
```

```powershell
# Python Implementation
python -m kclone --db multilayer.db node-add db-node --cpu 8 --mem 8192 --labels tier=database
python -m kclone --db multilayer.db node-add app-node-1 --cpu 4 --mem 4096 --labels tier=application
python -m kclone --db multilayer.db node-add app-node-2 --cpu 4 --mem 4096 --labels tier=application
python -m kclone --db multilayer.db deploy-create database --image postgres:13 --replicas 1 --selector app=db --labels tier=database
python -m kclone --db multilayer.db deploy-create backend --image python:3.9 --replicas 3 --selector app=backend --labels tier=application
python -m kclone --db multilayer.db service-create db-service --selector app=db --port 5432 --target-port 5432
python -m kclone --db multilayer.db service-create api-service --selector app=backend --port 8080 --target-port 8000
```

---

## Testing and Development

### Go Testing
```powershell
cd go
go test ./...
cd ..
```

### Python Testing
```powershell
cd python
pytest -v
cd ..
```

### Demo Applications
```powershell
# Go Demo
cd go
go run ./cmd/demo
cd ..

# Python Demo
make run-demo-python
# or
cd python
python -m kclone --up
```

---

## Environment Variables

### Go Required Variables
```powershell
$env:PATH="C:\Program Files\Go\bin;C:\msys64\mingw64\bin;" + $env:PATH
$env:CGO_ENABLED="1"
```

### Python Variables
```powershell
# Virtual environment activation
cd python
. .\.venv\Scripts\Activate.ps1
```

---

## Troubleshooting

### Common Issues
1. **CGO errors**: Ensure MinGW is in PATH and CGO_ENABLED=1
2. **Database errors**: Check file permissions and disk space
3. **Port conflicts**: Services use virtual IPs, not real ports
4. **Resource limits**: Check node capacity before creating pods

### Debug Commands
```powershell
# Check Go environment
go env GOARCH GOOS CGO_ENABLED

# Check Python environment
python --version
pip list | grep kclone

# Test database connectivity
.\kclone.exe --db test.db status
python -m kclone --db test.db status
```

---

## File Locations

### Go Binary
- `kclone.exe` (project root)

### Python Package
- `python/src/kclone/`
- Virtual environment: `python/.venv/`

### Database Files
- Default Go: `golang_cluster.db`
- Default Python: `state.db`
- Custom: Any `.db` file with `--db` flag

### State Files
- JSON exports: Any `.json` file with `state-save` command
