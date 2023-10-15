SERVICE_CONFIG = {
    "profile-api":{
        "base_http_local": "http://mypt.local/mypt-ho-profile-api/",
        "base_http_dev": "http://mypt-ho-profile-api-dev/mypt-ho-profile-api/",
        "base_http_staging": "http://mypt-ho-profile-api-staging/mypt-ho-profile-api/",
        "base_http_production": "http://mypt-ho-profile-api/mypt-ho-profile-api/",
        "get_code": {
            "func" : "code-in-block",
            "method" : "POST"
        },
        "info_from_email" : {
            "func" : "info-from-email",
            "method" : "POST"
        },
        "get_user_profile_by_list_email" : {
            "func" : "get-user-profile-by-list-email",
            "method" : "POST"
        },
        "get_list_email_by_list_child_depart": {
            "func": "get-list-email-by-list-child-depart",
            "method": "POST"
        },
        "get_email_from_code_or_name": {
            "func": "get-email-from-code-or-name",
            "method": "POST"
        },
        "get_profile_and_user_permissions": {
            "func": "get-profile-and-user-permissions",
            "method": "POST"
        },
        "get_all_employee_email_list": {
            "func": "get-all-employee-email-list",
            "method": "GET"
        }
    },
    "NOTIFICATION":{
        "base_http_local": "http://myptpdx-api-stag.fpt.net/mypt-ho-notification-api/",
        "base_http_staging": "http://mypt-ho-notification-api-staging/mypt-ho-notification-api/",
        "base_http_production": "http://mypt-ho-notification-api/mypt-ho-notification-api/",
        "send_noti": {
            "func" : "send-one-noti",
            "method" : "POST"
        },
        "send-multi-noti-with-diff-content-by-email": {
            "func": "send-multi-noti-with-diff-content-by-email",
            "method" : "POST"
        }
    },
    "SETTING":{
        "base_http_local": "http://mypt.local/mypt-setting-api/v1/",
        "base_http_staging": "http://mypt-setting-api-staging/mypt-setting-api/v1/",
        "base_http_production": "http://mypt-setting-api/mypt-setting-api/v1/",
        "show_hide_tab": {
            "func" : "show-hide-user-home-tab",
            "method" : "POST"
        }
    }
}
