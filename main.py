import sys
from core.gitManager import GitManager
from ui.main_window import MainWindow
from PyQt5.QtWidgets import QApplication

def main():
    app = QApplication(sys.argv)
    git_manager = GitManager("./saves")  # 默认存档目录
    window = MainWindow(git_manager)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()