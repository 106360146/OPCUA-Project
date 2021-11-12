import configparser
import collections
from os import name
from opcua.common.xmlparser import RefStruct, XMLParser
from opcua.ua.uaprotocol_auto import ReferenceTypeAttributes
import opcua
from opcua import ua
from opcua.ua.object_ids import ObjectIds
"""
    OBSERVATION: should consider adding _parse_attr in the future
"""

class NodeData():
    def __init__(self):
        """
        Only using nodetype, nodeid, browsename, displayname, parent, datatype
        """
        self.nodetype = None
        self.nodeid = None
        self.browsename = None
        self.displayname = None
        #self.symname = None  # FIXME: this param is never used, why?
        self.parent = None
        self.parentlink = None
        self.desc = ""
        self.typedef = None
        self.refs = []
        self.nodeclass = None
        self.eventnotifier = 0

        # variable
        self.datatype = None
        self.rank = -1  # check default value
        self.value = None
        self.valuetype = None
        self.dimensions = None
        self.accesslevel = None
        self.useraccesslevel = None
        self.minsample = None

        # referencetype
        self.inversename = ""
        self.abstract = False
        self.symmetric = False

        # datatype
        self.definition = []

        def __str__(self):
            return f"NodeData(nodeid:{self.nodeid})"
        __repr__ = __str__

class UAConfigParser(XMLParser):
    """
    TODO: check opcua's xmlparser in the future to see if it is
          convenient to implement another of its methods
    """

    def __init__(self, config_path, namespace_id, log_info):
        self.log_info = log_info
        self.logger = log_info.init_class_logger( self.__class__.__name__ )
        self.config_path = config_path
        self.parser = configparser.ConfigParser()
        self.parser.read(self.config_path)
        self.namespace_id = namespace_id
        self.ns = {}
        #{st_20033-40_smbplc.main:PNR OPC UA Server}
        
    def get_used_namespaces(self):
        """
        Return the used namespace uris 
        from this INI file
        """
        namespaces_uris = list()

        for key, value in self.ns.items():
            if value in namespaces_uris:
                continue
            else:
                namespaces_uris.append(value)

        return namespaces_uris
        
    def get_nodes_data(self):
        nodes = []
        for section_name in self.parser:
             #different sections may use different namespaces
            if section_name == 'DEFAULT':
                continue
            
            object_node = self._set_attr( "UAObject", self.namespace_id, section_name )
            nodes.append( object_node )
            prnt_nd_nm = section_name

            for key, value in self.parser[section_name].items():

                if key not in ['db_format']:
                    variable_node = self._set_attr("UAVariable", self.namespace_id, value, key, parent_node=prnt_nd_nm)
                    nodes.append( variable_node )
        
        return nodes
        
    def _set_attr(self, nodetype, current_namespace, value, key=None, parent_node=None):
        """
        Combination of xmlparser's __parse_attr and_set_attr 
        """
        obj = NodeData()
        obj.nodetype = nodetype
        info = value
        
        if obj.nodetype == "UAObject": 
            obj.nodeid      = f"ns={current_namespace};s={info}"
            obj.browsename = f"{current_namespace}:s={info}"
            obj.parent     = "ns=2;i=1"#Main_Folder
            obj.desc       = "Redis Collection"
            obj.datatype   = None
            refs           = [{"target":"i=58", "reftype":"HasTypeDefinition"},{"IsForward":False, "target":obj.parent,\
                             "reftype":"Organizes"}]
            
    
        else:
            obj.nodeid     = f"ns={current_namespace};s={parent_node}.{key}"
            obj.browsename = f"{current_namespace}:{parent_node}.{key}"
            obj.parent     = f"ns={current_namespace};s={parent_node}"
            obj.desc       = "Redis Variable"
            obj.datatype   = value
            refs           = [{"target":"i=61", "reftype":"HasTypeDefinition"},{"IsForward":False, "target":obj.parent,\
                             "reftype":"HasComponent"}]
            
        self.logger.debug(f"node_object_fresh: {obj.nodeid} {obj.parent}")
        obj.displayname = obj.browsename # give a default value to display name
        obj.refs = self._parse_refs(refs, obj )

        return obj
        
    def _parse_refs(self, refs, obj):
        parent, parentlink = obj.parent, None

        for ref in refs:
            struct = RefStruct()
            for key, value in ref.items():
                if key == "IsForward":
                    struct.forward = value
                
                if key == "target":
                    struct.target = value

                if key == "reftype":
                    if value == "HasTypeDefinition":
                        struct.reftype = value
                        obj.typedef = struct.target
                    else:
                        struct.reftype = value
            obj.refs.append(struct)

        if not struct.forward:
            parent, parentlink = struct.target, struct.reftype
            if obj.parent == parent:
                obj.parentlink = parentlink

        if not obj.parent or not obj.parentlink:
            obj.parent, obj.parentlink = parent, parentlink
            self.logger.info("Could not detect backward reference to parent for node '%s'", obj.nodeid)