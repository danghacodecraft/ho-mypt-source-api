from django.urls import path

from ..http.views.configs_view import ConfigView
from ..http.views.health_view import *
from ..http.views.hr_view import *
from ..http.views.ptq_view import *
from ..http.views.profile_view import *
from ..http.views.department_view import DepartmentView
from ..http.views.work_safe_card_view import *
from ..http.views.technical_support.technical_support_view import *
from ..http.views.workday.workday_view import *
from ..http.views.workday.info_checkin_view import *
from ..http.views.recruitment.child_depart_recruitment_view import *
from ..http.views.map_view import *
from ..http.views.employee_view import *
from ..http.views.kafka_view import *
from ..http.views.sync_view import SyncDataViewset
from ..http.views.ultility_view import UltilityView

urlpatterns = [
    path('health', HealthView.as_view({'get': 'health'})),
    path('get-api', HealthView.as_view({'get': 'add_kong'})),
    path('emp-info', HrView.as_view({'get': 'get_emp_info', 'post': 'post_emp_info'})),
    path('block-info', HrView.as_view({'get': 'get_block_info'})),
    path('emp-in-block', HrView.as_view({'post': 'get_all_in_block'})),
    path('email-in-block', HrView.as_view({'post': 'get_in_block'})),
    path('name-from-code', HrView.as_view({'post': 'name_from_code'})),
    path('list-name-from-code', HrView.as_view({'post': 'list_name_from_code'})),
    path('list-code-from-name', HrView.as_view({'post': 'list_code_from_name'})),
    path('info-from-email', HrView.as_view({'post': 'info_from_email'})),
    path('info-from-code-list', HrView.as_view({'post': 'info_from_code_list'})),
    path('import-employee', HrView.as_view({'post': 'import_employee'})),
    path('add-employee', HrView.as_view({'post': 'add_employee'})),
    path('edit-employee', HrView.as_view({'post': 'edit_employee'})),

    path('update-status-working', HrView.as_view({'post': 'update_status_working_employee'})),
    path('get-contracts-type', HrView.as_view({'get': 'get_contracts_type'})),
    path('delete-contracts-type-from-redis', HrView.as_view({'post': 'delete_contracts_type_from_redis'})),
    path('update-department', DepartmentView.as_view({'post': 'update_department'})),
    path('update-order-department',
         DepartmentView.as_view({'post': 'update_order_department'})),
    path('get-child-departs-from-parent-depart',
         DepartmentView.as_view({'post': 'get_child_departs_from_parent_depart'})),

    path('email-is-ptq', PtqView.as_view({'post': 'email_is_ptq'})),
    path('code-in-block', PtqView.as_view({'post': 'get_code_in_block'})),
    path('emp-rank', PtqView.as_view({'post': 'get_emp_rank'})),
    path('import-rank', PtqView.as_view({'post': 'import_rank'})),
    path('edit-rank', PtqView.as_view({'post': 'edit_rank'})),
    path('check-import-rank', PtqView.as_view({'post': 'check_import_rank'})),
    path('export-rank', PtqView.as_view({'post': 'export_emp_rank'})),
    path('safe-card-info', PtqView.as_view({'post': 'safe_card_info'})),
    path('add-safe-card', PtqView.as_view({'post': 'add_safe_card'})),
    path('import-safe-card', PtqView.as_view({'post': 'import_safe_card'})),
    path('get-profile-info', ProfileView.as_view({'post': 'get_profile_info'})),
    path('profile-and-user-permissions', ProfileView.as_view({'post': 'get_profile_and_user_permissions'})),
    path('get-name-fr-email', TechinicalSupportView.as_view({'post': 'get_name_fr_email'})),
    path('get-info-from-email', TechinicalSupportView.as_view({'post': 'get_info_fr_email'})),
    path('get-info-child-depart', TechinicalSupportView.as_view({'post': 'get_info_child_depart'})),

    path('get-fea-roles-by-codes', ProfileView.as_view({'post': 'get_feature_roles_by_codes'})),
    path('check-email-has-fea-roles-by-codes', ProfileView.as_view({'post': 'check_email_has_feature_roles_by_codes'})),

    path('info-emp-fr-branch', WorkdayView.as_view({'post': 'info_emp_fr_branch'})),
    path('detail-emp-for-workday', WorkdayView.as_view({'post': 'api_detail_emp_for_workday'})),
    path('detail-emp-for-leave-application', WorkdayView.as_view({'post': 'api_detail_emp_for_leave_application'})),
    path('check-status-from-emp-code', WorkdayView.as_view({'post': 'check_status_from_emp_code'})),
    path('get-list-emp-code', WorkdayView.as_view({'post': 'get_list_emp_code'})),
    path('get-list-emp-code-from-child-depart', InfoCheckinView.as_view({'post': 'get_list_emp_from_child_depart'})),
    path('get-emp-code-from-list-child-depart-and-email', InfoCheckinView.as_view({'post': 'get_emp_code_from_list_child_depart_and_email'})),
    path('get-emp-code-from-list-child-depart-and-name', InfoCheckinView.as_view({'post': 'get_emp_code_from_list_child_depart_and_name'})),

    path('child-depart-recruitment', ChildDepartRecruitmentView.as_view({'post': 'child_depart_recruitment'})),
    path('check-emp-rank', HrView.as_view({'post': 'check_emp_rank'})),
    path('save-all-departs-to-redis', ProfileView.as_view({'post': 'save_all_departs_to_redis'})),
    path('all-departs-levels-from-redis', ProfileView.as_view({'post': 'get_all_departs_levels_from_redis'})),

    path('get-branch-from-email', TechinicalSupportView.as_view({'post': 'get_branch_from_email'})),

    path('update-situation-safe-card', PtqView.as_view({'get': 'update_situation_safe_card'})),
    path('get-child-depart', ProfileView.as_view({'post': 'get_child_depart'})),
    path('view-info-work-safe-card', SafecardView.as_view({'post': 'view_info_work_safe_card'})),

    # danh cho quan ly the an toan lao dong,
    path('info-list-train', SafecardView.as_view({'post': "info_list_train"})),
    path('info-state-work-safe-card', SafecardView.as_view({'post': "info_state_work_safe_card_for_manager"})),
    # danh cho quan ly the an toan lao dong,
    path('info-histories-state-work-safe-card',
         SafecardView.as_view({'post': "info_histories_state_work_safe_card_for_manager"})),
    # danh cho quan ly the an toan lao dong,
    path('check-img-from-ocr', SafecardView.as_view({'post': "api_check_img_from_ocr"})),
    path('info-from-ocr', SafecardView.as_view({'post': 'api_get_info_error_data'})),

    path('export-for-state-card', SafecardView.as_view({'post': "export_state_card_for_manager"})),
    path('export-info-histories-work-safe-state-card',
         SafecardView.as_view({'post': "export_histories_state_card_for_manager"})),
    path('export-list-train', SafecardView.as_view({'post': 'export_list_train'})),

    path('delete-info-work-safe-card', SafecardView.as_view({'post': 'delete_info_from_id'})),

    path('edit-info-work-safe-card', SafecardView.as_view({'post': 'edit_info_safe_card'})),
    path('add-info-work-safe-card', SafecardView.as_view({'post': 'add_info_safe_card'})),
    path('auto-update-state-safe-card', SafecardView.as_view({'post': 'cron_auto_update_status_card'})),
    path('auto-update-status-card-ocr', SafecardView.as_view({'post': 'cron_auto_update_status_card_ocr'})),
    path('import-info-work-safe-card', SafecardView.as_view({'post': "import_info_safe_card_v2"})),
    path("check-input-import-info-work-safe-card", SafecardView.as_view({'post': 'check_input_import_info_safe_card'})),
    path("auto-update-active", SafecardView.as_view({'post': "auto_update_active"})),

    # ===========================================
    path('update-still-date', SafecardView.as_view({'post': 'auto_update_status_card_v2'})),
    path('auto-update-info-card', SafecardView.as_view({'post': 'api_auto_update_info_safe_card'})),
    path('auto-update-info-emp', SafecardView.as_view({'post': 'api_update_info_emp'})),


    # danh cho quan ly xe cai tien HO Company
    path("get-user-profile-by-list-email", ProfileView.as_view({'post': "get_user_profile_by_list_email"})),
    path('get-list-email-by-list-child-depart', ProfileView.as_view({'post': "get_list_email_by_list_child_depart"})),
    path('get-email-from-code-or-name', ProfileView.as_view({'post': "get_email_from_code_or_name"})),
    path('get-all-employee-email-list', PtqView.as_view({'get': 'get_all_employee_email_list'})),


    # danh cho chuc nang map
    path("get-map-coordinate", MapView.as_view({'post': 'api_get_map_coordinate'})),

    path("import-map-department", DepartmentView.as_view({'post': "api_import_map_department"})),
    path("get-info-branch", DepartmentView.as_view({'post': 'api_get_info_branch'})),
    path('update-email-manager', DepartmentView.as_view({'post': 'api_update_email_manager'})),
    path('get-email-from-code-or-name', ProfileView.as_view({'post': "get_email_from_code_or_name"})),
    path('map-branch-detail', MapView.as_view({'post': 'api_map_branch_detail'})),
    path('get-detail-info-emp', MapView.as_view({'post': 'api_get_detail_info_emp'})),
    path('update-acgency-inside', DepartmentView.as_view({'post': 'api_update_acgency_inside'})),


    # Api cập nhật danh sách department, cập nhật deparment cho employee, cập nhật email cho employee - tool nay` chỉ
    # dùng cho cá nhân, không public ra ngoài, không tùy  sử dụng
    path('update-or-create-department', DepartmentView.as_view({'post': 'update_or_create_department'})),
    path('update-department-for-employee', ProfileView.as_view({'post': 'update_department_for_employee'})),
    path('update-email-for-employee', ProfileView.as_view({'post': 'update_email_for_employee'})),
    # chỉ đúng 1 trường hợp đang làm, ko sử dụng cho việc khác
    path('update-employees-info-with-permissions-and-fea-roles',
         DepartmentView.as_view({'post': 'update_employees_info_with_permissions_and_fea_roles'})),

    # Api cho ho-job
    path('get-parent-depart-from-branch', DepartmentView.as_view({'post': 'get_parent_depart_from_branch'})),
    path('email-from-emp-code', HrView.as_view({'post': 'email_from_emp_code'})),
    path('email-list-from-emp-name', HrView.as_view({'post': 'email_list_from_emp_name'})),
    path('emp-code-by-child-depart', HrView.as_view({'post': 'emp_code_by_child_depart'})),
    path('get-emp-code-and-name-from-email', HrView.as_view({'post': 'get_emp_code_and_name_from_email'})),
    
    # api get employee info by filteration condition
    
    path('filteration-condition', EmployeeView.as_view({'post':'filteration_condition'})),

    # test kafka
    path('send-message-log', KafkaView.as_view({'post': 'api_send'})),

    # api cho table config
    path('list-config', ConfigView.as_view({'get': 'list'})),
    path('retrieve-config', ConfigView.as_view({'get': 'retrieve'})),
    path('create-config', ConfigView.as_view({'post': 'create'})),
    path('delete-config', ConfigView.as_view({'post': 'destroy'})),
    path('update-config', ConfigView.as_view({'post': 'update'})),

    path('hris-login', SyncDataViewset.as_view({'get': 'hris_login'})),
    path('sync-employees-data', SyncDataViewset.as_view({'get': 'sync_employees_data'})),
#     path('sync-employees-data-all', SyncDataViewset.as_view({'get': 'sync_employees_data_all'})),
    path('sync-employee-qualification-data', SyncDataViewset.as_view({'get': 'sync_employee_qualification_data'})),
    path('sync-employee-certificate-data', SyncDataViewset.as_view({'get': 'sync_employee_certificate_data'})),
    path('hris-view-cache', SyncDataViewset.as_view({'post': 'view_cache'})),
    path('sync-specified-employee-data', SyncDataViewset.as_view({'post': 'sync_specified_employee_data'})),

    path("get-modify-histories", UltilityView.as_view({'post': 'get_modify_histories'})),
    
    # view permission
    path("all-distinct-emp", EmployeeView.as_view({'post': 'all_distinct_emp'})),
    path("all-group-emp", EmployeeView.as_view({'post': 'all_group_emp'})),
    
    path("all-group-emp", EmployeeView.as_view({'post': 'all_group_emp'})),
]
