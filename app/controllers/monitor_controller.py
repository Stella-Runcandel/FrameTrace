import logging

from app.app_state import app_state


class MonitorController:
    def __init__(self, monitor_service):
        """Execute   init  .
        
        Why this exists: this function encapsulates one focused part of the app workflow so callers can reuse
        the behavior without duplicating logic.
        """
        self.monitor = monitor_service

    def start(self):
        """Execute start.
        
        Why this exists: this function encapsulates one focused part of the app workflow so callers can reuse
        the behavior without duplicating logic.
        """
        if not app_state.active_profile:
            return "No profile selected"

        if self.monitor.isRunning():
            return "Already monitoring"

        self.monitor.start()
        return "Monitoring start requested"

    def stop(self):
        """Execute stop.
        
        Why this exists: this function encapsulates one focused part of the app workflow so callers can reuse
        the behavior without duplicating logic.
        """
        if not self.monitor.isRunning():
            return "Not monitoring"

        self.monitor.stop()
        if not self.monitor.wait(5000):
            logging.warning("Monitor thread did not exit within 5 seconds")
        app_state.monitoring_active = False
        return "Monitoring stop requested"
