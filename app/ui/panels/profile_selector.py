from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel
)

from app.ui.panel_header import PanelHeader
from app.app_state import app_state
from core.profiles import list_profiles, create_profile
from PyQt6.QtWidgets import QInputDialog, QMessageBox
from core.profiles import create_profile, list_profiles


class ProfileSelectorPanel(QWidget):
    def __init__(self, nav):
        super().__init__()
        self.nav = nav

        # ---- header ----
        header = PanelHeader("Select Profile", nav)

        # ---- body ----
        self.body_layout = QVBoxLayout()

        self.refresh_profiles()

        # ---- create profile button ----
        create_btn = QPushButton("➕ Create New Profile")
        create_btn.clicked.connect(self.create_profile)

        # ---- main layout ----
        layout = QVBoxLayout()
        layout.addWidget(header)
        layout.addLayout(self.body_layout)
        layout.addWidget(create_btn)

        self.setLayout(layout)

    def refresh_profiles(self):
        # clear old buttons
        while self.body_layout.count():
            item = self.body_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        profiles = list_profiles()

        if not profiles:
            self.body_layout.addWidget(QLabel("No profiles found"))
            return

        for name in profiles:
            btn = QPushButton(name)
            btn.clicked.connect(lambda _, n=name: self.select_profile(n))
            self.body_layout.addWidget(btn)

    def select_profile(self, name):
        if app_state.monitoring_active:
            return
        app_state.active_profile = name
        self.nav.pop()  # go back to dashboard

    def create_profile(self):
        # TEMP simple creation (no dialog yet)
        name = f"Profile_{len(list_profiles()) + 1}"
        create_profile(name)
        self.refresh_profiles()
        
    def create_profile(self):
        name, ok = QInputDialog.getText(
            self,
            "Create New Profile",
            "Enter profile name:"
        )

        if not ok or not name.strip():
            return

        name = name.strip()

        if not create_profile(name):
            QMessageBox.warning(
                self,
                "Profile Exists",
                f"A profile named '{name}' already exists."
            )
            return

        # Auto-select new profile
        app_state.active_profile = name
        app_state.selected_frame = None
        app_state.selected_reference = None

        self.refresh_profiles()

        QMessageBox.information(
            self,
            "Profile Created",
            f"Profile '{name}' created and selected."
        )

        # Go back to dashboard
        self.nav.pop()
