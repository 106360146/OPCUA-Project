import os, os.path

import env
from file_handler.handler_ini_connection     import HandlerINIConnection
from file_handler.handler_excel              import HandlerExcel
from file_handler.handler_ini_nodes_struct   import HandlerININodes
from file_handler.handler_ini_revision       import HandlerINIRevision
from file_handler.handler_ini_redisdb        import HandlerINIRedisDB
from file_handler.handler_ini_revision_cloud import HandlerINIRevisionCloud

from google_api.gdrive_api import GDrive_API

class HandlerMain():
    def __init__(self, log_info, reload_excel=False):
        self.log_info     = log_info
        self.logger       = log_info.init_class_logger( self.__class__.__name__ )
        self.reload_excel = reload_excel

        self.gdrive = GDrive_API( log_info )

        self.fh_conn                = HandlerINIConnection   ( env.conn_config_path    , log_info )
        self.ini_redisdb            = HandlerINIRedisDB      ( env.redisdb_info_path   , log_info )
        self.ini_nodes_struct       = HandlerININodes        ( env.node_struct_path    , log_info )
        self.ini_revision           = HandlerINIRevision     ( env.revision_info_path  , log_info )
        self.ini_cloud_rev          = HandlerINIRevisionCloud( env.cloud_rev_info_path , log_info )
        
        self.__export_db_format_from_gdrive()
        self.__reload_db_format()

    def __export_db_format_from_gdrive(self):
        try:
            section_name  = self.__get_file_name( env.excel_db_format_path )

            cloud_fileID  = self.ini_cloud_rev.get_fileId( section_name )
            last_modified = self.gdrive.get_spreadsheet_lastmodified( cloud_fileID )

            cloud_db_revised  = self.ini_cloud_rev.update_last_modified( section_name, last_modified )
            if cloud_db_revised:
                self.logger.info(f"Google Drive DB format modified, updating config.")
                self.ini_cloud_rev.overwrite_config()
                self.logger.info(f"Exporting it from Google drive.... ")
                self.gdrive.export_spreadsheet_as_excel( cloud_fileID, env.excel_db_format_path )

        except Exception as err:
            self.logger.warn(f"Google API err. msg: '{err}'")

    def __reload_db_format(self):
        section_name = self.__get_file_name( env.excel_db_format_path )
        revised_db_format = self.ini_revision.update_revision( section_name, env.excel_db_format_path )

        if self.reload_excel and os.path.exists( env.node_struct_path ):
            os.remove( env.node_struct_path )

        if revised_db_format or self.reload_excel:
            self.logger.info(f"DB format modified, updating table schema config ... ")
            self.ini_revision.overwrite_config()

            db_fmt_names = self.ini_redisdb.retrieve_names_db_format()
            fh_excel     = HandlerExcel( env.excel_db_format_path, self.log_info, db_fmt_names )

            #Write node structure
            coll_names = self.ini_redisdb.retrieve_coll_names()
            for cll_nm in coll_names:
                fmt_name     = self.ini_redisdb.retrieve_db_format_name( cll_nm )
                namespace_uri = self.ini_redisdb.retrieve_namespace_uri( cll_nm )
                namespace_id = self.ini_redisdb.retrieve_namespace_id( cll_nm )
                if fmt_name and namespace_uri:
                    db_format = fh_excel.get_db_format( fmt_name )
                    if db_format:
                        self.ini_nodes_struct.init_section( cll_nm, db_format, namespace_uri, namespace_id, fmt_name )
                    else:
                        self.logger.info(f"No variables selected from this Collection:{cll_nm}")
                else:
                    self.logger.warn(f"Empty extracted db format name: {cll_nm}")

    def __get_file_name(self, path):
        file_name = path.split('/')[-1]
        return file_name.split('.')[0] # truncate extension

    def get_ini_nodes_struct(self):
        return self.ini_nodes_struct
        
    def opcua_info(self):
        return self.fh_conn.get_opcua_conn_info()

    def redisdb_info(self):
        return self.fh_conn.get_redisdb_conn_info()
 