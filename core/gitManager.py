import git
import os
from pathlib import Path

class GitManager:
    def __init__(self, repo_path):
        self.repo_path = Path(repo_path).absolute()
        self.repo = None

    def set_repo_path(self, path):
        """安全设置仓库路径并转换为Path对象"""
        self.repo_path = Path(path).absolute()

    def initialize(self):
        """初始化或加载现有Git仓库"""
        try:
            git_path = os.path.join(self.repo_path, '.git')
            if not os.path.exists(git_path):
                self.repo = git.Repo.init(self.repo_path)
                print(f"Initialized new Git repo at {self.repo_path}")
            else:
                self.repo = git.Repo(str(self.repo_path))  # 显式转换为字符串
                print(f"Loaded existing Git repo at {self.repo_path}")
        except git.InvalidGitRepositoryError:
            raise ValueError("指定路径不是有效的Git仓库")

    def create_decision_point(self, message):
        """创建决策点commit"""
        if not self.repo:
            raise RuntimeError("Git仓库未初始化")

        self.repo.git.add('.')
        commit = self.repo.index.commit(f"DECISION: {message}")
        return commit.hexsha

    def create_branch(self, branch_name, message):
        """从当前commit创建新分支"""
        if not self.repo:
            raise RuntimeError("Git仓库未初始化")

        # 在原始分支提交当前状态
        self.repo.git.add('.')
        original_commit = self.repo.index.commit(f"STATE: {message}")

        # 创建新分支并建立关联
        new_branch = self.repo.create_head(branch_name)
        self.repo.head.reference = new_branch
        self.repo.head.reset(index=True, working_tree=True)

        # 记录分支关系
        with open(os.path.join(self.repo_path, ".git/branches"), "a") as f:
            f.write(f"{new_branch.name} parent {original_commit.hexsha}\n")

        return new_branch.name

    def checkout_commit(self, commit_hash):
        """检出指定commit"""
        if not self.repo:
            raise RuntimeError("Git仓库未初始化")

        try:
            self.repo.git.checkout(commit_hash)
            return True
        except Exception as e:
            raise RuntimeError(f"检出失败: {str(e)}")

    def get_graph_data(self):
        """生成D3可视化所需的图数据"""
        import os  # 添加缺失的模块导入

        if not self.repo:
            return {"nodes": [], "links": []}

        # 获取所有本地分支及其上游分支关系
        branch_relations = {}

        # 1. 首先读取自定义的分支关系文件(保持向后兼容)
        branch_file = os.path.join(self.repo_path, ".git/branches")
        if os.path.exists(branch_file):
            with open(branch_file, "r") as f:
                for line in f.readlines():
                    branch, _, parent = line.strip().split()
                    branch_relations[branch] = parent

        # 2. 获取所有本地分支信息
        for branch in self.repo.heads:
            branch_name = branch.name
            # 如果分支未在关系文件中记录，则添加默认关系
            if branch_name not in branch_relations:
                # 获取分支的上游分支(如果有)
                tracking_branch = branch.tracking_branch()
                if tracking_branch:
                    branch_relations[branch_name] = tracking_branch.name
                else:
                    # 没有上游分支则指向分支创建时的父commit
                    branch_relations[branch_name] = branch.commit.hexsha

        # 获取git log的图形输出
        git_log = self.repo.git.log(
            '--all',
            '--graph',
            '--abbrev-commit',
            '--pretty=format:%h|%s|%ad|%p',
            '--date=short'
        )

        # 解析git log输出
        nodes = []
        links = []
        commit_cache = {}  # 存储commit信息: {hash: {"id": hash, ...}}
        branch_heads = {}

        # 第一遍遍历：收集所有commit信息
        for line in git_log.split('\n'):
            if not line.strip().startswith('*'):
                continue

            parts = line.split('|')
            commit_hash = parts[0].split()[-1]
            message = parts[1]
            date = parts[2]
            parent_hashes = parts[3].split()

            commit_data = {
                "id": commit_hash,
                "name": commit_hash[:7],
                "message": message,
                "date": date,
                "type": "decision" if "DECISION" in message else "branch" if "BRANCH" in message else "normal",
                "parents": parent_hashes
            }

            nodes.append(commit_data)
            commit_cache[commit_hash] = commit_data

            # 记录分支头指针
            if message.startswith("BRANCH:"):
                branch_name = message.split(":")[1].strip()
                branch_heads[branch_name] = commit_hash

        # 第二遍遍历：建立父子关系
        for commit in nodes:
            for parent_hash in commit["parents"]:
                if parent_hash in commit_cache:
                    links.append({
                        "from": parent_hash,
                        "to": commit["id"],
                    })

        # 添加分支关系链接
        for branch, parent in branch_relations.items():
            if branch in branch_heads and parent in branch_heads:
                links.append({
                    "from": branch_heads[parent],
                    "to": branch_heads[branch],
                })

        return {
            "nodes": nodes,
            "links": links,
            "branches": list(branch_heads.keys())
        }

if __name__ == '__main__':
    repoPath = "F:\\Games\\25-05-03\\克莱尔的任务Claire's Quest 0.28.1\\www\\save"
    gitManager = GitManager(repoPath)
    gitManager.initialize()
    data = gitManager.get_graph_data()
    nodes = data.get('nodes', [])
    links = data.get('links', [])
    branches = data.get('branches', [])
    for node in nodes:
        print(node)
    for link in links:
        print(link)
    # for branch in branches:
    #     print(branch)