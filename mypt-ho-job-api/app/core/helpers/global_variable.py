from decouple import config

STATUS_CODE_ERROR_LOGIC = 4
STATUS_CODE_NO_DATA = 6
STATUS_CODE_SUCCESS = 1
STATUS_CODE_INVALID_INPUT = 5
STATUS_CODE_FAILED = 0
STATUS_CODE_ERROR_SYSTEM = 4

MESSAGE_API_SUCCESS = "Thành công"
MESSAGE_API_FAILED = "Thất bại"
MESSAGE_API_NO_DATA = "Không có thông tin"
MESSAGE_API_NO_INPUT = "Vui lòng nhập đầy đủ thông tin"

MESSAGE_API_ERROR_SYSTEM = "Lỗi hệ thống"
MESSAGE_API_ERROR_LOGIC = "Thất bại"

APP_ENV = config("APP_ENV")
if APP_ENV == "production":
    MEDIA_URL = "http://mypt-ho-media-api/"
else:
    MEDIA_URL = "http://mypt-ho-media-api-staging/"
    # MEDIA_URL = "http://127.0.0.1:8000/"

NAME_SERVICE_MEDIA = "mypt-ho-media-api/"

MESSAGE_API_ERROR_SYSTEM = "Lỗi hệ thống"
MESSAGE_API_ERROR_LOGIC = "Thất bại"

DATETIME_FORMATED = ['%Y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M', '%Y-%m-%d', '%m/%d/%Y %H:%M:%S', '%m/%d/%Y %H:%M',
                     '%m/%d/%Y', '%m/%d/%y %H:%M:%S', '%m/%d/%y %H:%M', '%m/%d/%y']
DATETIME_Y_m_d = ['%Y-%m-%d %H:%M:%S']
YEAR_month_day = ['%Y-%m-%d']
month_day_YEAR = ['%d/%m/%Y']

FORMAT_DATE_DEFAULT = "%d/%m/%Y"
FORMAT_DATETIME_DEFAULT = "%d/%m/%Y %H:%M:%S"
