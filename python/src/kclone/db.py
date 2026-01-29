from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Dict, Any

from .models import Node, Pod, PodSpec, Service, Deployment, HealthCheck, PodStatus
from .state import ClusterState


SCHEMA = '''
CREATE TABLE IF NOT EXISTS nodes (
  id TEXT PRIMARY KEY,
  ip_address TEXT,
  total_cpu INTEGER,
  total_ram INTEGER,
  status TEXT,
  labels TEXT
);

CREATE TABLE IF NOT EXISTS pods (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  uid TEXT UNIQUE,
  name TEXT,
  namespace TEXT DEFAULT 'default',
  node_id TEXT,
  image TEXT,
  desired_status TEXT,
  current_status TEXT,
  cpu_request INTEGER,
  mem_request INTEGER,
  labels TEXT
);

CREATE TABLE IF NOT EXISTS services (
  name TEXT PRIMARY KEY,
  cluster_ip TEXT,
  selector TEXT,
  port INTEGER,
  target_port INTEGER
);

CREATE TABLE IF NOT EXISTS replica_sets (
  name TEXT PRIMARY KEY,
  selector TEXT,
  replicas_count INTEGER,
  pod_template TEXT
);
'''


def init_db(path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    try:
        conn.executescript(SCHEMA)
        conn.commit()
    finally:
        conn.close()


def load_state_from_db(path: str | Path) -> ClusterState:
    init_db(path)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    state = ClusterState()
    try:
        cur = conn.cursor()
        for r in cur.execute('SELECT * FROM nodes'):
            labels = json.loads(r['labels']) if r['labels'] else {}
            node = Node(name=r['id'], cpu_capacity=r['total_cpu'], mem_capacity=r['total_ram'], labels=labels, ready=(r['status']=='Ready'))
            state.add_node(node)

        for r in cur.execute('SELECT * FROM pods'):
            labels = json.loads(r['labels']) if r['labels'] else {}
            hc = HealthCheck()
            spec = PodSpec(name=r['name'], image=r['image'], cpu_request=r['cpu_request'] or 1, mem_request=r['mem_request'] or 128, labels=labels, health_check=hc)
            status = PodStatus(phase=r['current_status'] or 'Pending', node_name=r['node_id'])
            uid = r['uid'] or f"dbpod-{r['id']}"
            pod = Pod(name=r['name'], spec=spec, status=status, uid=uid)
            # don't auto-start subprocesses here; ClusterState will handle scheduling
            state.pods[uid] = pod

        for r in cur.execute('SELECT * FROM services'):
            selector = json.loads(r['selector']) if r['selector'] else {}
            svc = Service(name=r['name'], selector=selector, port=r['port'], target_port=r['target_port'], virtual_ip=r['cluster_ip'])
            state.services[svc.name] = svc

        for r in cur.execute('SELECT * FROM replica_sets'):
            selector = json.loads(r['selector']) if r['selector'] else {}
            tpl = json.loads(r['pod_template']) if r['pod_template'] else {}
            deploy = Deployment(name=r['name'], image=tpl.get('image', ''), replicas=r['replicas_count'], selector=selector, labels=tpl.get('labels', {}), cpu_request=tpl.get('cpu_request', 1), mem_request=tpl.get('mem_request', 128))
            state.deployments[deploy.name] = deploy

    finally:
        conn.close()
    return state


def save_state_to_db(state: ClusterState, path: str | Path) -> None:
    init_db(path)
    conn = sqlite3.connect(path)
    try:
        cur = conn.cursor()
        # replace nodes
        cur.execute('DELETE FROM nodes')
        for n in state.list_nodes():
            cur.execute('INSERT INTO nodes(id, ip_address, total_cpu, total_ram, status, labels) VALUES (?,?,?,?,?,?)', (n.name, None, n.cpu_capacity, n.mem_capacity, 'Ready' if n.ready else 'NotReady', json.dumps(n.labels)))

        # replace pods
        cur.execute('DELETE FROM pods')
        for p in state.list_pods():
            cur.execute('INSERT INTO pods(uid, name, namespace, node_id, image, desired_status, current_status, cpu_request, mem_request, labels) VALUES (?,?,?,?,?,?,?,?,?,?)', (p.uid, p.name, 'default', p.status.node_name, p.spec.image, 'Running' if p.status.phase=='Running' else 'Terminated', p.status.phase, p.spec.cpu_request, p.spec.mem_request, json.dumps(p.spec.labels)))

        # replace services
        cur.execute('DELETE FROM services')
        for s in state.services.values():
            cur.execute('INSERT INTO services(name, cluster_ip, selector, port, target_port) VALUES (?,?,?,?,?)', (s.name, s.virtual_ip, json.dumps(s.selector), s.port, s.target_port))

        # replace replica_sets
        cur.execute('DELETE FROM replica_sets')
        for d in state.deployments.values():
            tpl = {'image': d.image, 'labels': d.labels, 'cpu_request': d.cpu_request, 'mem_request': d.mem_request}
            cur.execute('INSERT INTO replica_sets(name, selector, replicas_count, pod_template) VALUES (?,?,?,?)', (d.name, json.dumps(d.selector), d.replicas, json.dumps(tpl)))

        conn.commit()
    finally:
        conn.close()


def control_loop(db_path: str | Path, loop_interval: int = 1) -> None:
    """Start the control loop that loads state from DB, reconciles deployments,
    schedules pods and persists back to DB on each iteration.
    """
    from time import sleep
    while True:
        control_loop_iteration(db_path)
        sleep(loop_interval)


def control_loop_iteration(db_path: str | Path) -> ClusterState:
    """Perform a single control-loop iteration: load state, reconcile deployments,
    schedule pods, persist state, and return the in-memory ClusterState.
    This is useful for testing and one-shot runs.
    """
    state = load_state_from_db(db_path)
    # reconcile deployments (controllers will create desired pods)
    try:
        from .controllers import reconcile_deployments

        reconcile_deployments(state)
    except Exception:
        pass
    # persist new state back to DB
    save_state_to_db(state, db_path)
    return state
