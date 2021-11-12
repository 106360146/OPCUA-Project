from termcolor import colored

class Thread_Service():
    def __init__(self, redisdb_comm, opcua_comm, sys_evs, log_info):
        self.log_info = log_info
        self.logger   = log_info.init_class_logger( self.__class__.__name__ )

        self.redisdb_comm = redisdb_comm
        self.opcua_comm   = opcua_comm
        
        self.sys_evs = sys_evs
        self.srv = None

        self.timeout = 0.5

    def register_service(self, service):
        self.srv = service( self.redisdb_comm, self.opcua_comm, self.sys_evs, self.log_info )

    def get_service(self):
        return self.srv

    def loop(self):
        raise NotImplementedError(f"Service '{__class__.__name__}' not implemented.")

    def stop_service(self):
        msg  = colored(self.__class__.__name__, 'red')
        print(f"Service {msg} stopped.")

    def finished_service(self):
        msg  = colored(self.__class__.__name__, 'green')
        print(f"Service {msg} finished.")