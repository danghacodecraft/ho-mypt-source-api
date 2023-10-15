AES_SECRET_KEY = 'pnc3976myptcjmgp'

SALARY_SECRET_KEY = 'dPFH6xlrOoHoSL5B'

JWT_SECRET_KEY = "tin592ojcQzWr701PNCxbt"

SERVICE_NAME = "mypt-ho-job-api"

ROUTES_PREFIX = "mypt-ho-job-api/"

MIDDLEWARE_APPLIED_FOR_ROUTES = {
    "authenusermiddleware": [
        "/" + ROUTES_PREFIX + "profile-and-user-permissions",
        "/" + ROUTES_PREFIX + "check-emp-rank",
        "/" + ROUTES_PREFIX + 'account-info',
        "/" + ROUTES_PREFIX + 'import-account',
        "/" + ROUTES_PREFIX + 'import-employee',
        "/" + ROUTES_PREFIX + 'add-account',
        "/" + ROUTES_PREFIX + 'edit-account',
        "/" + ROUTES_PREFIX + 'salary',
        "/" + ROUTES_PREFIX + 'emp-rank',
        "/" + ROUTES_PREFIX + 'import-rank',
        "/" + ROUTES_PREFIX + 'import-salary',
        "/" + ROUTES_PREFIX + 'safe-card-info',
        "/" + ROUTES_PREFIX + 'add-safe-card',
        "/" + ROUTES_PREFIX + 'import-safe-card',
        "/" + ROUTES_PREFIX + "email-in-block",
        "/" + ROUTES_PREFIX + "emp-in-block",
        "/" + ROUTES_PREFIX + "edit-employee",
        "/" + ROUTES_PREFIX + "emp-info",
        "/" + ROUTES_PREFIX + "email-is-ptq",
        "/" + ROUTES_PREFIX + "get-child-depart",
        "/" + ROUTES_PREFIX + "show-working-schedule",
        "/" + ROUTES_PREFIX + "import-working-schedule",
        "/" + ROUTES_PREFIX + "export-working-schedule",
        "/" + ROUTES_PREFIX + 'salary',
        "/" + ROUTES_PREFIX + 'import-salary',
        "/" + ROUTES_PREFIX + 'import-education',
        "/" + ROUTES_PREFIX + 'show-education'
    ],
    "userpermissionmiddleware": [
        "/" + ROUTES_PREFIX + "check-emp-rank",
        "/" + ROUTES_PREFIX + 'account-info',
        "/" + ROUTES_PREFIX + 'import-account',
        "/" + ROUTES_PREFIX + 'import-employee',
        "/" + ROUTES_PREFIX + 'add-account',
        "/" + ROUTES_PREFIX + 'edit-account',
        "/" + ROUTES_PREFIX + 'salary',
        "/" + ROUTES_PREFIX + 'emp-rank',
        "/" + ROUTES_PREFIX + 'import-rank',
        "/" + ROUTES_PREFIX + 'import-salary',
        "/" + ROUTES_PREFIX + 'safe-card-info',
        "/" + ROUTES_PREFIX + 'add-safe-card',
        "/" + ROUTES_PREFIX + 'import-safe-card',
        "/" + ROUTES_PREFIX + "email-in-block",
        "/" + ROUTES_PREFIX + "emp-in-block",
        "/" + ROUTES_PREFIX + "edit-employee",
        "/" + ROUTES_PREFIX + "emp-info",
        "/" + ROUTES_PREFIX + "get-child-depart",
        "/" + ROUTES_PREFIX + "show-working-schedule",
        "/" + ROUTES_PREFIX + "import-working-schedule",
        "/" + ROUTES_PREFIX + "export-working-schedule",
        "/" + ROUTES_PREFIX + 'salary',
        "/" + ROUTES_PREFIX + 'import-salary',
        "/" + ROUTES_PREFIX + 'import-education',
        "/" + ROUTES_PREFIX + 'show-education'
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
