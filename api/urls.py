from django.urls import path
from .views import *

urlpatterns = [
    path("signup/", SignupView.as_view(), name="signup"),
    path("verify/<str:email>/", Verify_Email_Signup.as_view(),name="verify_email_signup"),
    path("login/", LoginView.as_view(), name='login'),
    path("changepassword/", ChangePassword.as_view(), name='change_password'),
    path("forgetpassword/", ForgetPasswordView.as_view(), name="forget_password"),
    path("vefiry_for_forget/<str:email>/", Verify_User_ForgetPassword.as_view(), name='verify_user_forget_password'),
    path("reset_password/", ResetPasswordView.as_view(),name='reset_password'),
    path('google/', GoogleLoginView.as_view(),)
    
]
