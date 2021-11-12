from file_handler.struct_ini import StructINIConfig

"""
FEATURES:
    - imitates iot_collection's "handler_ini_connection.py"
    - initiation of OPC UA connection
"""

class StructINIOpcua( StructINIConfig ):
    
    section_name  = 'opcua'
    default_items = [
        ['name', 'PNR OPC UA Server'],
        ['endpoint' ,'opc.tcp://10.101.100.49:4840'],
        ['namespace_id', '2'],
    ]
    
    def __init__(self, config_path, log_info):
        super().__init__( config_path, log_info )
        self.load_from_config_path(__class__.section_name, __class__.default_items)

    def get_endpoint(self):
        return self.get_field('endpoint')
    
    def get_name(self):
        return self.get_field('name')
    
    def get_namespace_id(self):
        return self.get_field('namespace_id')

class StructINIRedisDB( StructINIConfig ):
    # field 1: item name,
    # feild 2: default value if not found
    section_name  = 'redis'
    default_items = [
        ['pass', ''          ],
        ['port', 6379        ],
        ['host', '127.0.0.1' ],
    ]
    def __init__(self, config_path, log_info):
        super().__init__( config_path, log_info )
        self.load_from_config_path( __class__.section_name, __class__.default_items )

    def get_password(self):
        return self.get_field('pass')

    def get_host(self):
        return self.get_field('host')

    def get_port(self):
        return self.get_field('port')

class HandlerINIConnection():
    
    def __init__( self, config_path, log_info ):
        self.opcua   = StructINIOpcua( config_path, log_info )
        self.redisdb = StructINIRedisDB( config_path, log_info )
    
    def get_opcua_conn_info(self):
        return self.opcua
    
    def get_redisdb_conn_info(self):
        return self.redisdb