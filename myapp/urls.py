from django.urls import path
from myapp.views import coordinator_student_reports_view, coordinator_student_detail_view, intern_login_view, coordinator_submit_update_view, chairman_coordinator_detail
from . import views

urlpatterns = [
    path('', intern_login_view, name='intern_login_root'), # Add this line
    path('coordinator/student-reports/', coordinator_student_reports_view, name='coordinator_student_reports'),
    path('coordinator/student-detail/<int:intern_id>/', coordinator_student_detail_view, name='coordinator_student_detail'),
    path('intern/login/', intern_login_view, name='intern_login'),
    path('coordinator/submit-update/', coordinator_submit_update_view, name='coordinator_submit_update'),
    path('chairman/coordinator/<int:coordinator_id>/', chairman_coordinator_detail, name='chairman_coordinator_detail'),
    path('coordinator/intern-summary/<int:intern_id>/', views.coordinator_intern_summary, name='coordinator_intern_summary'),
]