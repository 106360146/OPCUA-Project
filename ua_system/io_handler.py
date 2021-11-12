#redis的朋友
import collections
from threading import Lock
from typing import Dict
from ua_system.request_handler import RequestHandler
from ua_system.ua_manager import UAManager
from opcua import ua
from opcua.ua.object_ids import ObjectIds
class IOHandler(RequestHandler):
    """
    Controls the retrievement of nodes values from Redis when 
    required by the client 
    """

    """
    retreive values from Redis and assign them to the corresponding
    OPC UA Nodes
    """
    
    def __init__(self, uaserver, sys_evs, log_info):
        super().__init__(uaserver, sys_evs, log_info)
        self.server        = uaserver
        self.sys_evs       = sys_evs
        self.log_info      = log_info
        self.logger        = self.log_info.init_class_logger( self.__class__.__name__ )
        self.nodes_to_sync = None
        self.sync          = False
        self.ua_manager    = UAManager( self.server, self.log_info )
        self.sync_event    = self.sys_evs.get_sync_event() 
        self.unpause_event = self.sys_evs.get_unpause_event()

    def _get_nodes_from_sync(self, nodes_to_write):
        """
        The info comes back from Redis, time to assign values to the UA Nodes
        """     
        self.__write_nodes(nodes_to_write)

    def event_notification(self, nodes_to_read):
        self.nodes_to_read = nodes_to_read
        selected_nodes = self.select_nodes_to_sync()
        if selected_nodes: 
            self.nodes_to_sync = selected_nodes
            self.sync = True
            self.sync_event.set()
            self.logger.debug(f"Selected_nodes:{selected_nodes}") 
            return self.sys_evs.get_unpause_event()

        else:
            return None
                                     
    def select_nodes_to_sync(self):
        get_from_redis = []
        for read_value_id in self.nodes_to_read:
            collection_nodeid_string = read_value_id.NodeId.to_string()
            node_to_check = self.server.get_node(read_value_id.NodeId)
            node_class = node_to_check.get_node_class()
            node_description = node_to_check.get_description().to_string()
            
            if  node_class == ua.NodeClass.Object and node_description == "Redis Collection":
                components = node_to_check.get_children(refs=47)#if the object node does not have children, will not sync
                if collection_nodeid_string not in get_from_redis:
                    component_list = []
                    for component in components:   
                        component_list.append(component.nodeid.to_string())
                     
                    get_from_redis = component_list
        
        self.logger.debug(f"Nodes to get from redis:{get_from_redis}")
        
        return get_from_redis
        

    def assign_nodes_values(self, nodes_to_write):
        self.ua_manager.write(nodes_to_write)
        self.__reset_events()


    def __reset_events(self):
        self.nodes_to_sync = None
        self.sync = False
        self.sync_event.clear()
        self.logger.debug("Sync_event cleared")
        self.unpause_event.set()
        self.logger.debug("Unpause_event set")
        
    def get_nodes_to_sync(self):
        return self.nodes_to_sync