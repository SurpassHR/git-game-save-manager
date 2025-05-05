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

        # 读取分支关系数据
        branch_relations = {}
        branch_file = os.path.join(self.repo_path, ".git/branches")
        if os.path.exists(branch_file):
            with open(branch_file, "r") as f:
                for line in f.readlines():
                    branch, _, parent = line.strip().split()
                    branch_relations[branch] = parent

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
        commit_cache = {}
        branch_heads = {}

        for line in git_log.split('\n'):
            if not line.strip().startswith('*'):
                continue

            parts = line.split('|')
            commit_hash = parts[0].split()[-1]
            message = parts[1]
            date = parts[2]
            parent_hashes = parts[3].split()

            nodes.append({
                "id": commit_hash,
                "name": commit_hash[:7],
                "message": message,
                "date": date,
                "type": "decision" if "DECISION" in message else "branch" if "BRANCH" in message else "normal"
            })

            # 记录分支头指针
            if message.startswith("BRANCH:"):
                branch_name = message.split(":")[1].strip()
                branch_heads[branch_name] = commit_hash

            # 建立父子关系
            for parent_hash in parent_hashes:
                if parent_hash in commit_cache:
                    links.append({
                        "source": commit_hash,
                        "target": parent_hash,
                        "type": "parent"
                    })

            commit_cache[commit_hash] = True

        # 添加分支关系链接
        for branch, parent in branch_relations.items():
            if branch in branch_heads and parent in branch_heads:
                links.append({
                    "source": branch_heads[branch],
                    "target": branch_heads[parent],
                    "type": "branch"
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