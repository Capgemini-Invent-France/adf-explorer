import json
import tempfile
from pathlib import Path

import typer

from adf import Activity, Node

app = typer.Typer()


def load_all(root):
    if root is None:
        typer.echo("The root parameter is mandatory")
        raise typer.Exit(code=1)
    if not root.exists():
        typer.echo("The root parameter does not exist")
        raise typer.Exit(code=1)
    for p in (root / "pipeline").glob("*.json"):
        Activity.load(p)
    Node.resolve_all()


@app.command("draw")
def draw(
    dot: Path = None,
    root: Path = typer.Option(None, envvar="ADF_ROOT"),
):
    load_all(root)

    if dot is not None:
        g = Node.draw_all(dot)
        g.view()
    else:
        dirname = tempfile.mkdtemp(prefix="adf")
        dot = Path(dirname) / "pipeline.dot"
        g = Node.draw_all(dot)
        g.view()


@app.command("list")
def list(
    pattern: str = typer.Argument(None),
    root: Path = typer.Option(None, envvar="ADF_ROOT"),
):
    load_all(root)

    if pattern is not None:
        pattern = pattern.lower()

    def gen():
        for node in Node.filter():
            if pattern is None or pattern in json.dumps(node.export()).lower():
                yield node

    for node in gen():
        print(f"{node.file}|{node.type}|{node.name}")


@app.command("find")
def find(
    type: str = None,
    name: str = None,
    root: Path = typer.Option(None, envvar="ADF_ROOT"),
):
    load_all(root)

    def fil(node):
        if name and (name.lower() not in node.name.lower()):
            return False
        if type and (type.lower() not in node.type.lower()):
            return False
        return True

    print(json.dumps(Node.export_all(fil), indent=True))


def main():
    app()
