import sys
import os
from pathlib import Path
from datetime import datetime
from git import Repo
from rich import print

rootPath = str(Path(__file__).resolve().parent.parent)
sys.path.append(rootPath)

from core.algorithms.dag import DAG


class CommitObj:
    def __init__(
        self,
        hexSha: str = "",
        author: str | None = "",
        message: str | bytes = "",
        parents: list[str] = [],
        children: list[str] = [],
        branches: list[str] = [],
        commitDate: str = "",
    ):
        self.hexSha = hexSha
        self.author = author
        self.message = message
        self.parents = parents
        self.children = children
        self.branches = branches
        self.commitDate = commitDate

    def setItem(self, key: str, value: str | int | list):
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise KeyError(f"Key {key} not found in CommitObj")

    def getDict(self) -> dict:
        return self.__dict__

    def getKeys(self) -> list:
        return list(self.getDict().keys())

class GitRepoInfoMgr(DAG):
    def __init__(self, repoPath: str):
        super().__init__()

        if not self.checkRepoPathValid(repoPath):
            exit(-1)
        self.gitRepo = Repo.init(repoPath)
        assert not self.gitRepo.bare

    def checkRepoPathValid(self, repoPath: str) -> bool:
        return os.path.isdir(repoPath)

    def getBasicRepoCommitInfo(self) -> dict[str, CommitObj]:
        iterCommit = list(self.gitRepo.iter_commits('--all'))
        commitDict: dict[str, CommitObj] = {}
        for commit in iterCommit:
            hexSha = commit.hexsha[:8]
            commitObj = CommitObj(
                hexSha=hexSha,
                author=commit.author.name,
                message=commit.message,
                children=[],
                branches=[],
                commitDate=datetime.fromtimestamp(commit.committed_date).strftime("%Y-%m-%d %H:%M:%S"),
            )
            self.add_node(hexSha)
            commitDict[hexSha] = commitObj

        for commit in iterCommit:
            hexSha = commit.hexsha[:8]
            parents = [parentHash.hexsha[:8] for parentHash in commit.parents]
            commitDict[hexSha].setItem("parents", parents)
            for parent in parents:
                self.add_edge(parent, hexSha)

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
                    self.add_edge(commitHash, _hash)

        return commitInfo

    def getRepoRawCommitInfo(self) -> dict[str, CommitObj]:
        self.reset_graph()
        commitInfoDict = self.getBasicRepoCommitInfo()
        branchNameList = self.getRepoBranchInfo()
        commitsInEachBranch = self.getCommitHashFromEachBranch(branchNameList)
        commitInfoDict = self.addBranchInfoToCommitDict(commitInfoDict, commitsInEachBranch)
        return self.addChildInfoToCommitDict(commitInfoDict)

    # 通过 mr 节点关系建立有向无环图
    # def createDAG(self, commitInfo: Optional[dict[str, CommitObj]] = None) -> DAG:
    #     commitInfo = self.getRepoRawCommitInfo() if commitInfo is None else commitInfo
    #     graph = DAG()
    #     for commitHexSha in commitInfo.keys():
    #         graph.add_node(commitHexSha)
    #     for commitObj in commitInfo.values():
    #         parents = commitObj.parents
    #         for parent in parents:
    #             graph.add_edge(parent, commitObj.hexSha)
    #         children = commitObj.children
    #         for child in children:
    #             graph.add_edge(commitObj.hexSha, child)
    #     return graph

if __name__ == '__main__':
    repoPath = "F:\\Games\\25-05-03\\克莱尔的任务Claire's Quest 0.28.1\\www\\save"
    repoInfoMgr = GitRepoInfoMgr(repoPath)
    commitInfo = repoInfoMgr.getRepoRawCommitInfo()
    print(commitInfo)
    print(repoInfoMgr.graph.__dict__)
    # print(repoInfoMgr.createDAG().graph)