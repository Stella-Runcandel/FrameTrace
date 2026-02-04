from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton
)

import os
import cv2
import json

from app.ui.panel_header import PanelHeader
from app.app_state import app_state
from core.profiles import get_profile_dirs


class CropPanel(QWidget):
    def __init__(self, nav):
        super().__init__()
        self.nav = nav

        header = PanelHeader("Crop Reference", nav)

        self.info_label = QLabel(
            "Crop a base frame to create a reference"
        )

        add_crop_btn = QPushButton("➕ Add Crop")
        add_crop_btn.clicked.connect(self.add_crop)

        layout = QVBoxLayout()
        layout.addWidget(header)
        layout.addWidget(self.info_label)
        layout.addWidget(add_crop_btn)

        self.setLayout(layout)

    def add_crop(self):
        profile = app_state.active_profile
        frame = app_state.selected_frame

        if not profile or not frame:
            return

        dirs = get_profile_dirs(profile)

        frame_path = os.path.join(dirs["frames"], frame)

        if not os.path.exists(frame_path):
            return

        # Load ORIGINAL frame (read-only)
        img = cv2.imread(frame_path)
        if img is None:
            return

        # Select ROI on a COPY (frame itself is untouched)
        roi = cv2.selectROI(
            "Crop reference from frame",
            img,
            fromCenter=False,
            showCrosshair=True
        )

        x, y, w, h = roi
        if w <= 0 or h <= 0:
            cv2.destroyAllWindows()
            return

        crop = img[y:y+h, x:x+w]

        # ---- Save as NEW reference ----
        base = os.path.splitext(frame)[0]

        refs_dir = dirs["references"]
        existing = [
            f for f in os.listdir(refs_dir)
            if f.startswith(base) and f.endswith(".png")
        ]

        ref_name = f"{base}_ref{len(existing)+1}.png"
        ref_path = os.path.join(refs_dir, ref_name)

        cv2.imwrite(ref_path, crop)

        # ---- Save metadata (parent frame) ----
        meta_path = ref_path.replace(".png", ".json")
        with open(meta_path, "w") as f:
            json.dump(
                {"parent_frame": frame},
                f,
                indent=2
            )

        cv2.destroyAllWindows()