from decouple import config

APP_ENV = config("APP_ENV")


FORMAT_DATE_DEFAULT = "%d/%m/%Y"
FORMAT_DATETIME_DEFAULT = "%d/%m/%Y %H:%M:%S"

if APP_ENV == "production":
    VIEW_FILE_AUTH_PUBLIC = "https://apis.fpt.vn/mypt-media-api/v1/view-file-auth?path="
else:
    VIEW_FILE_AUTH_PUBLIC = "https://apis-stag.fpt.vn/mypt-media-api/v1/view-file-auth?path="

