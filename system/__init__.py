"""
Follow Ike's Service_Main at service/__init__.py
"""
import threading
import signal

from log                             import LOG_INFORMATION 
from file_handler                    import HandlerMain
from system.thread_opcua_server      import ThreadOPCUAServer
from system.thread_sync              import ThreadSyncOPCUARedis
from system.events                   import System_Events
from system_communication.redis_comm import RedisComm
from system_communication.opcua_comm import OPCUAComm

class SystemMain():
    """
    Main class that controls all the features of the system:
        - OPCUA Server 
        - Redis 
        - Import/Export of information from excel files
        - Communication with main
    """

    system_modules = [
        ThreadSyncOPCUARedis,
        ThreadOPCUAServer,
    ]

    def __init__(self, args):
        self.log_info = LOG_INFORMATION( args.log_level, args.log_classes )
        self.logger   = self.log_info.init_class_logger( self.__class__.__name__ )

        self.sys_evs = System_Events()
        self.threads = list()
        
        self.__register_signal()

        fh_main = HandlerMain( self.log_info, args.reload_excel)

        self.opcua_comm = OPCUAComm( fh_main, self.log_info,  self.sys_evs)#contains the UAServer
        self.redis_comm = RedisComm( fh_main, self.log_info )#contains the redisDB
        
        self.services = list()
        self.__START_SYSTEM() 



    def __register_signal(self):
        signal.signal( signal.SIGTERM, lambda signal, frame: self.__de_initialization() )
        signal.signal( signal.SIGINT , lambda signal, frame: self.__de_initialization() )

    def __de_initialization(self):
        print("\nGot an interrupt signal, stopping all services ... ")
        self.sys_evs.stop()

    def __START_SYSTEM(self):
        for module in __class__.system_modules:
            srvc_thrd = module( self.redis_comm, self.opcua_comm, self.sys_evs, self.log_info )
            self.__start_system( callback_func=srvc_thrd.loop, thread_name=srvc_thrd.__class__.__name__ )
            self.services.append( srvc_thrd )

    def __start_system(self, callback_func, thread_name, args=(), kwargs=None):
        thr = threading.Thread(target=callback_func, name=thread_name, args=args, kwargs=kwargs)
        thr.start()
        self.threads.append(thr)
    
    def loop(self):
        for thread in self.threads:
            thread.join()