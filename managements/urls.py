from django.urls import path
from .views import *

urlpatterns = [
    
    path('job-posts/', PostJobs.as_view(), name='guards-job-post-section'),
    path('job-posts/<int:pk>/', PostJobs.as_view(), name='post_jobs_detail'),

    path('job-details/<int:pk>/', JobDetailsCompanyPoint.as_view(), name="job-details"), # job details only view details
    path('job-select-an-operative/<int:pk>/<int:apk>/', JobDetailsCompanyPoint.as_view(), name="select_operative"), # select operatives


    path('company-engagements/', EngagementsViews.as_view(), name='engagements'),
    path('company-engagements-details/<int:pk>/', EngagementsDetailsViews.as_view(), name='engagements'),
    path('company-perfromed-operatives/', PerferetOperativeViews.as_view(), name='perfromed-operatives'),
    path('company-perfromed-operatives/<int:pk>/', PerferetOperativeViews.as_view(), name='perfromed-operatives-delete'),

    path('comanny-payroll-management-views/', PayRollManagementViews.as_view(), name="payroll-managements"),

    path('company-operative-trackers-views/', OperativeViews.as_view(), name='opreative-trackers'),
    path('company-dashboard-metrics/', Company_Dashboard_Analytics.as_view(), name='company-dashboard-metrics'),

    #############
    path('user-job-posts/', GuardsJobPostSection.as_view(), name='user_job_posts'),
    path('user-job-posts/<int:pk>/', GuardsJobPostSection.as_view(), name='user_job_posts_details'),
    path('user-dashboard-data/', Guard_Dashboard.as_view(), name='user-dashboard-data'),
    path("user_Jobs_history/", Gard_Jobs_History.as_view(), name="job-history" ),
    path('user-engagements-ammends/', EngagementsViewsAmmend.as_view(), name='engagements-ammends'),
    # EngagementsViewsAmmend
  


  
    ###### after appy#
    path('user/my-jobs/', Gard_Jobs_Section.as_view(), name='users-my-jobs'),
    path('user/my-jobs/<int:pk>/', Gard_Jobs_Section.as_view(), name='users-my-jobs-amnd-request-handle'),




    #### rating on a engagement
    path('rating-on-an-eng/<int:pk>/', Rate_On_Engagement.as_view(), name='rating-management'),


    # licence type
    path('licence-types/', Licence_Types_List.as_view(), name='licence-types'),
    path('certificate-types/', Certificate_Types_List.as_view(), name='certificate-types'),
    path('support-message/', SupportView.as_view(), name='support-message'),

    


]
