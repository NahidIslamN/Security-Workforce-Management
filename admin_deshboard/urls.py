from django.urls import path
from .views import *

urlpatterns = [
    path("varification-center/", Verification_center.as_view(), name="verication-center"),
    path("recent-user/", Recent_User.as_view(), name="verication-center"),
    path("recent-user/<int:pk>/", Recent_User.as_view(), name="delete-user"),
    path("recent-subscribsion/", Subscribtions.as_view(), name="subscription"),
    path("recent-subscribsion/<int:pk>/", Subscribtions.as_view(), name="subscription"),
    path("user-details/<int:pk>/", UserDetails.as_view(), name="user-details"),


    path('operative-management/', Operative_Management.as_view(), name='operative-managements'),
    path('company-management/', Company_Management.as_view(), name='company-managements'),
    path('job-management/', JobManagement.as_view(), name='job-managements'),
    path('job-management/<int:pk>/', JobManagement.as_view(), name='job-managements'),
    path('contact-management/', ContactManagementAdmin.as_view(), name='contact-managements'),
    path('contact-management/<int:pk>/', ContactManagementAdmin.as_view(), name='contact-managements'),
    path('payroll-management/', PayrollReportAPIView.as_view(), name='contact-managements'),
    path('raffaral-report/', Refarral_Reprt.as_view(), name='reffaral-report'),
    path('dashboard-summary/', AdminDashboardAnalytics.as_view(), name='dashboard-summary'),
    path('payment-controller/', Payment_Crontrollers.as_view(), name='payment-controller'),
    path("subs-plans/", SubscribtionPlans.as_view(), name="subscription"),
    path("subs-plans/<int:pk>/", SubscribtionPlans.as_view(), name="subscription"),
    

]
