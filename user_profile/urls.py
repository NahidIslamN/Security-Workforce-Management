from django.urls import path
from .views import *

urlpatterns = [
    path("user-profile/", MyProfileData.as_view(), name='mycompany-details'),
    path("user-refarral-code/", Myrefarral_link.as_view(), name='refarral-code'),
    path("user-refarral-users/", Myrefarral_User.as_view(), name='refarral-code'),
    path("company-details/", MycompanyDetails.as_view(), name='mycompany-details'),
    path('profile-update/', UserProfileChangeView.as_view(), name="user-profile-change"),
    path('licences/', UserLicenceCreateView.as_view(), name="user-licence-create"),
    path('licences/<int:pk>/', UserLicenceCreateView.as_view(), name="user-licence-update"),
    path('certificates/', UsersCertificatesCreateUpdateView.as_view(), name='user-certificate-create'),
    path('certificates/<int:pk>/', UsersCertificatesCreateUpdateView.as_view(), name='user-certificate-update'),
    path('location-update/', Location_update.as_view(), name="location-update"),
    path('save-card-info/', Get_myCard_info.as_view(), name="card info"),
    path('get-card-info/', Get_myCard_info.as_view(), name="card info"),
    path('get-invoices/', Get_My_Invoices.as_view(), name="billings data"),

]
