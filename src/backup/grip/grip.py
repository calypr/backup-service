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
import gripql
import orjson


@dataclass
class GripConfig:
    """GripConfig config"""

    host: str
    port: int


def _getEdges():
    pass


def _getVertices():
    pass


def _connect(grip: GripConfig) -> gripql.Connection:
    """
    Connects to a given grip instance.
    """
    # Create a grip client
    try:
        client = gripql.Connection(url="http://localhost:8201")
    except Exception as err:
        print(f"Error connecting to Grip: {err}")
        raise

    return client


def _dump(grip: GripConfig):
    # Dump

    conn = _connect(grip)

    conn.addGraph("NEWGRAPH")
    G = conn.graph("NEWGRAPH")

    print("dumping data")
    # write vertex and edge objects from grip DB to file
    with open("grip.vertices", "wb") as f:
        count = 0
        for i in G.query().V().limit(20000):
            f.write(orjson.dumps(i, option=orjson.OPT_APPEND_NEWLINE))
            count += 1
            if count % 10000 == 0:
                print("dumped %d vertices" % count)

    with open("grip.edges", "wb") as f:
        count = 0
        for i in G.query().E().limit(20000):
            f.write(orjson.dumps(i, option=orjson.OPT_APPEND_NEWLINE))
            count += 1
            if count % 10000 == 0:
                print("dumped %d edges" % count)

    # At this point you will need to reconnect to the new grip instance to load the data that was dumped


def _restore(grip: GripConfig):
    ## Load
    print("loading data")

    conn = _connect(grip)

    conn.addGraph("NEWGRAPH")
    G = conn.graph("NEWGRAPH")

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
