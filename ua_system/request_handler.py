from opcua.ua.uaprotocol_hand import ErrorMessage

class RequestHandler():
    
    def __init__(self, server, sys_evs, log_info) -> None:
        self.server   = server
        self.sys_evs  = sys_evs
        self._data    = None
        self._event   = None
        self.log_info = log_info
        
    def datachange_notification(self, node, val, data):
        print("Python: New data change event", node, val)

    def event_notification(self, event):
        print("Python: New event", event)    
        self._event = event

class EventCommunicator():
    
    def __init__(self):
        self._handlers = {}


    def dispatch(self, eventName, params):
        if eventName not in self._handlers:
            raise ErrorMessage('No handler for this request type')
        else:
            isinstance(self._handlers[eventName], RequestHandler)
            if hasattr(self._handlers[eventName], "event_notification"):
                try:
                   unpause_event = self._handlers[eventName].event_notification(params)
                   return unpause_event
                except Exception as err:
                    print(f"Not possible to run IOHandler's event_notificaiton. Error = {err}")                
        

    def add_handler(self, event_name, handler):
        #Only one handler for each kind of event
        self._handlers[event_name] = handler

    def remove_handler(self, event_Name, handler=None):
        del self._handlers[event_Name]