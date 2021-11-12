import threading #maybe will need, maybe not
import signal
import opcua
from mariadb.db_production import Database_Production
from log import LOG_INFORMATION
from file_handler import HandlerMain
from file_handler.handler_subscription import HandlerSubscription
from ua_system.ua_common import UACommon 
from opcua import Client
from opcua import UaClient
from opcua import ua

"""
FEATURES: 
    - call for the creation of the Database and its tables
    - implementation of OPC UA Services (subscription, subscription_handler #should be a class (?))
    - tables processing (insert, query, 什麼的。。。)
"""

class StructClientData(): #QUESTION: why the need of this class? no functions, only attributes
                          #ANSWER: to safe valuable info handled by the client
    def __init__(self, file_handler, mydb, args):
        self.file_handler = file_handler
        self.mydb = mydb
        self.args = args

class UAClient():
    def __init__(self, args):
        self.log_info = LOG_INFORMATION(args.log_level, args.log_classes) #TODOLAU: UNDERSTAND THE LOG THING 
                                                                          #COMING FROM main.py
        file_handler = HandlerMain( self.log_info )

        db_config = file_handler.get_db_config()
        mydb = DatabaseProduction(db_config, self.log_info)

        self.clientData = StructClientData(file_handler, mydb, args) 
        
        client = UACommon()
        url = file_handler.opcua_info
        #UA_command
        #TODOLAU: CONFIGURE SUBSCRIPTION SERVICES, SUBHANDLER, EVENTS
    
    def _register_signal(self):
        signal.signal( signal.SIGINT, self._signal_handler())
        signal.signal( signal.SIGTERM, self._signal_handler())
    
    def _signal_handler(self):
        client.client.disconnect() #QUESTION: how does it know what disconnect I am calling?

    def _get_root_node(self): #OBSERVATION: 我覺得method not necessary, 
                              #可以把get_root_node()應用在另外一邊
        root = self.client.get_root_node()
    
    def _set_url():
        
        """
        try:
            client = Client(url)
            client.init_opcua()
        except:
        """

    def _ua_command(self, log_info, userdata):
        #init UACommon()
    
    def _create_subscription(self,handler):
        handler = file_handler.handler_subscription
        subscription = client.subscribe(nodeid, handler)


