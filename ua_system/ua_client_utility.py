from opcua import Client
"""
Usefull Low-Level OPCUA services' implementations for an
OPCUA CLIENT
Other OPCUA low-level services are contained by the UAManager class.
"""
class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription
    data_change and event methods are called directly from receiving thread.
    Do not do expensive, slow or network operation there. Create another 
    thread if you need to do such a thing
    """

    def datachange_notification(self, node, val, data):
        print("Python: New data change event", node, val)

    def event_notification(self, event):
        print("Python: New event", event)

class UAClient(Client):
    def __init__(self, url, timeout):
        super().__init__(url, timeout=timeout)

    def subscribe(self, node_id):
        """
        Subscribe to a variable node
        """
        my_variable = self.get_node(node_id)
        handler = SubHandler()
        subscription = client.create_subscription(5000, handler) #create_subscription(publish interval (ms)/
                                                        #CreateSubscriptionParameters isnctance, handler)
        handle = subscription.subscribe_data_change(my_variable)
        modify = subscription.modify_monitored_item(handle,10000,50,-1)
    
if __name__ == "__main__":
    
    client = UAClient("opc.tcp://127.0.0.1:4840")

    try:
        client.connect()

        # Client has a few methods to get proxy to UA nodes that should always be in address space such as Root or Objects
        root = client.get_root_node()
        objects = client.get_objects_node()

        # Node objects have methods to read and write node attributes as well as browse or populate address space
        root_children = root.get_children()
        object_children = objects.get_children()
    
    finally:
        client.disconnect
        