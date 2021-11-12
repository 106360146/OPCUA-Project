from opcua import ua
from opcua import client
from file_handler.handler_subscription import HandlerSubscription
from ua_system import UAClient
class UACommon():
    def __init__(self, log_info, userdata=None):
        self.on_connect = self.__on_connect
        #llamar super para pedir self.mydb y usarlo al llamar a
        #handler_subscription(mydb)
        

    def _on_connect(self, )
        #TODOLAU: subscribe to the nodes
        root = client.get_root_node()    
            
    def init_opcua(self, url): #TODOLAU: get the url from handler_ini_connection (example at mqtt_command.py)
        #TODOLAU: verify the url first
        self.url = url
        if self.url:
             #QUESTION: where should I do the connection?
            client.connect()
    
    def subscribe(self, nodeid, handler):#TODOLAU keep seeing what is useful from simple_UA_client.py
        handler = file_handler.handler_subscription()
        sub = client.create_subscription(10000, handler)
        handle_master = sub.subscribe_data_change(nodeid, ua.AttributeIds.Value, queuesize = 10)
    
    def browse_below_node(self, nodeid):
        node = self.client.get_node(nodeid)
        attributes = node.get_children_descriptions()
        nodeList = []
        for listElement in attributes:
            newID = listElement.NodeId.to_string()
            nodeList.append(newID)
            
            newNode = client.get_node(newID)
            newList = newNode.get_children_descriptions()
            if newList:
                for listElement in newList:
                    newID = listElement.NodeId.to_string()
                    nodeList.append(newID)

            else:
                continue
        
        return nodeList
        
    def read(self, nodeid): #IDEA： could add another argument called attribute to read
                            #       any attritube other than "Value"
        params = ua.ReadParameters()
        for node_id_str in self.browse_below_node(nodeid):
            nodeid = ua.NodeId.from_string(node_id_str)
            attr = ua.ReadValueId()
            attr.NodeId = nodeid
            attr.AttributeId = ua.AttributeIds.Value
            params.NodesToRead.append( attr )


#the client stablishes a connection with the server
#the client asks for info from the server
    #what kind of info 呢？
    #要顯示我們的tree
    #the server needs to access Pioneer's Redis topology
    #to display the information
        