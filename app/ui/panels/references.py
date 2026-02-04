from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea
)
import os
import json

from app.ui.panel_header import PanelHeader
from app.app_state import app_state
from core.profiles import get_profile_dirs


class ReferencesPanel(QWidget):
    """
    References Panel (FINAL)
    - Lists references
    - Shows parent frame
    - Allows selecting a reference
    - Allows creating new references from selected frame
    """

    def __init__(self, nav):
        super().__init__()
        self.selected_btn = None
        self.nav = nav

        header = PanelHeader("References", nav)

        self.info_label = QLabel("Selected reference: None")

        self.body_layout = QVBoxLayout()

        self.new_ref_btn = QPushButton("➕ New Reference")
        self.new_ref_btn.clicked.connect(self.create_reference)

        self.refresh_references()
        self.update_new_ref_button()

        container = QWidget()
        container.setLayout(self.body_layout)

        scroll = QScrollArea()
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)

        layout = QVBoxLayout()
        layout.addWidget(header)
        layout.addWidget(self.info_label)
        layout.addWidget(scroll)
        layout.addWidget(self.new_ref_btn)

        self.setLayout(layout)

    # ---------------- UI Refresh ----------------

    def refresh(self):
        self.refresh_references()
        self.update_new_ref_button()

        if app_state.selected_reference:
            self.info_label.setText(
                f"Selected reference: {app_state.selected_reference}"
            )
        else:
            self.info_label.setText("Selected reference: None")

    # ---------------- Reference Listing ----------------

    def refresh_references(self):
        while self.body_layout.count():
            item = self.body_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        profile = app_state.active_profile
        if not profile:
            self.body_layout.addWidget(QLabel("No profile selected"))
            return

        dirs = get_profile_dirs(profile)
        ref_dir = dirs["references"]

        refs = sorted(
            f for f in os.listdir(ref_dir)
            if f.lower().endswith(".png")
        )

        if not refs:
            self.body_layout.addWidget(QLabel("No references found"))
            return

        for ref in refs:
            parent = self.get_parent_frame(ref)
            btn = QPushButton(f"{ref}  ←  {parent}")
            btn.clicked.connect(lambda _, r=ref: self.select_reference(r))
            self.body_layout.addWidget(btn)

    def get_parent_frame(self, ref_name):
        """
        Safely get parent frame for a reference.
        Handles legacy references with missing / empty / broken metadata.
        """
        profile = app_state.active_profile
        dirs = get_profile_dirs(profile)

        meta_path = os.path.join(
            dirs["references"],
            ref_name.replace(".png", ".json")
        )

        # No metadata file at all → legacy reference
        if not os.path.exists(meta_path):
            return "legacy"

        try:
            with open(meta_path, "r") as f:
                content = f.read().strip()

                # Empty file → legacy
                if not content:
                    return "legacy"

                data = json.loads(content)
                return data.get("parent_frame", "legacy")

        except Exception:
            # ANY failure = legacy reference
            return "legacy"


    # ---------------- Actions ----------------

    def select_reference(self, ref_name):
        if app_state.monitoring_active:
            return
        app_state.selected_reference = ref_name
        self.info_label.setText(f"Selected reference: {ref_name}")

        if self.selected_btn:
            self.selected_btn.setStyleSheet("")

        self.selected_btn = self.sender()
        self.selected_btn.setStyleSheet(
            "font-weight: bold; background-color: #2d6cdf; color: white;"
        )


    def create_reference(self):
        if not app_state.selected_frame:
            return

        from app.ui.panels.crop_panel import CropPanel
        self.nav.push(CropPanel(self.nav), "crop")

    def update_new_ref_button(self):
        if app_state.selected_frame:
            self.new_ref_btn.setEnabled(True)
            self.new_ref_btn.setText(
                f"➕ New Reference (from {app_state.selected_frame})"
            )
        else:
            self.new_ref_btn.setEnabled(False)
            self.new_ref_btn.setText(
                "➕ New Reference (select a frame first)"
            )