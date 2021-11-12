from ua_system import UAServer
from system.thread_service import Thread_Service


class Service_OPCUAComm():

    def __init__(self, redisdb_comm, opcua_comm, sys_evs, log_info):
        self.sys_evs       = sys_evs
        self.log_info      = log_info
        self.logger        = log_info.init_class_logger( self.__class__.__name__ )

        self.redisdb       = redisdb_comm.get_redis()
        self.opcua_comm    = opcua_comm.get_opcua()
        self.ua_io_handler = opcua_comm.get_io_handler()
    
    def start_server(self):
        self.opcua_comm.start()

    def stop_server(self):
        self.opcua_comm.stop()

class ThreadOPCUAServer(Thread_Service):
    def __init__(self, redisdb_comm, opcua_comm, sys_evs, log_info):
        super().__init__(redisdb_comm, opcua_comm, sys_evs, log_info)
        self.register_service( Service_OPCUAComm )

    def loop(self):
        stop_event = self.sys_evs.get_stop_event()
        srv = self.get_service()
        
        srv.start_server()

        while not stop_event.isSet():
            stop_event_is_set = stop_event.wait( self.timeout )
            if stop_event_is_set:
                srv.stop_server()
                self.stop_service()
                return


            