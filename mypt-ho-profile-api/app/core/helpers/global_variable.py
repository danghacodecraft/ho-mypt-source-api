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
    URL_INFO_OCR = "http://mypt-ho-ocr-extraction-api/mypt-ho-ocr-extraction-api/extract_pdf"
    PUBLIC_URL = "https://apis.fpt.vn/"
    HO_CHECKIN_URL = "http://mypt-ho-checkin-api/"
    BOOTSTRAP_SERVER = "isc-kafka01:9092"
    TOPIC_LOG_KAFKA = "mypt-logs"
elif APP_ENV == "local":
    MEDIA_URL = "http://myptpdx-api-stag.fpt.net/"
    URL_INFO_OCR = "http://myptpdx-api-stag.fpt.net/mypt-ho-ocr-extraction-api/extract_pdf"
    PUBLIC_URL = "https://apis-stag.fpt.vn/"
    HO_CHECKIN_URL = "http://myptpdx-api-stag.fpt.net/"
    BOOTSTRAP_SERVER = "kafka-1:19092"
    TOPIC_KAFKA = "dev-mypt-logs"
else:
    MEDIA_URL = "http://mypt-ho-media-api-staging/"
    URL_INFO_OCR = "http://mypt-ho-ocr-extraction-api-staging/mypt-ho-ocr-extraction-api/extract_pdf"
    PUBLIC_URL = "https://apis-stag.fpt.vn/"
    HO_CHECKIN_URL = "http://mypt-ho-checkin-api-staging/"
    BOOTSTRAP_SERVER = "isc-kafka01:9092"
    TOPIC_KAFKA = "stag-mypt-logs"

    # MEDIA_URL = "http://127.0.0.1:8000/"

NAME_SERVICE_MEDIA = "mypt-ho-media-api/"
NAME_SERVIE_HO_CHECKIN = "mypt-ho-checkin-api/"

MESSAGE_API_ERROR_SYSTEM = "Lỗi hệ thống"
MESSAGE_API_ERROR_LOGIC = "Thất bại"

LIST_STATE_CARD = ["Còn hạn", "Sắp Hết Hạn", "Hết Hạn", "Chưa Cấp"]

DICT_KEY_LIST_SAFE_CARD = {
    "manager": {
        "parentDepart": "Vùng",
        "agency": "Đơn vị",
        "childDepart": "Bộ phận",

        "empCode": "Mã NV",
        "name": "Tên nhân viên",
        "jobTitle": "Vị trí công việc",
        "dateJoinCompany": "Ngày vào công ty",
        "sex": "Giới tính",
        "birthday": "Ngày sinh",
        "cmnd": "CMND/CCCD",
        "trainingGroup": "Nhóm đào tạo",
        "trainingStartDate":"Ngày bắt đầu đào tạo",
        "dateCertificate": "Ngày cấp thẻ ATLĐ",
        "expirationDate": "Ngày hết hạn ATLĐ",
        "numberCard": "Số thẻ",
        "statusCertificate": "Tình trạng thẻ/Chứng nhận",
        "certificate": "Cấp thẻ/Chứng nhận",
        "pictureCertificate": "Tên file hình ảnh/chứng nhận"

    },
    "hr": {
        "parentDepart": "Vùng",
        "agency": "Đơn vị",
        "childDepart": "Bộ phận",

        "empCode": "Mã NV",
        "name": "Tên nhân viên",
        "jobTitle": "Vị trí công việc",
        "trainingGroup": "Nhóm đào tạo",
        "trainingStartDate":"Ngày bắt đầu đào tạo",
        "dateCertificate": "Ngày cấp thẻ ATLĐ",
        "expirationDate": "Ngày hết hạn ATLĐ",
        "numberCard": "Số thẻ",
        "statusCertificate": "Tình trạng thẻ/Chứng nhận",
        "certificate": "Cấp thẻ/Chứng nhận",
        "pictureCertificate": "Tên file hình ảnh/chứng nhận"
    }
}


WORK_SAFE_IMPORT = {
    "empCode": "Mã nhân viên",
    "numberCard": "Số thẻ",
    # "jobTitle": "Vị trí công việc",
    "trainingGroup": "Nhóm đào tạo",
    "trainingStartDate": "Ngày bắt đầu đào tạo",
    "trainingEndDate": "Ngày kết thúc đào tạo",
    "dateCertificate": "Ngày cấp thẻ ATLĐ",
    "expirationDate": "Ngày hết hạn ATLĐ"
}

GROUP_TRAIN_WORK_SAFE = ["Nhóm 1", "Nhóm 2", "Nhóm 3", "Nhóm 4"]

DICT_CONVERT_TRAIN = {
                "parentDepart": "Vùng",
                "agency": "Đơn vị",
                "childDepart": "Bộ phận",
                "empCode": "Mã NV",
                "name": "Họ và tên",
                "jobTitle": "Vị trí công việc",
                "dateJoinCompany": "Ngày vào công ty",
                "sex": "Giới tính",
                "birthday": "Ngày sinh",
                "cmnd": "CMND/CCCD",
                "trainingGroup": "Nhóm đào tạo",
                "certificate": "Đối tượng cấp thẻ/Chứng nhận"
}

DATE_EXPORT_ATLD = 16


AVATAR_DEFAULT = {
    'male' : "https://apis.fpt.vn/mypt-ho-media-api/view-file?path=0125205881182526",
    'female' : "https://apis.fpt.vn/mypt-ho-media-api/view-file?path=0269357356197571"
}

MAX_ROW = 500