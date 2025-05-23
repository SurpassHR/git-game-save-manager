import sys
from pathlib import Path
from collections import OrderedDict, defaultdict
from copy import copy, deepcopy

rootPath = str(Path(__file__).resolve().parent.parent.parent)
sys.path.append(rootPath)

from core.tools.utils.simpleLogger import loggerPrint

class DAG(object):
    """ Directed acyclic graph implementation. """

    def __init__(self):
        """ Construct a new DAG with no nodes or edges. """
        self.reset_graph()

    def add_node(self, node_name, graph=None):
        """ Add a node if it does not exist yet, or error out. """
        if not graph:
            graph = self.graph
        if node_name in graph:
            raise KeyError('node %s already exists' % node_name)
        graph[node_name] = set()

    def add_node_if_not_exists(self, node_name, graph=None):
        try:
            self.add_node(node_name, graph=graph)
        except KeyError:
            pass

    def delete_node(self, node_name, graph=None):
        """ Deletes this node and all edges referencing it. """
        if not graph:
            graph = self.graph
        if node_name not in graph:
            raise KeyError('node %s does not exist' % node_name)
        graph.pop(node_name)

        for node, edges in graph.items():
            if node_name in edges:
                edges.remove(node_name)

    def delete_node_if_exists(self, node_name, graph=None):
        try:
            self.delete_node(node_name, graph=graph)
        except KeyError:
            pass

    def add_edge(self, ind_node, dep_node, graph=None):
        """ Add an edge (dependency) between the specified nodes. """
        if not graph:
            graph = self.graph
        if ind_node not in graph or dep_node not in graph:
            raise KeyError('one or more nodes do not exist in graph')
        test_graph = deepcopy(graph)
        test_graph[ind_node].add(dep_node)
        is_valid, message = self.validate(test_graph)
        if is_valid:
            graph[ind_node].add(dep_node)
        else:
            raise Exception()

    def delete_edge(self, ind_node, dep_node, graph=None):
        """ Delete an edge from the graph. """
        if not graph:
            graph = self.graph
        if dep_node not in graph.get(ind_node, []):
            raise KeyError('this edge does not exist in graph')
        graph[ind_node].remove(dep_node)

    def rename_edges(self, old_task_name, new_task_name, graph=None):
        """ Change references to a task in existing edges. """
        if not graph:
            graph = self.graph
        for node, edges in graph.items():

            if node == old_task_name:
                graph[new_task_name] = copy(edges)
                del graph[old_task_name]

            else:
                if old_task_name in edges:
                    edges.remove(old_task_name)
                    edges.add(new_task_name)

    def predecessors(self, node, graph=None):
        """ Returns a list of all predecessors of the given node """
        if graph is None:
            graph = self.graph
        return [key for key in graph if node in graph[key]]

    def downstream(self, node, graph=None):
        """ Returns a list of all nodes this node has edges towards. """
        if graph is None:
            graph = self.graph
        if node not in graph:
            raise KeyError('node %s is not in graph' % node)
        return list(graph[node])

    def all_downstreams(self, node, graph=None):
        """Returns a list of all nodes ultimately downstream
        of the given node in the dependency graph, in
        topological order."""
        if graph is None:
            graph = self.graph
        nodes = [node]
        nodes_seen = set()
        i = 0
        while i < len(nodes):
            downstreams = self.downstream(nodes[i], graph)
            for downstream_node in downstreams:
                if downstream_node not in nodes_seen:
                    nodes_seen.add(downstream_node)
                    nodes.append(downstream_node)
            i += 1
        return list(
            filter(
                lambda node: node in nodes_seen,
                self.topological_sort(graph=graph)
            )
        )

    def all_leaves(self, graph=None):
        """ Return a list of all leaves (nodes with no downstreams) """
        if graph is None:
            graph = self.graph
        return [key for key in graph if not graph[key]]

    def from_dict(self, graph_dict):
        """ Reset the graph and build it from the passed dictionary.
        The dictionary takes the form of {node_name: [directed edges]}
        """

        self.reset_graph()
        for new_node in graph_dict.keys():
            self.add_node(new_node)
        for ind_node, dep_nodes in graph_dict.items():
            if not isinstance(dep_nodes, list):
                raise TypeError('dict values must be lists')
            for dep_node in dep_nodes:
                self.add_edge(ind_node, dep_node)

    def reset_graph(self):
        """ Restore the graph to an empty state. """
        self.graph = OrderedDict()

    def ind_nodes(self, graph=None):
        """ Returns a list of all nodes in the graph with no dependencies. """
        if graph is None:
            graph = self.graph

        dependent_nodes = set(
            node for dependents in graph.values() for node in dependents
        )
        return [node for node in graph.keys() if node not in dependent_nodes]

    def validate(self, graph=None):
        """ Returns (Boolean, message) of whether DAG is valid. """
        graph = graph if graph is not None else self.graph
        if len(self.ind_nodes(graph)) == 0:
            return False, 'no independent nodes detected'
        try:
            self.topological_sort(graph)
        except ValueError:
            return False, 'failed topological sort'
        return True, 'valid'

    def topological_sort(self, graph=None):
        """ Returns a topological ordering of the DAG.
        Raises an error if this is not possible (graph is not valid).
        """
        if graph is None:
            graph = self.graph
        result = []
        in_degree = defaultdict(lambda: 0)

        for u in graph:
            for v in graph[u]:
                in_degree[v] += 1
        ready = [node for node in graph if not in_degree[node]]

        while ready:
            u = ready.pop()
            result.append(u)
            for v in graph[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    ready.append(v)

        if len(result) == len(graph):
            return result
        else:
            raise ValueError('graph is not acyclic')

    def graphSize(self):
        return len(self.graph)

    def distance(self, nodeA: str, nodeB: str) -> int:
        def findPath(fromNode: str, toNode: str, path: list[str]) -> None:
            if fromNode == toNode:
                return

            fromNodeDown = self.downstream(fromNode)
            for node in fromNodeDown:
                currNodeDown = self.all_downstreams(node)
                if toNode in currNodeDown or toNode in fromNodeDown:
                    path.append(node)
                    findPath(node, toNode, path)
                    return

        if nodeA == nodeB:
            return 0
        path: list[str] = []
        # A 是 B 的下游
        nodeADownstream = self.all_downstreams(nodeA)
        nodeBDownstream = self.all_downstreams(nodeB)
        if nodeA in nodeBDownstream:
            findPath(
                fromNode=nodeB,
                toNode=nodeA,
                path=path,
            )
        # B 是 A 的下游
        elif nodeB in nodeADownstream:
            findPath(
                fromNode=nodeA,
                toNode=nodeB,
                path=path,
            )
        # loggerPrint(f"nodeA: '{nodeA}', nodeB: '{nodeB}' - {path}")
        return len(path)

    def get_all_edges(self, graph = None):
        if graph is None:
            graph = self.graph
        edges = []
        for node, neighbors in graph.items():
            for neighbor in neighbors:
                edges.append((node, neighbor))
        return edges

    # 获取节点的直接上游节点
    def upstream(self, node: str) -> list[str]:
        # 所有该节点的直接下游节点
        downStream: list[str] = list(self.graph[node])
        # 非直接下游节点
        excludeDownStream: list[str] = [n for n in self.graph.keys() if n not in downStream]
        # 非直接下游节点中的该节点的直接上游节点
        return [n for n in excludeDownStream if node in self.downstream(n)]

    # 获取直接连接该节点的所有节点
    def directNodes(self, node: str) -> list[str]:
        return self.upstream(node) + self.downstream(node)


if __name__ == '__main__':
    dag = DAG()
    dag.add_node("a")
    dag.add_node("b")
    dag.add_node("c")
    dag.add_node("d")
    dag.add_node("e")
    dag.add_edge("a", "b")
    dag.add_edge("a", "d")
    dag.add_edge("b", "c")
    dag.add_edge("c", "e")
    # pprint(dag.topological_sort())
    loggerPrint(f"{dag.graph}")
    # pprint(dag.all_downstreams("b"))
    loggerPrint(f"{dag.distance("b", "e")}")
    loggerPrint(f"{dag.get_all_edges()}")
    loggerPrint(f"{dag.directNodes("b")}")