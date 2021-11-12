import configparser
import collections
"""
FEATURES:
    - imitates iot_collection's "struct_ini.py"
    - main format of the INI file
"""
class StructINIConfig():
    def __init__(self, config_path, log_info):
        self.logger       = log_info.init_class_logger( self.__class__.__name__ )
        self.config_path  = config_path
        self.config       = collections.OrderedDict()
        self.section_name = ''

    def retrieve_section_name(self):
        return self.section_name

    def load_from_config_path(self, section_name, default_items):
        self.section_name = section_name

        fh = configparser.ConfigParser()
        fh.read( self.config_path )

        if section_name not in fh:
            self.logger.warn(f"Section name '{section_name}' not in config, use default config.")
            fh[section_name] = collections.OrderedDict()

        section = fh[section_name]
        for key, value in default_items:
            if key not in section:
                self.config[ key ] = value
                continue

            if isinstance(value, float):
                value = fh.getfloat( section_name, key )
            elif isinstance(value, int):
                value = fh.getint( section_name, key )
            elif isinstance(value, bool):
                value = fh.getboolean( section_name, key )
            elif isinstance(value, str):
                value = fh.get( section_name, key )
            else:
                raise ValueError(f"Unknown type of value: {type(value)}")

            self.config[ key ] = value

        self.logger.debug(f"config: {self.config}")

    def save_to_config_path(self, section_name):
        config = configparser.ConfigParser()
        config.optionxform = str # set 'key' case sensitive

        config.read( self.config_path )
        if section_name in config:
            config[ section_name ].clear()
        else:
            config[ section_name ] = collections.OrderedDict()

        for key, value in self.config.items():
            config[ section_name ][ key ] = value

        with open(self.config_path, 'w') as configfile:
            config.write( configfile )
     
    def get_field(self, field_name):
        return self.config[field_name]

    def set_field(self, field_name, value):
        self.config[field_name] = value

    def get_copied_config(self):
        return self.config.copy()
