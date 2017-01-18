#    BSD license.
from itertools import chain, count
import json
import networkx as nx

__all__ = ['cytoscape_data', 'cytoscape_graph']

_attrs = dict(source='source', target='target', name='name', id='id')

def cytoscape_data(G, attrs=None):
    """Return data in Cytoscape JSON format (cyjs).

    Parameters
    ----------
    G : NetworkX Graph


    Returns
    -------
    data: dict
        A dictionary with cyjs formatted data.
    Raises
    ------
    NetworkXError
        If values in attrs are not unique.
    """
    multigraph = G.is_multigraph()
    if not attrs:
        attrs = _attrs
    else:
        attrs.update({k: v for (k, v) in _attrs.items() if k not in attrs})

    name = attrs["name"]
    source = attrs["source"]
    target = attrs["target"]
    
    if len(set([source, target, name])) < 3:
        raise nx.NetworkXError('Attribute names are not unique.')
    
    jsondata = {"data" : list(G.graph.items())}
    jsondata['directed'] = G.is_directed()
    jsondata['multigraph'] = multigraph
    jsondata["elements"] = {"nodes" : [], "edges" : []}
    nodes = jsondata["elements"]["nodes"]
    edges = jsondata["elements"]["edges"]

    for i, j in G.node.items():
        n = {"data" : j.copy()}
        n["data"]["id"] = str(i)
        n["data"]["value"] = i
        n["data"]["name"] = j.get(name) or str(i)
        nodes.append(n)
        
    for e in G.edges():
        n = {"data" : G.edge[e[0]][e[1]].copy().copy()}
        n["data"]["source"] = n["data"].get(source) or e[0]
        n["data"]["target"] = n["data"].get(target) or e[1]
        edges.append(n)
    return jsondata


def cytoscape_graph(data, attrs=None):
    if not attrs:
        attrs = _attrs
    else:
        attrs.update({k: v for (k, v) in _attrs.items() if k not in attrs})
    
    name = attrs["name"]
    source = attrs["source"]
    target = attrs["target"]
    if len(set([source, target, name])) < 3:
        raise nx.NetworkXError('Attribute names are not unique.')
        
    multigraph = data.get('multigraph')
    directed = data.get('directed')
    if multigraph:
        graph = nx.MultiGraph()
    else:
        graph = nx.Graph()
    if directed:
        graph = graph.to_directed()
    graph.graph = dict(data.get('data'))
    for d in data["elements"]["nodes"]:
        node_data = d["data"].copy()
        node = d["data"]["value"]
        
        if d["data"].get(name):
            node_data[name] = d["data"].get(name)
#            continue
        
        graph.add_node(node)
        graph.node[node].update(node_data)
    for d in data["elements"]["edges"]:
        edge_data = d["data"].copy()
        sour = d["data"].get("source")
        targ = d["data"].get("target")
        graph.add_edge(sour, targ)
        graph.edge[sour][targ].update(edge_data)
    return graph

