from pathlib import Path

from kclone.db import init_db, load_state_from_db, save_state_to_db, control_loop_iteration
from kclone.models import Node
from kclone.controllers import create_deployment


def test_db_load_save(tmp_path):
    db = tmp_path / "cluster.db"
    init_db(db)
    state = load_state_from_db(db)
    state.add_node(Node(name="n1", cpu_capacity=2, mem_capacity=512))
    save_state_to_db(state, db)

    loaded = load_state_from_db(db)
    assert "n1" in [n.name for n in loaded.list_nodes()]


def test_control_loop_iteration_creates_pods(tmp_path):
    db = tmp_path / "cluster.db"
    init_db(db)
    state = load_state_from_db(db)
    state.add_node(Node(name="node-a", cpu_capacity=4, mem_capacity=2048))
    # create a replica set via deployments table
    create_deployment(state, "app", "nginx", replicas=2, selector={"app": "app"}, labels={"app": "app"}, cpu_request=1, mem_request=128)
    save_state_to_db(state, db)

    new_state = control_loop_iteration(db)
    pods = [p for p in new_state.list_pods() if p.spec.labels.get("app") == "app"]
    assert len(pods) == 2
