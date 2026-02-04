K-Clone CLI Reference Sheet

**Database path used:**
`C:\Users\Kimat\Documents\Projects\Kubernetes-Clone\state.db`

---

Activate Python Virtual Environment

```powershell
cd C:\Users\Kimat\Documents\Projects\Kubernetes-Clone\python
. .\.venv\Scripts\Activate.ps1
```

*(The dot + space before the path is required in PowerShell.)*

---

Nodes Commands

**Add a node:**

```powershell
python -m kclone --db "C:\Users\Kimat\Documents\Projects\Kubernetes-Clone\state.db" node-add mynode --cpu 4 --mem 4096 --labels region=us,env=dev
```

*Adds a node with 4 CPUs, 4096 MB memory, and labels `region=us, env=dev`.*

**List all nodes:**

```powershell
python -m kclone --db "C:\Users\Kimat\Documents\Projects\Kubernetes-Clone\state.db" nodes
```

*Displays all nodes in the cluster, their resources, labels, and status.*

---

Pods Commands

**Create a pod:**

```powershell
python -m kclone --db "C:\Users\Kimat\Documents\Projects\Kubernetes-Clone\state.db" pod-create mypod --image nginx:latest --cpu 1 --mem 128 --labels app=web,env=dev
```

*Creates a pod named `mypod` with 1 CPU, 128 MB memory, `nginx:latest` image, and labels `app=web, env=dev`.*

**List all pods:**

```powershell
python -m kclone --db "C:\Users\Kimat\Documents\Projects\Kubernetes-Clone\state.db" pods
```

*Shows all pods, their UID, status, assigned node, and resource usage.*

**Delete a single pod by UID:**

```powershell
python -m kclone --db "C:\Users\Kimat\Documents\Projects\Kubernetes-Clone\state.db" pod-delete <UID>
```

*Deletes the pod with the specified UID.*

**Delete all pods (direct via SQLite):**

```powershell
sqlite3 "C:\Users\Kimat\Documents\Projects\Kubernetes-Clone\state.db" "DELETE FROM pods;"
```

*Removes all pods from the cluster.*

---

Services Commands

**Create a service:**

```powershell
python -m kclone --db "C:\Users\Kimat\Documents\Projects\Kubernetes-Clone\state.db" service-create myservice --selector app=web --port 80 --target-port 8080
```

*Creates a service targeting pods labeled `app=web`, exposing port 80 and forwarding to target port 8080.*

**List all services:**

```powershell
python -m kclone --db "C:\Users\Kimat\Documents\Projects\Kubernetes-Clone\state.db" services
```

*Displays all services, their selectors, ports, and linked pods.*

---

Go Project Commands

**Build your Go project:**

```powershell
cd C:\Users\Kimat\Documents\Projects\Kubernetes-Clone\go
go build -o ../kclone.exe ./cmd/kclone
```

*Creates the `kclone.exe` executable in your project root.*

**Run Go demo:**

```powershell
cd C:\Users\Kimat\Documents\Projects\Kubernetes-Clone\go
go run ./cmd/demo
```

*Runs the demo using the Go implementation.*
