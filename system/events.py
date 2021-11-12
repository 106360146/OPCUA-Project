import threading

class System_Events():

    def __init__(self):
        self.stop_event    = threading.Event()
        self.sync_event    = threading.Event()
        self.unpause_event = threading.Event()
    def get_stop_event(self):
        return self.stop_event

    def get_sync_event(self):
        return self.sync_event

    def get_unpause_event(self):
        return self.unpause_event
    
    def stop(self):
        self.stop_event.set()