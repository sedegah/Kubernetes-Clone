from kclone.controllers import create_deployment, reconcile_deployments
from kclone.lifecycle import create_pod
from kclone.models import Node
from kclone.persistence import load_state, save_state
from kclone.scheduler import schedule_pending_pods
from kclone.service import create_service, route_request
from kclone.state import ClusterState


def test_scheduler_places_pod():
    state = ClusterState()
    state.add_node(Node(name="node-a", cpu_capacity=2, mem_capacity=1024))
    pod = create_pod(state, "p1", "nginx", 1, 128, labels={"app": "web"})
    assert pod.status.phase == "Running"
    assert pod.status.node_name == "node-a"


def test_service_round_robin():
    state = ClusterState()
    state.add_node(Node(name="node-a", cpu_capacity=4, mem_capacity=2048))
    create_pod(state, "p1", "nginx", 1, 128, labels={"app": "web"})
    create_pod(state, "p2", "nginx", 1, 128, labels={"app": "web"})
    create_service(state, "web", selector={"app": "web"}, port=80, target_port=80)
    first = route_request(state, "web")
    second = route_request(state, "web")
    assert first != second
    assert set([first, second]) == set(state.services["web"].endpoints)


def test_deployment_reconcile_and_scale():
    state = ClusterState()
    state.add_node(Node(name="node-a", cpu_capacity=4, mem_capacity=4096))
    create_deployment(state, "api", "nginx", replicas=2, selector={"app": "api"}, labels={"app": "api"}, cpu_request=1, mem_request=128)
    reconcile_deployments(state)
    assert len(state.select_pods({"app": "api"})) == 2
    state.deployments["api"].replicas = 1
    reconcile_deployments(state)
    assert len(state.select_pods({"app": "api"})) == 1


def test_state_persistence(tmp_path):
    state = ClusterState()
    state.add_node(Node(name="node-a", cpu_capacity=2, mem_capacity=1024))
    create_pod(state, "p1", "nginx", 1, 128, labels={"app": "web"})
    create_service(state, "web", selector={"app": "web"}, port=80, target_port=80)
    save_path = tmp_path / "state.json"
    save_state(state, save_path)

    loaded = load_state(save_path)
    assert loaded.nodes.keys() == state.nodes.keys()
    assert loaded.services["web"].virtual_ip == state.services["web"].virtual_ip
    assert loaded.pods.keys() == state.pods.keys()
    # After load, scheduling decisions remain intact
    for uid, pod in loaded.pods.items():
        assert pod.status.phase == state.pods[uid].status.phase
        assert pod.status.node_name == state.pods[uid].status.node_name
