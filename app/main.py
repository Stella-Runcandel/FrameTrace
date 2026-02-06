import sys
from PyQt6.QtCore import QCoreApplication
from PyQt6.QtWidgets import QApplication

from app.ui.app_shell import AppShell


def main():
    QCoreApplication.setOrganizationName("Frame Trace")
    QCoreApplication.setApplicationName("Frame Trace")
    app = QApplication(sys.argv)
    app.setApplicationName("Frame Trace")
    shell = AppShell()
    shell.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
