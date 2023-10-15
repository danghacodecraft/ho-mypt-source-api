from django.urls import path
from .http.views.health_view import *
from .http.views.ptq_view import *
from .http.views.improve_car_view import *


urlpatterns = [
    path('health', HealthView.as_view({'get':'health'})),
    path('get-api', HealthView.as_view({'get':'add_kong'})),
    path('show-report', PtqView.as_view({'post':'show_report'})),
    path('get-contract', PtqView.as_view({'post':'get_contract'})),
    path('import-report', PtqView.as_view({'post':'import_report_ptq'})),
    path('show-tools', PtqView.as_view({'post':'get_tools'})),
    path('show-report-ptq', PtqView.as_view({'post':'show_report_ptq'})),
    path('list-report', PtqView.as_view({'post':'list_type_report'})),
    path('show-explanation', PtqView.as_view({'get':'show_explanation'})),
    # Vua edit, vua xoa
    path('explanation', PtqView.as_view({'post':'explanation'})),
    # gio chi con dung de lay ly do xoa
    path('delete-ptq', PtqView.as_view({'get':'get_delete_ptq', 'post':'delete_ptq'})),
    path('cron-status-ptq', PtqView.as_view({'post':'cron_status_ptq'})),
    path('insert-reports-to-new-ptq-tb', PtqView.as_view({'post':'insertReportsToNewPtqTb'})),
    path('explanation-reminder', PtqView.as_view({'get':'explanation_reminder'})),

    path('export-improve-car',  ImprovecarView.as_view({'post': 'export_car'})),
    path('get-list-improved-car', ImprovecarView.as_view({'post': 'get_list_improved_car'})),
    path('get-detail-improved-car', ImprovecarView.as_view({'post': 'get_detail_improved_car'})),
    path('delete-improved-car-comment', ImprovecarView.as_view({'post': 'delete_improved_car_comment'})),
    path('all-improve-car-type-title', ImprovecarView.as_view({'get': 'all_improve_car_type_title'})),
]
