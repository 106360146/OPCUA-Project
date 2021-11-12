import configparser

import opcua
from opcua import ua
from opcua.common.xmlimporter import XmlImporter

from ua_system.ua_config_parser import UAConfigParser
"""
In the future we can use several INI files to describe one excell file
That way, we can include other attributes such as references
"""

class ConfigImporter(XmlImporter):
    """
    Imports into OPCUA the nodes already parsed by the UAConfigParser from INI Files
    """
    def __init__(self, server, namespace_id, log_info):
        super().__init__(server)
        self.log_info = log_info
        self.logger      = log_info.init_class_logger( self.__class__.__name__ )
        self.server = server
        self.parser = None
        self.namespace_id = namespace_id
        self.namespaces = {}
           
    def import_config(self, config_path=None):
        """
        import config and return added nodes
        """
        self.logger.debug(f"Importing INI config {config_path}")
        self.parser = UAConfigParser(config_path, self.namespace_id, self.log_info)
        self.namespaces = self._map_namespaces(self.parser.get_used_namespaces())
        self.refs = []

        dnodes = self.parser.get_nodes_data()
        dnodes = self.make_objects(dnodes)
        nodes_parsed = self._sort_nodes_by_parentid(dnodes)

        nodes = []
        for nodedata in nodes_parsed: 
            try:
                node = self._add_node_data(nodedata)    
            except Exception:
                self.logger.warning(f"failure adding node nodeid:{nodedata.nodeid}, parent:{nodedata.parent}")
                raise
            nodes.append(node)

        self.refs, remaining_refs = [], self.refs
        self._add_references(remaining_refs)
        if len(self.refs) != 0:
            self.logger.warning("The following references could not be imported and are probaly broken: %s", self.refs) 

        return nodes