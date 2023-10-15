SERVICE_CONFIG = {
    'HO-AUTH': {
        'local': 'http://myptpdx-api-stag.fpt.net/mypt-ho-auth-api/',
        'staging': 'http://mypt-ho-auth-api-staging/mypt-ho-auth-api/',
        'production': 'http://mypt-ho-auth-api/mypt-ho-auth-api/',
        'add_ho_pers_and_fea_roles_for_emails': {
            'func': 'add-ho-pers-and-fea-roles-for-emails',
            'method': 'POST'
        },
        'add_user_permissions_by_email_mypt': {
            'func': 'add-user-permissions-by-email-mypt',
            'method': "POST"
        },
        'permissions-to-tech-emp': {
            'func': 'add-mypt-permissions-to-tech-emp',
            'method': 'POST'
        },
        'get-user-id-by-email': {
            'func': 'get-user-id-by-email',
            'method': 'POST'
        }
    },
    "HRIS": {
        "domain": {
            "local": "http://hrapi.fpt.vn",
            "staging": "http://hrapistag.fpt.vn",
            "production": "http://hrapi.fpt.vn"
        },
        "login": {
            "url": "/api/services/hub/Login",
            "method": "POST",
            "body": {
                "username": "mypt@hr.fpt.vn",
                "password": "!@#mYpt123"
            },
            "headers": {
                "Abp.TenantId": "1",
                'Content-Type': 'application/json'
            }
        },
        "get_list_employees": {
            "url": "/api/services/app/mypt/GetListEmployees",
            "method": "POST"
        },
        "get_list_employees_qualification": {
            "url": "/api/services/app/mypt/GetListEmployeesQualification",
            "method": "POST"
        },
        "get_list_employees_certificate": {
            "url": "/api/services/app/mypt/GetListEmployeesCertificate",
            "method": "POST"
        }
    }
}

