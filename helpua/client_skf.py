"""
FEATURES: opcua version of Ike's mqtt module

"""
import signal
import opcua
from file_handler import HandlerMain
from opcua import Client
from opcua import UaClient
from opcua import ua

#IDEA: combine  Ike's MQTTCommon and MQTTCommand in a suitable way
class UAClient():
    def __init__(self, log_info, userdata=None): #TODOLAU: rethink the arguments
        self.log_info = log_info
        file_handler = HandlerMain( self.log_info )

        db_config = file_handler.get_db_config()
        mydb = DatabaseProduction(db_config, self.log_info)

        self.client = StructClientData(file_handler, mydb, args) 

    def __register_signal(self):
        signal.signal( signal.SIGINT, self._signal_handler())
        signal.signal( signal.SIGTERM, self._signal_handler())
    
    def _signal_handler(self):
        client.disconnect()

    def __on_connect(self, )
        #TODOLAU: subscribe to the nodes

    def __set_url(self,url):
        #OBSERVATION: should not need this method because in OPCUA we only need the link to initialize
        
    def init_opcua(self, url): #TODOLAU: get the url from handler_ini_connection (example at mqtt_command.py)
        #TODOLAU: verify the url first
        if self.url:
            client = Client(url) #QUESTION: where should I do the connection?
            client.connect()

    def _get_root_node(self): #OBSERVATION: 我覺得method not necessary, 
                              #可以把get_root_node()應用在另外一邊
        root = client.get_root_node()
    
    def browse_below_node(self, nodeid):#QUESTION： should I create a class for the services?
        node = client.get_node(nodeid)
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

    def subscribe(self, nodeid):#TODOLAU keep seeing what is useful from simple_UA_client.py
        handler = file_handler.handler_subscription
        sub = client.create_subscription(10000, handler)
        handle_master = sub.subscribe_data_change(nodeid, ua.AttributeIds.Value, queuesize = 10)
        #FIXME: this goes in __on_connect
        # 1. get the nodes to subscribe to
        # 2. subcribe
        # 3. set the parameters (like queuesize, sampling interval...) 