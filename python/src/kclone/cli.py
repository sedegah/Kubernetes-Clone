from __future__ import annotations

import click
from tabulate import tabulate

from .controllers import create_deployment, reconcile_deployments
from .lifecycle import create_pod, delete_pod
from .models import Node
from .persistence import load_state, save_state
from .resource import cluster_capacity, node_resource_table
from .scheduler import schedule_pending_pods
from .service import create_service, route_request
from .state import ClusterState

state = ClusterState()


def parse_labels(label_str: str | None) -> dict:
    if not label_str:
        return {}
    labels = {}
    for pair in label_str.split(","):
        if not pair:
            continue
        if "=" not in pair:
            raise click.BadParameter("Labels must be key=value")
        k, v = pair.split("=", 1)
        labels[k.strip()] = v.strip()
    return labels


@click.group()
def cli() -> None:
    """Simplified Kubernetes-style cluster manager."""


@cli.command("node-add")
@click.argument("name")
@click.option("--cpu", default=4, show_default=True, help="CPU capacity")
@click.option("--mem", default=4096, show_default=True, help="Memory capacity in MB")
@click.option("--labels", default=None, help="Comma-separated key=value labels")
def node_add(name: str, cpu: int, mem: int, labels: str | None) -> None:
    node = Node(name=name, cpu_capacity=cpu, mem_capacity=mem, labels=parse_labels(labels))
    state.add_node(node)
    click.echo(f"Added node {name}")
    schedule_pending_pods(state)


@cli.command("nodes")
def list_nodes() -> None:
    rows = node_resource_table(state)
    if not rows:
        click.echo("No nodes present")
        return
    click.echo(tabulate(rows, headers="keys"))


@cli.command("pod-create")
@click.argument("name")
@click.option("--image", required=True, help="Container image")
@click.option("--cpu", default=1, show_default=True, help="CPU request")
@click.option("--mem", default=128, show_default=True, help="Memory request in MB")
@click.option("--labels", default=None, help="Comma-separated key=value labels")
def pod_create(name: str, image: str, cpu: int, mem: int, labels: str | None) -> None:
    pod = create_pod(state, name, image, cpu, mem, parse_labels(labels))
    click.echo(f"Created pod {pod.uid} -> {pod.status.phase}")


@cli.command("pods")
def list_pods() -> None:
    if not state.pods:
        click.echo("No pods present")
        return
    rows = []
    for pod in state.pods.values():
        rows.append(
            {
                "uid": pod.uid,
                "name": pod.name,
                "image": pod.spec.image,
                "phase": pod.status.phase,
                "node": pod.status.node_name or "",
                "cpu": pod.spec.cpu_request,
                "mem": pod.spec.mem_request,
                "labels": ",".join(f"{k}={v}" for k, v in pod.spec.labels.items()),
            }
        )
    click.echo(tabulate(rows, headers="keys"))


@cli.command("pod-delete")
@click.argument("uid")
def pod_delete(uid: str) -> None:
    delete_pod(state, uid)
    click.echo(f"Deleted pod {uid}")


@cli.command("deploy-create")
@click.argument("name")
@click.option("--image", required=True)
@click.option("--replicas", default=1, show_default=True)
@click.option("--selector", default=None, help="Selector labels (key=value,...)")
@click.option("--labels", default=None, help="Pod template labels (key=value,...)")
@click.option("--cpu", default=1, show_default=True, help="CPU request per pod")
@click.option("--mem", default=128, show_default=True, help="Memory request per pod in MB")
def deploy_create(name: str, image: str, replicas: int, selector: str | None, labels: str | None, cpu: int, mem: int) -> None:
    sel = parse_labels(selector) or {"app": name}
    lbls = parse_labels(labels) or {"app": name}
    create_deployment(state, name, image, replicas, sel, lbls, cpu, mem)
    reconcile_deployments(state)
    click.echo(f"Created deployment {name} with {replicas} replicas")


@cli.command("deploy-scale")
@click.argument("name")
@click.option("--replicas", required=True, type=int)
def deploy_scale(name: str, replicas: int) -> None:
    deploy = state.deployments.get(name)
    if not deploy:
        raise click.BadParameter(f"Deployment {name} not found")
    deploy.replicas = replicas
    reconcile_deployments(state)
    click.echo(f"Scaled {name} to {replicas} replicas")


@cli.command("services")
def list_services() -> None:
    if not state.services:
        click.echo("No services present")
        return
    rows = []
    for svc in state.services.values():
        rows.append(
            {
                "name": svc.name,
                "vip": svc.virtual_ip,
                "port": svc.port,
                "targets": ",".join(svc.endpoints),
                "selector": ",".join(f"{k}={v}" for k, v in svc.selector.items()),
            }
        )
    click.echo(tabulate(rows, headers="keys"))


@cli.command("service-create")
@click.argument("name")
@click.option("--selector", default=None, help="Selector labels (key=value,...)" )
@click.option("--port", default=80, show_default=True, type=int)
@click.option("--target-port", default=80, show_default=True, type=int)
def service_create(name: str, selector: str | None, port: int, target_port: int) -> None:
    sel = parse_labels(selector) or {"app": name}
    svc = create_service(state, name, sel, port, target_port)
    click.echo(f"Created service {name} with VIP {svc.virtual_ip}")


@cli.command("service-route")
@click.argument("name")
def service_route(name: str) -> None:
    pod_uid = route_request(state, name)
    click.echo(f"Service {name} routed to pod {pod_uid}")


@cli.command("status")
def cluster_status() -> None:
    caps = cluster_capacity(state)
    click.echo(tabulate([caps], headers="keys"))


@cli.command("state-save")
@click.argument("path")
def state_save_cmd(path: str) -> None:
    save_state(state, path)
    click.echo(f"Saved state to {path}")


@cli.command("state-load")
@click.argument("path")
def state_load_cmd(path: str) -> None:
    global state
    state = load_state(path)
    click.echo(f"Loaded state from {path}")


def main() -> None:
    cli()


if __name__ == "__main__":
    main()
