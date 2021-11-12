from ua_system            import UAServer

class OPCUAComm():
    def __init__(self, fh_main, log_info,  sys_evs ):
        self.log_info   = log_info
        self.nodes_info = fh_main.get_ini_nodes_struct()
        self.opcua_info = fh_main.opcua_info()
        self.sys_evs    = sys_evs

        self.opcua      = UAServer( self.opcua_info, self.nodes_info, self.sys_evs, self.log_info )
        
    def get_opcua(self):
        return self.opcua

    def get_io_handler(self):
        return self.opcua.io_handler

    def get_nodes_to_sync(self):
        return self.opcua.io_handler.get_nodes_to_sync()

