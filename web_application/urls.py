"""
URL configuration for web_application project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from myapp.views import (
    intern_login_view, coordinator_login_view, chairman_login_view,
    coordinator_register_view, chairman_register_view, chairman_dashboard_view,
    chairman_logout_view, coordinator_dashboard_view, interns_reports_view,
    coordinator_logout_view, intern_register_view, intern_dashboard_view,
    intern_logout_view, add_week_report_view, get_week_reports_view,
    coordinator_sections_view, coordinator_submissions_view, add_rating_view,portfolio_analysis_view, coordinator_view_interns, coordinator_intern_summary_view
)

urlpatterns = [
    path('', include('myapp.urls')),  # This line is required!
    path('coordinator/login/', coordinator_login_view, name='coordinator_login'),
    path('coordinator/register/', coordinator_register_view, name='coordinator_register'),
    path('coordinator/dashboard/', coordinator_dashboard_view, name='coordinator_dashboard'),
    path('coordinator/student-reports/', interns_reports_view, name='interns_reports'),
    path('coordinator/logout/', coordinator_logout_view, name='coordinator_logout'),
    path('coordinator/register-intern/', intern_register_view, name='intern_register'),
    path('coordinator/sections/', coordinator_sections_view, name='coordinator_sections'),
    path('coordinator/submissions/', coordinator_submissions_view, name='coordinator_submissions'),
    path('chairman/login/', chairman_login_view, name='chairman_login'),
    path('chairman/register/', chairman_register_view, name='chairman_register'),
    path('chairman/dashboard/', chairman_dashboard_view, name='chairman_dashboard'),
    path('chairman/logout/', chairman_logout_view, name='chairman_logout'),
    path('intern/dashboard/', intern_dashboard_view, name='intern_dashboard'),
    path('intern/logout/', intern_logout_view, name='logout'),
    path('add-week-report/', add_week_report_view, name='add_week_report'),
    path('get-week-reports/', get_week_reports_view, name='get_week_reports'),
    path('admin/', admin.site.urls),
    path('coordinator/add-rating/<int:report_id>/', add_rating_view, name='add_rating'),
    path('portfolio-analysis/<int:intern_id>/', portfolio_analysis_view, name='portfolio_analysis'),
    path('coordinator/view-interns/', coordinator_view_interns, name='coordinator_view_interns'),
    path('coordinator/interns-summary/', coordinator_intern_summary_view, name='coordinator_interns_summary'),
]
