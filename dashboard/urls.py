from django.urls import path

from dashboard import views

app_name = "dashboard"

urlpatterns = [
    path("weekly/", views.WeeklyDashboardView.as_view(), name="weekly"),
    path("monthly/", views.MonthlyDashboardView.as_view(), name="monthly"),
]
