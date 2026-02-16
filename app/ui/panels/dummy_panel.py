from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from app.ui.panel_header import PanelHeader


class DummyPanel(QWidget):
    def __init__(self, nav):
        """Execute   init  .
        
        Why this exists: this function encapsulates one focused part of the app workflow so callers can reuse
        the behavior without duplicating logic.
        """
        super().__init__()
        self.nav = nav

        header = PanelHeader("Dummy Panel", nav)
        body = QLabel("Dummy Sub Panel Content")

        layout = QVBoxLayout()
        layout.addWidget(header)
        layout.addWidget(body)

        self.setLayout(layout)
