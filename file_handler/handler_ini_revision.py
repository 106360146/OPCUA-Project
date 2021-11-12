import hashlib
import configparser
from datetime import datetime
from collections import OrderedDict

import env

def calculate_file_md5(to_be_hashed):
    m = hashlib.md5()
    with open(to_be_hashed, "rb") as fptr:
        buf = fptr.read()
        m.update(buf)

    return m.hexdigest()


class HandlerINIRevision():

    def __init__(self, config_path, log_info):
        self.config_path = config_path
        self.logger      = log_info.init_class_logger( self.__class__.__name__ )

        self.config = configparser.ConfigParser()
        self.config.read( config_path )

    def __set_md5(self, section_name, md5):
        self.config[ section_name ]['md5'] = md5

    def __get_md5(self, section_name):
        return self.config[section_name].get('md5', '')

    def __set_datetime(self, section_name):
        self.config[section_name]['last_modified'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def __set_path(self, section_name, path):
        self.config[section_name]['path'] = path

    def __clear_section(self, section_name):
        del self.config[ section_name ]
        self.config[ section_name ] = OrderedDict()

    def update_revision(self, section_name, path):
        if section_name not in self.config:
            self.config[ section_name ] = OrderedDict()

        prev_md5 = self.__get_md5( section_name )
        calculated_md5 = calculate_file_md5( path )
        if calculated_md5 == prev_md5:
            return False

        self.logger.info(f"File '{path}' updated")
        self.__clear_section( section_name )
        self.__set_md5      ( section_name, calculated_md5 )
        self.__set_path     ( section_name, path )
        self.__set_datetime ( section_name )

        return True
        
    def overwrite_config(self):
        with open( self.config_path, 'w') as fptr:
            self.config.write( fptr )