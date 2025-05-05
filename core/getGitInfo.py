import os
from copy import copy, deepcopy
from datetime import datetime
from collections import defaultdict, OrderedDict
from git import Repo

class CommitObj:
    def __init__(
        self,
        hexSha: str,
        author: str | None,
        message: str | bytes,
        parents: list[str],
        children: list[str],
        branches: list[str],
        commitDate: str
    ):
        self.hexSha = hexSha
        self.author = author
        self.message = message
        self.parents = parents
        self.children = children
        self.branches = branches
        self.commitDate = commitDate

class GitRepoInfoMgr:
    def __init__(self, repoPath: str):
        if not self.checkRepoPathValid(repoPath):
            exit(-1)
        self.gitRepo = Repo.init(repoPath)
        assert not self.gitRepo.bare

    def checkRepoPathValid(self, repoPath: str) -> bool:
        return os.path.isdir(repoPath)

    def getBasicRepoCommitInfo(self) -> dict[str, CommitObj]:
        iterCommit = self.gitRepo.iter_commits('--all')
        commitDict: dict[str, CommitObj] = {}
        for commit in iterCommit:
            commitObj = CommitObj(
                hexSha=commit.hexsha[:8],
                author=commit.author.name,
                message=commit.message,
                parents=[parentHash.hexsha[:8] for parentHash in commit.parents],
                children=[],
                branches=[],
                commitDate=datetime.fromtimestamp(commit.committed_date).strftime("%Y-%m-%d %H:%M:%S"),
            )
            commitDict[commit.hexsha[:8]] = commitObj
        return commitDict

    def getRepoBranchInfo(self) -> list[str]:
        repoBranch = [branch.name for branch in self.gitRepo.branches]
        return repoBranch

    def getCommitHashFromEachBranch(self, branchNameList: list[str]) -> dict[str, list]:
        commitsInEachBranch: dict[str, list] = {}
        for branchName in branchNameList:
            commitsInBranch: list = []
            commits = self.gitRepo.iter_commits(branchName)
            for commit in commits:
                commitsInBranch.append(commit.hexsha[:8])
            commitsInEachBranch[branchName] = commitsInBranch

        return commitsInEachBranch

    def addBranchInfoToCommitDict(self, commitInfo: dict[str, CommitObj], commitsInEachBranch: dict[str, list]) -> dict[str, CommitObj]:
        for branchName, commitHashList in commitsInEachBranch.items():
            for commitHash in commitHashList:
                commitInfo[commitHash].branches.append(branchName)

        return commitInfo

    def addChildInfoToCommitDict(self, commitInfo: dict[str, CommitObj]) -> dict[str, CommitObj]:
        for commitHash, commitDict in commitInfo.items():
            for _hash, _dict in commitInfo.items():
                if commitHash in _dict.parents:
                    commitDict.children.append(_hash)

        return commitInfo

    def getRepoCommitInfo(self) -> dict[str, CommitObj]:
        commitInfoDict = self.getBasicRepoCommitInfo()
        branchNameList = self.getRepoBranchInfo()
        commitsInEachBranch = self.getCommitHashFromEachBranch(branchNameList)
        commitInfoDict = self.addBranchInfoToCommitDict(commitInfoDict, commitsInEachBranch)
        return self.addChildInfoToCommitDict(commitInfoDict)

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

        for _, edges in graph.items():
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
        is_valid, _ = self.validate(test_graph)
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

    def size(self):
        return len(self.graph)

def createDAG(commitInfo: dict[str, CommitObj]) -> DAG:
    graph = DAG()
    for commitHexSha in commitInfo.keys():
        graph.add_node(commitHexSha)
    for commitObj in commitInfo.values():
        parents = commitObj.parents
        for parent in parents:
            graph.add_edge(parent, commitObj.hexSha)
        children = commitObj.children
        for child in children:
            graph.add_edge(commitObj.hexSha, child)
    return graph

if __name__ == '__main__':
    repoPath = "F:\\Games\\25-05-03\\克莱尔的任务Claire's Quest 0.28.1\\www\\save"
    repoInfoMgr = GitRepoInfoMgr(repoPath)
    commitInfoDict = repoInfoMgr.getRepoCommitInfo()
    dagGraph = createDAG(commitInfoDict)
    print(dagGraph.topological_sort())
    print(dagGraph.graph)