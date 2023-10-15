SERVICE_CONFIG = {
    "HO-AUTH": {
        "local": "http://mypt.local/mypt-ho-auth-api/",
        "staging": "http://mypt-ho-auth-api-staging/mypt-ho-auth-api/",
        "production": "http://mypt-ho-auth-api/mypt-ho-auth-api/",
        "permissions-to-tech-emp": {
            "func": "add-mypt-permissions-to-tech-emp",
            "method": "POST"
        }
    },
    "HO-PROFILE": {
        "local": "http://myptpdx-api-stag.fpt.net/mypt-ho-profile-api/",
        "staging": "http://mypt-ho-profile-api-staging/mypt-ho-profile-api/",
        "production": "http://mypt-ho-profile-api/mypt-ho-profile-api/",

        "get-parent-depart-from-branch": {
            "func": "get-parent-depart-from-branch",
            "method": "POST"
        },
        "email-from-emp-code": {
            "func": "email-from-emp-code",
            "method": "POST"
        },
        "email-list-from-emp-name": {
            "func": "email-list-from-emp-name",
            "method": "POST"
        },
        "emp-code-by-child-depart": {
            "func": "emp-code-by-child-depart",
            "method": "POST"
        },
        "get-emp-code-and-name-from-email": {
            "func": "get-emp-code-and-name-from-email",
            "method": "POST"
        },
        "filteration_condition": {
            "func": "filteration-condition",
            "method": "POST"
        }
    },
    "POWER-BI": {
        "local": "https://dashboard-api-stag.mypt.vn/",
        "staging": "https://dashboard-api-stag.mypt.vn/",
        "production": "https://dashboard-api.mypt.vn/",
        "user": {
            "email": "tinpnc.cdsmn@fpt.net",
            "password": "P@ssword01022022"
        },
        # "staging":"http://myptpdx-api-stag.fpt.net/mypt-ho-profile-api/",
        # "production":"http://myptpdx-api.fpt.net/mypt-ho-profile-api/",
        "giang_vien": {
            "func": "api/lecturers",
            "method": "POST"
        },
        "login": {
            "func": "api/login",
            "method": "POST"
        },
        "dao_tao": {
            "func": "api/education",
            "method": "POST"
        },
        "cong_tac": {
            "func": "api/business-trip",
            "method": "POST"
        }
    }
}
