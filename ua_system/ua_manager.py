from opcua import ua
import collections

class UAManager():
    """
     Usefull Low-Level OPCUA services' implementations for an
     OPCUA SERVER
    """
    def __init__(self, uaserver, log_info):
        self.log_info = log_info
        self.server = uaserver
        
    #this method is for the client
    def browse_below_node(self, node_id):
        main_node = self.server.get_node( node_id )
        attributes = main_node.get_children_descriptions()
        if attributes:
            node_list = list()
            for list_element in attributes:
                new_ID = list_element.NodeId.to_string()
                node_list.append(new_ID)
                
                self.__browse_below_node( new_ID )
            return node_list
        
        else:
            self.logger.info(f"No child nodes below node { node_id }")

    def read(self, nodes_to_read):
        params = ua.ReadParameters()
        for node_id_str in nodes_to_read:
            nodeid = ua.NodeId.from_string( node_id_str )
            attr = ua.ReadValueId()
            attr.NodeId = nodeid
            attr.AttributeId = ua.AttributeIds.Value
            params.NodesToRead.append( attr )
        result =  self.server.iserver.isession.read( params )
        #For client:
        #result = result = client.uaclient.read(params)
        return result

    def write(self, nodes_to_write):
        if isinstance(nodes_to_write, (collections.OrderedDict, dict)):
            params = ua.WriteParameters()
            for node_id_str, value in nodes_to_write.items():
                node_id = ua.NodeId.from_string(node_id_str)
                attr = ua.WriteValue()
                attr.NodeId = node_id
                attr.AttributeId = ua.AttributeIds.Value
                attr.Value = ua.DataValue(ua.Variant(value))
                params.NodesToWrite.append(attr)
            result = self.server.iserver.isession.write(params)
            #For client:
            #result = result = client.uaclient.write(params)
        return result

    def browse(self, node_id):
        main_node = self.server.get_node( node_id )
        object_children = main_node.get_children()
        
        params = ua.BrowseParameters()
        for node_id in object_children:
            attr = ua.BrowseDescription()
            attr.NodeId = node_id
            params.NodesToBrowse.append(attr)

        result = self.server.iserver.issesion.browse(params)
        #For client:
        #result = result = client.uaclient.browse(params)

        return result
    
