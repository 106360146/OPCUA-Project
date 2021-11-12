import hashlib
import configparser
from datetime import datetime
from collections import OrderedDict

import env

class HandlerINIRevisionCloud():

    def __init__(self, config_path, log_info):
        self.config_path = config_path
        self.logger = log_info.init_class_logger( self.__class__.__name__ )

        self.config = configparser.ConfigParser()
        self.config.read( config_path )

    def set_last_modified(self, section_name, last_modified):
        self.config[section_name]['last_modified'] = str(last_modified)

    def get_last_modified(self, section_name):
        dtime = f"{self.config[section_name]['last_modified']}"
        if dtime:
            return datetime.strptime(dtime, "%Y-%m-%d %H:%M:%S.%f")
        else:
            return None

    def set_fileId(self, section_name, fileId):
        self.config[section_name]['fileid'] = fileId

    def get_fileId(self, section_name):
        return self.config[section_name]['fileid']

    def update_last_modified(self, section_name, last_modified):
        prev_last_modified = self.get_last_modified( section_name )
        if prev_last_modified and prev_last_modified == last_modified:
            return False

        self.set_last_modified( section_name, last_modified )
        return True

    def overwrite_config(self):
        with open( self.config_path, 'w') as fptr:
            self.config.write( fptr )