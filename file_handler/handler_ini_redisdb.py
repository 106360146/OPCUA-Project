import collections
import env

from file_handler.struct_ini  import  StructINIConfig
from file_handler.utility_ini import get_section_names
class StructINIRedisDB( StructINIConfig ):
    db_format     = 'db_format'
    namespace_id  = 'namespace_id'
    namespace_uri = 'namespace_uri'

    default_items = [
        [db_format , ''],
        [namespace_id, ''],
        [namespace_uri, ''],
    ]
    ########
    def __init__(self, config_path, log_info):
        self.log_info = log_info
        self.logger   = log_info.init_class_logger( self.__class__.__name__ )

        super().__init__( config_path, log_info )

    def load_section_from_config_path(self, section_name):
        self.section_name = section_name
        self.load_from_config_path( section_name, __class__.default_items )

    def get_column_format(self):
        return self.get_field(__class__.db_format)
    
    def get_namespace_id(self):
        return self.get_field(__class__.namespace_id)

    def get_namespace_uri(self):
        return self.get_field(__class__.namespace_uri)

class HandlerINIRedisDB():
    """
    INI config for mapping information between Redis and OPC UA
    """
    def retrieve_coll_names(self):
        return self.coll_names

    def retrieve_names_db_format(self):
        fmt_names = set()
        for name in self.db_format_name.values():
            if name:
                fmt_names.add( name )
        return fmt_names

    def __init__(self, config_path, log_info):
        self.config_path    = config_path
        self.logger         = log_info.init_class_logger( self.__class__.__name__ )
        self.sections       = collections.OrderedDict()
        self.section_names  = get_section_names( config_path )
        self.db_format_name = collections.OrderedDict()
        self.namespace_id   = collections.OrderedDict()
        self.namespace_uri  = collections.OrderedDict()
        self.extr_intervals = collections.OrderedDict()#not sure if needed
        self.coll_names     = list()
        
        for sec_name in self.section_names:
            ini_coll = StructINIRedisDB( config_path, log_info )
            ini_coll.load_section_from_config_path( sec_name )

            self.coll_names.append( sec_name )
            self.logger.debug(f"collection name: '{sec_name:35}'")

            self.sections      [ sec_name ] = ini_coll
            self.db_format_name[ sec_name ] = ini_coll.get_column_format()
            self.namespace_id  [ sec_name ] = ini_coll.get_namespace_id()
            self.namespace_uri [ sec_name ] = ini_coll.get_namespace_uri()

    def retrieve_db_format_name(self, section_name):
        return self.db_format_name[ section_name ]
    
    def retrieve_namespace_id(self, section_name):
        return self.namespace_id[ section_name ]

    def retrieve_namespace_uri(self, section_name):
        return self.namespace_uri[ section_name ]

    def retrieve_extracted_intervals(self):
        return self.extr_intervals

    def retrieve_section_names(self):
        return self.section_names