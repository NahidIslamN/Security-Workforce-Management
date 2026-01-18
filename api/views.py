
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import CustomUser
from .serializers import *
from django.contrib.auth import authenticate
import random
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import check_password
from .tasks import sent_email_to
from chat_app.tasks import sent_note_to_user
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from django.utils import timezone
from datetime import timedelta

sleep_time = 0
import time


class SignupView(APIView):
    def post(self, request):
        time.sleep(sleep_time)
        serializers = UsermodelSignupSerializer(data = request.data)
        email = serializers.initial_data['email']
        user = CustomUser.objects.filter(email=email).first()
        if user and user.is_email_varified==False:
            user.email = email
            user.set_password(serializers.initial_data['password'])
            user.user_type = serializers.initial_data['user_type']
            user.first_name = serializers.initial_data['first_name']
            user.save()    
            return Response({ "success": True, "message": "user created successfully."},status=status.HTTP_201_CREATED)

        if serializers.is_valid():
            user = serializers.save()
            otp = f"{random.randint(0, 999999):06}"
            subject = 'Verification'
            plain_message = f"your otp is {otp}"
            sent_email_to.delay(email= user['email'], text = plain_message, subject=subject)
            user = CustomUser.objects.get(email = serializers.data["email"])
            user.otp = otp
            user.save()
            token = request.GET.get('referral_token', None)
            if token is not None:
                try:
                    company = CompanyModel.objects.get(refaral_token=token)
                    company.refaral_users.add(user)
                    company.save()

                except :
                    pass

                try:
                    application = JobApplications.objects.get(refaral_token=token)
                    application.refaral_users.add(user)
                    application.save()
                except :
                    pass

            else:
                pass

            return Response({ "success": True, "message": "The user has been created successfully."},status=status.HTTP_201_CREATED)
        
        return Response({ "success": False, "message": "The email address already exists.", "errors":serializers.errors},status=status.HTTP_400_BAD_REQUEST)


    

class Verify_Email_Signup(APIView):
    def post(self,request, email):
        time.sleep(sleep_time)
        serializers = OTPSerializer(data = request.data)
        if serializers.is_valid():
            
            try:
                user = CustomUser.objects.get(email = email)
                otp = user.otp
                if serializers.data['otp'] == otp:
                    user.is_email_varified = True
                    otp = str(random.randint(000000, 999999))
                    user.otp = otp
                    user.save()
                    # Notify user about successful email verification
                    sent_note_to_user.delay(user_id=user.id, title=f"Email Verified", content=f"Your email has been successfully verified. Welcome to SecurityGuard!", note_type='success')
                    return Response({"message":"verified successfully!"}, status = status.HTTP_200_OK)
                else:
                    return Response({"success":False,"message":"Invalid verification code."}, status=status.HTTP_400_BAD_REQUEST)

            except CustomUser.DoesNotExist:
                return Response({"success":False,"message":"user not found"},status=status.HTTP_400_BAD_REQUEST)

        return Response({"success":False,"message":"validation errors","errors":serializers.errors}, status=status.HTTP_400_BAD_REQUEST)





class LoginView(APIView):
    def post(self,request):
        time.sleep(sleep_time)
        serializer = LoginSerializers(data = request.data)
        time.sleep(sleep_time)
        if serializer.is_valid():
            user = authenticate(email = serializer.data['email'], password = serializer.data['password'])
            if user:
                if user.is_email_varified:

                    if user.is_admin_aproved or user.user_type == "admin":                        
                        refresh = RefreshToken.for_user(user)
                        return Response( {
                            "success":True,
                            'verified':True,
                            "message":f"Welcome {user.first_name}!",
                            'access': str(refresh.access_token),
                            'refresh': str(refresh)  
                                                
                        }, status=status.HTTP_200_OK)
                    
                    else:
                        if user.user_type == "guard":
                            application_data, create = JobApplications.objects.get_or_create(candidate = user)
                            serializer = Gurd_Application_Details(application_data)
                            refresh = RefreshToken.for_user(user)
                            return Response( {
                                "success":True,
                                'is_admin_aproved':user.is_admin_aproved,
                                "message":f"Welcome {user.first_name}!",
                                'access': str(refresh.access_token),
                                'refresh': str(refresh),
                                'guard_details':serializer.data
                                
                            }, status=status.HTTP_200_OK)
                        
                        
                        elif user.user_type == "company":
                            company, create = CompanyModel.objects.get_or_create(company = user)
                            company_serializer = CompanyinfoSerializer(company)
                            refresh = RefreshToken.for_user(user)
                            return Response( {
                                "success":True,
                                'verified':False,
                                'company_name':user.first_name,
                                "message":f"Welcome {user.first_name}!",
                                'access': str(refresh.access_token),
                                'refresh': str(refresh),
                                'company_info':company_serializer.data
                                            
                            }, status=status.HTTP_200_OK)
                        
                        else:
                            pass
                
                otp = f"{random.randint(0, 999999):06}"
                subject = 'Verification'
                plain_message = f"your otp is {otp}"
                sent_email_to.delay(email= user.email, text = plain_message, subject=subject)
                user.otp = otp
                user.save()
                return Response(
                    {
                        "success":False,
                        "message":"OTP sent to your email. Please verify before logging.", 
                        
                    },
                    status=status.HTTP_401_UNAUTHORIZED
                    
                )

            return Response({"success":False,"message":"Invalid username or password.!"}, status=status.HTTP_400_BAD_REQUEST)   
        return Response({"success":False,"message":"validation errors", "errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

class ChangePassword(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        time.sleep(sleep_time)
        user = request.user        
        serializer =  ChangePassword_serializer(data = request.data)
        if serializer.is_valid():
            hash_password = user.password
            raw_password = serializer.data['old_password']
            if check_password(raw_password, hash_password):
                user.set_password(serializer.data['new_password'])
                user.save()
                # Notify user about password change
                sent_note_to_user.delay(user_id=user.id, title=f"Password changed successfully.", content=f"Your password has been changed successfully", note_type='success')
                return Response({"message":"Password changed successfully!"}, status= status.HTTP_200_OK)
            else:
                return Response({"message":"worng old password!"}, status=status.HTTP_400_BAD_REQUEST )
        return Response({"success":False, "message":"validation errors", "errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    


class ForgetPasswordView(APIView):
    def post(self, request):
        serializer = ForgetPasswordSerializer(data=request.data)

        if serializer.is_valid():
            try:

                user = CustomUser.objects.get(
                    email=serializer.validated_data['email']
                )
               
                # Check if an OTP was generated recently (e.g., within 60 seconds)
                now = timezone.now()
                # Assuming updated_at is updated whenever save() is called.
                # If we just saved OTP, updated_at should be very recent.
                # Logic: If updated_at is < 60s ago AND user has an OTP, reuse it.
                
                # Note: 'updated_at' field exists on CustomUser based on models.py
                time_threshold = now - timedelta(seconds=60)
                
                if user.otp and user.updated_at and user.updated_at > time_threshold:
                    otp = user.otp
                    # We don't save the user here to avoid changing updated_at again if we want to be strict,
                    # OR we can save it to extend the window. 
                    # But the goal is to stabilize the OTP.
                    # Let's NOT save a new OTP.
                else:
                    otp = f"{random.randint(0, 999999):06}"
                    user.otp = otp
                    user.save(update_fields=["otp", "updated_at"])  # Update DB
    
                sent_email_to.delay(
                    email=user.email,
                    text=f"Your OTP is {otp}",
                    subject="Verification"
                )

                return Response(
                    {
                        "success": True,
                        "message": "OTP sent to your email"
                    },
                    status=status.HTTP_200_OK
                )

            except CustomUser.DoesNotExist:
                return Response(
                    {"success": False, "message": "User not found."},
                    status=status.HTTP_400_BAD_REQUEST
                )

        return Response(
            {
                "success": False,
                "message": "Validation error",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

class Verify_User_ForgetPassword(APIView):
    def post(self, request, email):
        time.sleep(sleep_time)
        serializer = OTPSerializer(data = request.data)
        if serializer.is_valid():
            try:
                user = CustomUser.objects.get(email = email)
                otp = user.otp
                if serializer.data['otp'] == otp:
                    refresh = RefreshToken.for_user(user)
                    # this refresh token will one time use for reset password

                    otp = str(random.randint(000000, 999999))
                    user.otp = otp
                    user.save()
                    return Response( {
                        "success":True,
                        "message":"verified successfully!",
                        'access': str(refresh.access_token),
                        'refresh': str(refresh)                        
                    },status=status.HTTP_200_OK)
                else:
                    return Response({"success":False,"message":"Invalid verification code."}, status=status.HTTP_400_BAD_REQUEST)
            except CustomUser.DoesNotExist:
                return Response({"success":False,"message":"User not found!"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"success":False,"message":"validation errors", "errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        time.sleep(sleep_time)
        user = request.user
        serializer = ResetPasswordSerializer(data = request.data)
        if serializer.is_valid():
            user.set_password(serializer.data['new_password'])
            # Notify user about password reset
            sent_note_to_user.delay(user_id=user.id, title=f"Password Reset", content=f"Your password has been reset successfully", note_type='success')
            user.save()
            return Response({ "success": True, "message": "Your password has been reset successfully."}, status=status.HTTP_200_OK)
        return Response({ "success": False, "message": "validation error!", "errors": serializer.errors }, status=status.HTTP_400_BAD_REQUEST)


def generate_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "success":True,
        "message":f"Welcome {user.first_name}",
        "access": str(refresh.access_token),
        "refresh": str(refresh),
        
    }

class GoogleLoginView(APIView):
    def post(self, request):
        time.sleep(sleep_time)
        token = request.data.get("id_token")
        try:
            idinfo = id_token.verify_oauth2_token(token, google_requests.Request())
            email = idinfo.get("email")
            owner_name = idinfo.get("name")
            print(email)
            users, created = CustomUser.objects.get_or_create(email=email)
            users.first_name=owner_name
            users.defaults={"email": email}
            users.username = email
            users.is_email_verified=True
            users.save()
            return Response(generate_tokens_for_user(users), status=status.HTTP_200_OK)
        except Exception as e:
            print(e)
            return Response({"success":False,"error": "Invalid Google token"}, status=status.HTTP_400_BAD_REQUEST)
    


class GetMyPolan(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        plan = SubscribtionPlan.objects.filter()
        serializer = SubPlanSerializer(plan, many=True)

        return Response(
            {
                "success":True,
                "message":"Subscription plans retrieved successfully.!",
                "plans":serializer.data
            }
        )



