from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QFileDialog,
    QScrollArea
)
import os
import shutil

from app.ui.panel_header import PanelHeader
from app.app_state import app_state
from core.profiles import get_profile_dirs


class FramesPanel(QWidget):
    """
    Frames Panel
    - Shows all base frames for the active profile
    - Allows uploading multiple images
    - Allows selecting ONE frame for cropping
    """

    def __init__(self, nav):
        super().__init__()
        self.selected_btn = None
        self.nav = nav

        header = PanelHeader("Frames", nav)

        self.selected_label = QLabel("Selected frame: None")

        self.body_layout = QVBoxLayout()
        self.refresh_frames()

        add_btn = QPushButton("➕ Add Frames")
        add_btn.clicked.connect(self.add_frames)

        container = QWidget()
        container.setLayout(self.body_layout)

        scroll = QScrollArea()
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)

        layout = QVBoxLayout()
        layout.addWidget(header)
        layout.addWidget(self.selected_label)
        layout.addWidget(scroll)
        layout.addWidget(add_btn)

        self.setLayout(layout)

    def refresh_frames(self):
        # clear old entries
        while self.body_layout.count():
            item = self.body_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        profile = app_state.active_profile
        if not profile:
            self.body_layout.addWidget(QLabel("No profile selected"))
            return

        dirs = get_profile_dirs(profile)
        frames_dir = dirs["frames"]

        frames = sorted(
            f for f in os.listdir(frames_dir)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        )

        if not frames:
            self.body_layout.addWidget(QLabel("No frames uploaded"))
            return

        for frame in frames:
            btn = QPushButton(frame)
            btn.clicked.connect(
                lambda _, f=frame: self.select_frame(f)
            )
            self.body_layout.addWidget(btn)

    def add_frames(self):
        profile = app_state.active_profile
        if not profile:
            return

        files, _ = QFileDialog.getOpenFileNames(
            self,
            "Select frame images",
            "",
            "Images (*.png *.jpg *.jpeg)"
        )

        if not files:
            return

        dirs = get_profile_dirs(profile)
        frames_dir = dirs["frames"]

        for src in files:
            name = os.path.basename(src)
            dst = os.path.join(frames_dir, name)

            # avoid overwrite
            if not os.path.exists(dst):
                shutil.copy2(src, dst)

        self.refresh_frames()

    def select_frame(self, frame_name):
        if app_state.monitoring_active:
            return
        app_state.selected_frame = frame_name
        self.selected_label.setText(f"Selected frame: {frame_name}")

        if self.selected_btn:
            self.selected_btn.setStyleSheet("")

        self.selected_btn = self.sender()
        self.selected_btn.setStyleSheet(
            "font-weight: bold; background-color: #2d6cdf; color: white;"
        )
