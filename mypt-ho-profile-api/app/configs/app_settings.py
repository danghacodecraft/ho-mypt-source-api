AES_SECRET_KEY = 'pnc3976myptcjmgp'

JWT_SECRET_KEY = "tin592ojcQzWr701PNCxbt"

SERVICE_NAME = "mypt-ho-profile-api"

ROUTES_PREFIX = "mypt-ho-profile-api/"

MIDDLEWARE_APPLIED_FOR_ROUTES = {
    "authenusermiddleware": [
        "/" + ROUTES_PREFIX + "profile-and-user-permissions",
        "/" + ROUTES_PREFIX + "check-emp-rank",
        "/" + ROUTES_PREFIX + 'import-employee',
        "/" + ROUTES_PREFIX + 'emp-rank',
        "/" + ROUTES_PREFIX + 'import-rank',
        "/" + ROUTES_PREFIX + 'edit-rank',
        "/" + ROUTES_PREFIX + 'check-permission-import-rank',
        "/" + ROUTES_PREFIX + 'safe-card-info',
        "/" + ROUTES_PREFIX + 'add-safe-card',
        "/" + ROUTES_PREFIX + 'import-safe-card',
        "/" + ROUTES_PREFIX + "email-in-block",
        "/" + ROUTES_PREFIX + "emp-in-block",
        "/" + ROUTES_PREFIX + "edit-employee",

        "/" + ROUTES_PREFIX + "get-contracts-type",
        "/" + ROUTES_PREFIX + "delete-contracts-type-from-redis",
        "/" + ROUTES_PREFIX + "update-status-working",
        "/" + ROUTES_PREFIX + "update-department",
        "/" + ROUTES_PREFIX + "update-order-department",
        "/" + ROUTES_PREFIX + "get-child-departs-from-parent-depart",
        "/" + ROUTES_PREFIX + "emp-info",
        "/" + ROUTES_PREFIX + "email-is-ptq",
        "/" + ROUTES_PREFIX + "get-child-depart",
        "/" + ROUTES_PREFIX + "check-import-rank",

        "/" + ROUTES_PREFIX + "info-list-train",
        "/" + ROUTES_PREFIX + "info-state-work-safe-card",
        "/" + ROUTES_PREFIX + "info-histories-state-work-safe-card",
        "/" + ROUTES_PREFIX + "export-for-state-card",
        "/" + ROUTES_PREFIX + "export-info-histories-work-safe-state-card",
        "/" + ROUTES_PREFIX + "export-list-train",
        "/" + ROUTES_PREFIX + "delete-info-work-safe-card",
        "/" + ROUTES_PREFIX + "edit-info-work-safe-card",
        "/" + ROUTES_PREFIX + "add-info-work-safe-card",
        "/" + ROUTES_PREFIX + "import-info-work-safe-card",
        "/" + ROUTES_PREFIX + "check-input-import-info-work-safe-card",
        "/" + ROUTES_PREFIX + "get-detail-info-emp",
        "/" + ROUTES_PREFIX + "info-from-ocr",
        '/' + ROUTES_PREFIX + "check-img-from-ocr",

        "/" + ROUTES_PREFIX + "get-map-coordinate",

        "/" + ROUTES_PREFIX + "sync-specified-employee-data"


    ],
    "userpermissionmiddleware": [
        "/" + ROUTES_PREFIX + "check-emp-rank",
        "/" + ROUTES_PREFIX + 'import-account',
        "/" + ROUTES_PREFIX + 'import-employee',
        "/" + ROUTES_PREFIX + 'emp-rank',
        "/" + ROUTES_PREFIX + 'import-rank',
        "/" + ROUTES_PREFIX + 'edit-rank',
        "/" + ROUTES_PREFIX + 'safe-card-info',
        "/" + ROUTES_PREFIX + 'add-safe-card',
        "/" + ROUTES_PREFIX + 'import-safe-card',
        "/" + ROUTES_PREFIX + "email-in-block",
        "/" + ROUTES_PREFIX + "emp-in-block",
        "/" + ROUTES_PREFIX + "edit-employee",
        "/" + ROUTES_PREFIX + "emp-info",
        "/" + ROUTES_PREFIX + "get-child-depart",
        "/" + ROUTES_PREFIX + "check-import-rank",

        "/" + ROUTES_PREFIX + "delete-info-work-safe-card",
        "/" + ROUTES_PREFIX + "add-info-work-safe-card",
        "/" + ROUTES_PREFIX + "sync-specified-employee-data"
    ]
}

EMPLOYEE_CONTRACT_TYPES = {
    "new": [
        "hợp đồng đào tạo nghề",
        "hợp đồng thử việc",
        "hđ đào tạo nghề",
        "hđ thử việc",
        "thử việc"
    ],
    'office': [

    ]
}
