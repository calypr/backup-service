### Ex: extract data from one grip instance and load it into another grip instance:
#
# Method 1:
# If you have direct access to grip from within the cluster you can do something like this from command line
# You might be able to do this from another pod by specificing a --host and the proper address to the running grip instance
# 8201 for https and 8202 for grpc
#
# grip dump TEST --vertex > grip.vertices.json
# grip dump TEST --edge > grip.edges.json
#
# grip load TEST --vertex grip.vertices
# grip load TEST --edge grip.edges


## Method 2:
# You can always use the python client
# You will need to pip install gripql, orjson.
# pip install "git+https://github.com/bmeg/grip.git@feature/indexing#subdirectory=gripql/python"
# pip install orjson

from dataclasses import dataclass
from pathlib import Path
import gripql
import orjson


@dataclass
class GripConfig:
    """GripConfig config"""

    host: str
    port: int


def _getEdges(grip: GripConfig, graph: str, limit: int) -> list[str]:
    """
    Utility function to connect to Grip and list all edges.
    """

    # Connect to Grip
    c = _connect(grip)

    # List Edges
    edges = []

    G = c.graph(graph)

    for i in G.query().E().limit(limit):
        edges.append(i)

    return edges


def _getVertices(grip: GripConfig, graph: str, limit: int) -> list[str]:
    """
    Utility function to connect to Grip and list all vertices.
    """
    c = _connect(grip)

    # List Vertices
    vertices = []

    G = c.graph(graph)

    for i in G.query().V().limit(limit):
        vertices.append(i)

    return vertices


def _connect(grip: GripConfig) -> gripql.Connection:
    """
    Connects to a given grip instance.
    """

    # Create a grip client
    try:
        client = gripql.Connection(url=f"http://{grip.host}:{grip.port}")
    except Exception as err:
        print(f"Error connecting to Grip: {err}")
        raise

    return client


def _dump(grip: GripConfig, graph: str, limit: int, vertex: bool, edge: bool, out: Path) -> None:
    # Dump
    conn = _connect(grip)
    G = conn.graph(graph)

    # write vertex and edge objects from grip DB to file
    if vertex:
        with open(out / "grip.vertices", "wb") as f:
            for i in G.query().V().limit(limit):
                f.write(orjson.dumps(i, option=orjson.OPT_APPEND_NEWLINE))

    if edge:
        with open(out / "grip.edges", "wb") as f:
            for i in G.query().E().limit(limit):
                f.write(orjson.dumps(i, option=orjson.OPT_APPEND_NEWLINE))

    # TODO: At this point you will need to reconnect to the new grip instance to load the data that was dumped


def _restore(grip: GripConfig, graph: str, dir: Path):
    ## Load
    conn = _connect(grip)
    G = conn.graph(graph)

    bulkV = G.bulkAdd()
    with open("grip.vertices", "rb") as f:
        count = 0
        for i in f:
            data = orjson.loads(i)
            _id = data["_id"]
            _label = data["_label"]
            del data["_id"], data["_label"]
            bulkV.addVertex(_id, _label, data)
            count += 1
            if count % 10000 == 0:
                print("loaded %d vertices" % count)
    err = bulkV.execute()
    print("Vertices load res: ", str(err))

    bulkE = G.bulkAdd()
    with open("grip.edges", "rb") as f:
        count = 0
        for i in f:
            data = orjson.loads(i)
            _id = data["_id"]
            _label = data["_label"]
            _to = data["_to"]
            _from = data["_from"]
            del data["_id"], data["_label"], data["_to"], data["_from"]
            bulkE.addEdge(_to, _from, _label, data=data, gid=_id)
            count += 1
            if count % 10000 == 0:
                print("loaded %d edges" % count)
    err = bulkE.execute()
    print("Edges load res: ", str(err))
