from datetime import datetime

from google_api import Create_Service

class GDrive_API():
    # If modifying these scopes, delete the file token.pickle.
    SCOPES = ['https://www.googleapis.com/auth/drive']

    def __init__(self, log_info):
        self.logger = log_info.init_class_logger( self.__class__.__name__ )
        self.service = Create_Service(self.__class__.__name__, 'drive', 'v3', __class__.SCOPES)
        self.file_service = self.service.files()

    def export_spreadsheet_as_excel(self, fileID, dest_path):
        byteData = self.file_service.export_media(
            fileId   = fileID,
            mimeType = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ).execute()

        with open( dest_path, 'wb' ) as fptr:
            fptr.write(byteData)

    def get_spreadsheet_lastmodified(self, fileID):
        data = self.file_service.get(fileId=fileID, fields='modifiedTime').execute()
        return datetime.strptime(data["modifiedTime"], "%Y-%m-%dT%H:%M:%S.%fZ")
