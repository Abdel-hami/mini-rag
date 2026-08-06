from enum import Enum

class ResponseSignal(Enum):
    FILE_VALIDATED_SUCCESSFULLY = "File validated successfully"
    FILE_NOT_VALIDATED = "File not validated"
    FILE_TYPE_NOT_SUPPORTED = "File type not supported"
    FILE_SIZE_EXCEEDED = "File size exceeded"
    FILE_UPLOADED_SUCCESSFULLY = "File uploaded successfully"
    FILE_NOT_UPLOADED = "File not uploaded"