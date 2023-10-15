AES_SECRET_KEY = 'pnc3976myptcjmgp'

JWT_SECRET_KEY = "tin592ojcQzWr701PNCxbt"

ROUTES_PREFIX = "mypt-ho-auth-api/"

MIDDLEWARE_APPLIED_FOR_ROUTES = {
    "timeauthmiddleware": [
        "/" + ROUTES_PREFIX + "user-token"
    ],
    "authenusermiddleware": [
        "/" + ROUTES_PREFIX + "logout",
        "/" + ROUTES_PREFIX + "test-get-user-session",
        "/" + ROUTES_PREFIX + "get-all-permissions"
    ]
}

OAUTH_CLIENT_ID = "My_PT_HO"

EXPIRES_AT_ACCESS_TOKEN = 60
EXPIRES_AT_REFRESH_TOKEN = 43200

MYPT_HO_PROFILE_LOCAL_DOMAIN_NAME = "http://127.0.0.1:8002"
MYPT_HO_PROFILE_STAGING_DOMAIN_NAME = "http://mypt-ho-profile-api-staging"
MYPT_HO_PROFILE_PRODUCTION_DOMAIN_NAME = "http://mypt-ho-profile-api"

AZURE_CLIENT_ID = "d7962a93-e9ba-4614-868d-d65a2f5afb13"
AZURE_CLIENT_SECRET = "V-g8Q~WbrUjch3xszWOSLNs5IpYJQ5JEGpbRqduS"
