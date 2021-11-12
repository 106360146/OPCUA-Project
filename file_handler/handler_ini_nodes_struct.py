import configparser
import collections

import re
import env
from file_handler.struct_ini import StructINIConfig

#from plc DataType to opcua DataType
#datatypes identifiers
#https://python-opcua.readthedocs.io/en/latest/opcua.ua.html#opcua.ua.object_ids.ObjectIds.Float
plc2ua = {
    'int'  : 'Int16'   , #datatype=4
    'word' : 'Int16'   , #datatype=4
    'uint' : 'UInt16'  , #datatype=5
    'dint' : 'Int32'   , #datatype=6
    'udint': 'UInt32'  , #datatype=7
    'usint': 'UInt32'  , #datatype=7
    'real' : 'Float'   , #datatype=10
    'bool' : 'Boolean' , #datatype=1
    'dtl'  : 'DateTime', #datatype=13
    'dword': 'Int32'   , #datatype=6
    'lreal': 'Double'  , #datatype=11
}

namespace_info = {
   #index : uri/name
    'PNR OPC UA Server'   : '2'
}

def convert_type_plc_to_opcua(config):
    for key, value in config.items():
        ua_type = ''                  
        value = value.lower()
        
        ua_type = plc2ua[ value ]

        config[ key ] = ua_type

class HandlerININodes():

    def __init__(self, config_path, log_info):
        self.log_info    = log_info
        self.config_path = config_path
        self.logger      = log_info.init_class_logger( self.__class__.__name__ )
        self.sections    = collections.OrderedDict()

        fh = configparser.ConfigParser()
        fh.optionxform = str #set 'key' (node id's string identifier ) case sensitive
        fh.read( config_path )

        for section_name in fh:
            if section_name == 'DEFAULT':
                continue
            ini_nodes = StructINIConfig( self.config_path, self.log_info )
            for key, value in fh[section_name].items():
                ini_nodes.set_field(key, value)
            self.sections[ section_name ] = ini_nodes
    
    def init_section(self, section_name, config, namespace_uri, namespace_id, db_format):
        if isinstance( config, collections.OrderedDict ):
            
            ini_nodes = StructINIConfig( self.config_path, self.log_info )
            self.sections[ section_name ] = ini_nodes

            convert_type_plc_to_opcua( config )
            ini_nodes.set_field('db_format', db_format )

            for key, value in config.items():
                ini_nodes.set_field( key, value )

            ini_nodes.save_to_config_path( section_name )

        else:
            self.logger.warn(f"Incorrect type of config, should be '{collections.OrderedDict}'")
        
    def get_struct(self, section_name):
        config = self.sections[ section_name ].get_copied_config()
        rv = list()
        for key, value in config.items():
            rv.append([key, value])
        return rv