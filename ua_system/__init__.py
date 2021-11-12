
from ua_system.ua_config_importer import ConfigImporter
from ua_system.ua_wrappers.server_wrap import ServerWrap, InternalServerWrap
from ua_system.io_handler import IOHandler
"""
1. For the config importing -> Github's 
   python-opcua/examples/simple-client-server-xml/server.py /

2. For file handling -> 本 module 之 file_handler
ReadRequest Numeric Node ID = 629
"""
try:
    from IPython import embed
except ImportError:
    import code

    def embed():
        myvars = globals()
        myvars.update(locals())
        shell = code.InteractiveConsole(myvars)
        shell.interact()

class UAServer():
    """
    OPC UA Server ready to explore production lines topology through Redis
     
    """
    def __init__(self, opcua_info, nodes_info, sys_evs, log_info):#本來是(self, endpoint, name, config_path)
        self.log_info     = log_info
        self.logger       = log_info.init_class_logger( self.__class__.__name__ )
        self.server       = ServerWrap()
        self.nodes_struct = nodes_info
        self.conn_info    = opcua_info
        self.sys_evs      = sys_evs
        
        endpoint               = self.conn_info.get_endpoint()
        name                   = self.conn_info.get_name()
        self.namespace_id      = self.conn_info.get_namespace_id()

        self.server.set_endpoint( endpoint )
        self.logger.info(f"Server endpoint set {endpoint}")
        self.server.set_server_name( name )
        
        namespace = self.server.register_namespace("PNR OPC UA Server")
        node = self.server.get_objects_node()
        
        folder_node = node.add_folder(namespace, "Pioneer Machinery")

        ini_path          = self.nodes_struct.config_path
        
        #  This needs to be imported at the start or else it will overwrite the data
        self.import_config( ini_path )#fh_main contains the config path

        self.io_handler = IOHandler(self.server, self.sys_evs, self.log_info)
        self.server.iserver.add_request_handler("Read Request Event", self.io_handler)
    
    def start(self):
        self.server.start()
        self.logger.info("Succesfully started")

    def stop(self):
        self.server.stop()
        self.logger.info("Succesfully stopped")

    def get_root_node(self):
        return self.server.get_root_node()

    def get_sys_evs(self):
        return self.sys_evs
    
    def import_config(self, config_path):
        """
        Import nodes defined in INI config
        """
        importer = ConfigImporter( self.server, self.namespace_id, self.log_info )
        
        return importer.import_config( config_path )
        