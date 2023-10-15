from django.urls import path
from .http.views.health_view import *
from .http.views.login_view import *
from .http.views.token_view import *
from .http.views.permission_view import *
from .http.views.permission_tools_view import *
from .http.views.user_infos_view import *


urlpatterns = [
    path('health', HealthView.as_view({'get':'health'})),
    path('show-login', LoginView.as_view({'get':'showLogin'})),
    path('azure-login', LoginView.as_view({'get':'showAzureLogin'})),
    path('gen-user-token-by-code', LoginView.as_view({'post':'genUserTokenByCode'})),
    path('gen-user-token-by-azure-code', LoginView.as_view({'post':'genUserTokenByAzureCode'})),
    path('user-token', TokenView.as_view({'post':'genUserToken'})),
    path('logout', LoginView.as_view({'post':'doLogout'})),
    path('gen-logginned-user-token', LoginView.as_view({'post':'genLogginedUserToken'})),
    path('test-permission', LoginView.as_view({'post':'testPermission'})),
    path('get-all-permissions', HoPermissionView.as_view({'post': 'getAllPermissions'})),
    path('save-permission-route-to-redis', HoPermissionView.as_view({'post': 'savePermissionWithRouteToRedis'})),
    path('get-permission-route-from-redis', HoPermissionView.as_view({'post': 'getPermissionWithRouteFromRedis'})),
    path('test-get-user-session', LoginView.as_view({'post': 'testGetUserSession'})),

    path('get-all-permissions-ho', HoPermissionToolsView.as_view({'post': 'getAllPermissionsHO'})),
    path('get-all-permission-groups-ho', HoPermissionToolsView.as_view({'post': 'getAllPermissionGroupsHO'})),
    path('get-all-permissions-by-group-code-ho', HoPermissionToolsView.as_view({'post': 'getPermissionsByGroupCodeHO'})),
    path('get-logged-in-user-permissions-ho', HoPermissionToolsView.as_view({'post': 'getLoggedInUserPermissionsHO'})),
    path('get-allowed-assign-permissions-web-ho', HoPermissionToolsView.as_view({'post': 'getAllowedAssignPermissionsWebHo'})),
    path('add-user-permissions-by-email-ho', HoPermissionToolsView.as_view({'post': 'addUserPermissionsByEmailHO'})),
    path('add-user-permissions-by-email-mypt', HoPermissionToolsView.as_view({'post': 'addUserPermissionsByEmailAppMyPT'})),
    path('update-one-child-depart-user-permission-ho', HoPermissionToolsView.as_view({'post': 'updateOneChildDepartUserPermissionHO'})),
    path('delete-one-user-permission-ho', HoPermissionToolsView.as_view({'post': 'deleteOneUserPermissionHO'})),

    path('add-mypt-permissions-to-tech-emp', HoPermissionToolsView.as_view({'post': 'addMyPTPermissionsToTechEmp'})),

    path('add-ho-pers-and-fea-roles-for-emails', HoPermissionToolsView.as_view({'post': 'addHoPersAndFeaRolesForEmails'})),

    path('save-employee', UserInfosView.as_view({'post': 'saveEmployee'})),
    path('add-all-permissions-web-ho', UserInfosView.as_view({'post': 'addAllPermissionsWebHO'})),
    path('add-all-permissions-app-mypt', UserInfosView.as_view({'post': 'addAllPermissionsAppMyPT'}))
]
