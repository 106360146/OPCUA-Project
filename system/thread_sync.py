"""
Syncing OPCUA and Redis
Creating threads to be started at __init__.py (System)
use instead of the IO_handler 吧 or use WITH the IO_handler 
(maybe some of its functions)
"""
from system.thread_service import Thread_Service
import collections
import threading
class SyncOPCUARedis():
    """
    connect_redis() should become the __init__ function of IOManager
    the signal when receiveng a Read Request should be sent by the SyncOPCUARedis() class
    """
    def __init__(self, redisdb_comm, opcua_comm, sys_evs, log_info):
        self.sys_evs       = sys_evs
        self.log_info      = log_info
        self.logger        = log_info.init_class_logger( self.__class__.__name__ )

        self.redisdb       = redisdb_comm.get_redis()
        self.opcua_comm    = opcua_comm.get_opcua()
        self.ua_io_handler = opcua_comm.get_io_handler()
        
        self.nodes_to_sync      = list()
        
    def start_sync(self, nodes_to_sync):
        #nodes_to_sync = {'ns=2;s=st_20033-40_smbplc.main': ['ns=2;s=st_20033-40_smbplc.main.ser_id', 
        #'ns=2;s=st_20033-40_smbplc.main.digital_input_w0', 'ns=2;s=st_20033-40_smbplc.main.digital_output_w0']}
        
        self.nodes_to_sync = nodes_to_sync
            
        result = self.__start_sync( self.nodes_to_sync )

        self.ua_io_handler.assign_nodes_values(result)

        return

    def __start_sync(self, node_list):

        rd_keys = self.redis_keys_name(node_list)#{node_id:redis_key_2}

        redis_values = self.__get_redis_values(rd_keys)#{redis_key:value}
        
        result = self.__map_values(redis_values, rd_keys)

        return result

    def __map_values(self, redis_values, rd_keys):
        ua_data = collections.OrderedDict()
        for redis_key, value in redis_values.items():
            for node_id, redis_key_2 in rd_keys.items():
                if redis_key == redis_key_2:
                    ua_data[node_id] = value
        
        return ua_data
    
    def __from_ndId_to_redis(self, ndId_string):
        #ndId_string  = "ns=2;s=ex-2.energy.ser-id"
        ndI_list = ndId_string.split(";")
        self.crrnt_namespace = ndI_list[0]
        del ndI_list[0]
        ndI_list = ndI_list[0].split("=")
        del ndI_list[0]
        
        return ndI_list[0]# = ex-2.energy.ser-id
    
    def __get_redis_values(self, rd_keys):
        keys_data = collections.OrderedDict()
        for key, value in rd_keys.items():
            if value not in keys_data:
                data = self.redisdb.get_line_data(value)
                keys_data[value] = data
        self.logger.info(f"keys_data: {keys_data}")
        return keys_data

    def redis_keys_name(self, node_id_list ):
        """
        From node id to redis elements
        """
        redis_names = {}
        for node_id in node_id_list:
            node_id_redis = self.__from_ndId_to_redis(node_id)
            redis_names[node_id] =  node_id_redis

        return redis_names

class ThreadSyncOPCUARedis( Thread_Service ):
    def __init__(self, redisdb_comm, opcua_comm, sys_evs, log_info ):
        super().__init__(redisdb_comm, opcua_comm, sys_evs, log_info )
        self.register_service( SyncOPCUARedis )
        
    def loop(self):
        sync_event = self.sys_evs.get_sync_event()
        stop_event = self.sys_evs.get_stop_event()
        srv = self.get_service()
        
        while not stop_event.isSet():
            
            while not sync_event.isSet():
                stop_event_is_set = stop_event.wait( self.timeout )
                if stop_event_is_set:
                    break
                
                self.logger.debug("Waiting for sync event!")

                sync_event_is_set = sync_event.wait( self.timeout )    
                if sync_event_is_set:
                    self.logger.debug('sync_event set: %s', sync_event_is_set)
                    nodes_to_sync = self.opcua_comm.get_nodes_to_sync()
                    self.logger.debug(f"Nodes to sync{nodes_to_sync}")
                    
                    srv.start_sync(nodes_to_sync)
                    self.finished_service()

        self.stop_service()