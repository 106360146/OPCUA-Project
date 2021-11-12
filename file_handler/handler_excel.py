import pandas as pd
import ipaddress
import collections

class HandlerExcel():
    column_key       = 'name'
    column_value     = 'type'
    column_sql_req   = 'sql require'
    column_opcua     = 'opcua'
    column_extracted = 'extracted'
    column_valid     = 'valid keys'
    column_names     = { \
        column_valid, column_sql_req, column_key, \
        column_value, column_opcua  , column_extracted, \
    }

    def __init__(self, excel_path, log_info, sheet_names):
        self.log_info = log_info
        self.logger = log_info.init_class_logger( self.__class__.__name__ )
        
        self.sheet_names = sheet_names
        self.excel_path = excel_path

        sheets = pd.read_excel(self.excel_path, sheet_name=None, skiprows=2, nrows =250, engine='openpyxl')
        self.__remove_sheets    ( sheets )
        self.__lowercase_columns( sheets )
        self.__remove_nan       ( sheets )
        self.__drop_columns     ( sheets, __class__.column_names )
        self.__drop_rows        ( sheets,  __class__.column_valid, __class__.column_opcua )
        
        ckey = __class__.column_key
        cval = __class__.column_value
        self.db_formats = self.__to_ordered_dict( sheets, key=ckey, value=cval )

    def __remove_sheets(self, sheets):
        '''
            remove categories not defined in 'sheet_allowed'
        '''
        to_be_removed = list()
        for sheet_name in sheets:
            name = sheet_name.lower().strip()
            if name not in self.sheet_names:
                to_be_removed.append( sheet_name )

        for name in to_be_removed:
            self.logger.debug(f"sheet to be removed: '{name}'")
            del sheets[ name ]

    def __lowercase_columns(self, sheets):
        '''
            Rename the name of columns as lower cases amd replace space with _.
        '''
        for sheet_name in sheets:
            to_be_renamed = dict()
            for col_name in sheets[ sheet_name ].keys():
                to_be_renamed[ col_name ] = col_name.lower()

            for key, value in to_be_renamed.items():
                sheets[ sheet_name ].rename(columns={key: value}, inplace=True)

    def __remove_nan(self, sheets):
        for sheet_name in sheets:
            sheets[ sheet_name ].fillna('', inplace=True)

    def __drop_columns(self, sheets, valid_columns):
        for sheet_name in sheets:
            to_be_dropped = list()
            for col_name in sheets[ sheet_name ].keys():
                if col_name.lower() not in valid_columns:
                    to_be_dropped.append( col_name )

            # axis=1 means column, axis=0 indicates rows to be used
            # inplace=True, remove the columns in sheets
            sheets[ sheet_name ].drop( to_be_dropped, axis=1, inplace=True )

    def __drop_rows(self, sheets, base_column, subset_column):
        '''
            Drop rows that don't have a valid type
        '''
        for sheet_name in sheets:
            nrows = self.__get_nrow( sheets, sheet_name )
            to_be_dropped = list()
            for idx in range(nrows):
                row = sheets[ sheet_name ].iloc[idx,:]
                if not (row[ base_column ] and row[ subset_column ]):
                    to_be_dropped.append( idx )

            sheets[ sheet_name ].drop( to_be_dropped, axis=0, inplace=True )

    def __to_ordered_dict(self, sheets, key, value ):

        db_formats = collections.OrderedDict()
        for sheet_name in sheets:

            sht_name = sheet_name.lower().strip()
            db_formats[ sht_name ] = collections.OrderedDict()

            nrows = self.__get_nrow( sheets, sheet_name )
            for idx in range(nrows):
                row = sheets[ sheet_name ].iloc[idx,:]
                db_formats[ sht_name ][ row[key] ] = row[value].lower()

        return db_formats

    def get_db_format(self, sheet_name):
        return self.db_formats[ sheet_name ].copy()

    def __get_nrow(self, sheets, sheet_name):
        if sheet_name in sheets:
            return sheets[ sheet_name ].shape[0]
        else:
            return 0