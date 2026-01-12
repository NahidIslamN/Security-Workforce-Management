from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch


User = get_user_model()



from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from api.models import CustomUser
import re

class SignupViewTest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse("signup")  # Replace with your URL name

        # Existing user for duplicate email test
        self.existing_user = CustomUser.objects.create_user(
            email="existing@test.com", 
            password="pass123"
        )

    def test_signup_success(self):
        payload = {
            "first_name": "John",
            "email": "newuser@test.com",
            "password": "securePass123",
            "user_type": "guard"
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "user create successfully!")
        self.assertEqual(response.data["data"]["email"], payload["email"])

        # Check user is created in DB
        user = CustomUser.objects.get(email=payload["email"])
        self.assertIsNotNone(user)
        # OTP should be 6 digits
        self.assertTrue(re.match(r'^\d{6}$', user.otp))

    def test_signup_missing_email(self):
        """Test missing email field"""
        payload = {
            "password": "pass123",
            "user_type": "guard",
            "first_name": "John"
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_signup_invalid_email(self):
        """Test invalid email format"""
        payload = {
            "email": "invalid-email",
            "password": "pass123",
            "user_type": "guard",
            "first_name": "John"
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_signup_missing_password(self):
        """Test missing password field"""
        payload = {
            "email": "user2@test.com",
            "user_type": "guard",
            "first_name": "John"
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password", response.data)

    def test_signup_duplicate_email(self):
        """Test signup with an email that already exists"""
        payload = {
            "email": self.existing_user.email,
            "password": "newpass123",
            "user_type": "guard",
            "first_name": "John"
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)




class VerifyEmailSignupTestCase(APITestCase):

    def setUp(self):
        # Create a user with OTP
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="StrongPass123",
            otp="123456",
            is_email_varified=False
        )

        self.url = reverse("verify_email_signup", kwargs={"email": self.user.email})

    def test_valid_otp_verifies_user(self):
        data = {"otp": "123456"}
        response = self.client.post(self.url, data, format="json")

        self.user.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(self.user.is_email_varified)
        self.assertEqual(response.data["message"], "verifyed successfully")

    def test_invalid_otp_returns_error(self):
        data = {"otp": "999999"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("wrong varification code!", response.data["message"])
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_email_varified)

    def test_user_not_found_returns_error(self):
        invalid_url = reverse("verify_email_signup", kwargs={"email": "notfound@example.com"})
        data = {"otp": "123456"}
        response = self.client.post(invalid_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("user not found", response.data["message"])

    def test_validation_error_returns_error(self):
        data = {}  # missing OTP field
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("validation errors", response.data["message"])





from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
from rest_framework_simplejwt.tokens import RefreshToken

from api.models import JobApplications, CompanyModel  # adjust your imports
from api.serializers import Gurd_Application_Details, CompanyinfoSerializer  # adjust your imports

User = get_user_model()

class LoginViewTests(APITestCase):
    def setUp(self):
        self.password = "StrongPass123"
        self.login_url = reverse("login")  # make sure your url name matches
        self.admin_user = User.objects.create_user(
            email="admin@example.com",
            password=self.password,
            user_type="admin",
            is_email_varified=True,
            is_admin_aproved=True
        )

        self.guard_user = User.objects.create_user(
            email="guard@example.com",
            password=self.password,
            user_type="guard",
            is_email_varified=True,
            is_admin_aproved=False
        )

        self.company_user = User.objects.create_user(
            email="company@example.com",
            password=self.password,
            user_type="company",
            is_email_varified=True,
            is_admin_aproved=False
        )

        self.unverified_user = User.objects.create_user(
            email="unverified@example.com",
            password=self.password,
            user_type="guard",
            is_email_varified=False,
        )

    def test_login_with_invalid_credentials(self):
        data = {"email": self.admin_user.email, "password": "WrongPass"}
        res = self.client.post(self.login_url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(res.data["message"], "username or password Invalid!")
        self.assertFalse(res.data["success"])

    def test_login_with_missing_fields(self):
        data = {}
        res = self.client.post(self.login_url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("errors", res.data)

    def test_login_with_verified_admin_user(self):
        data = {"email": self.admin_user.email, "password": self.password}
        res = self.client.post(self.login_url, data, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(res.data["success"])
        self.assertTrue(res.data["verified"])
        self.assertIn("access", res.data)
        self.assertIn("refresh", res.data)

    def test_login_with_verified_guard_user_creates_application(self):
        data = {"email": self.guard_user.email, "password": self.password}
        res = self.client.post(self.login_url, data, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(JobApplications.objects.filter(candidate=self.guard_user).exists())
        self.assertIn("guard_details", res.data)
        self.assertFalse(res.data["verified"])
        self.assertTrue(res.data["success"])

    def test_login_with_verified_company_user_creates_company(self):
        data = {"email": self.company_user.email, "password": self.password}
        res = self.client.post(self.login_url, data, format="json")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(CompanyModel.objects.filter(company=self.company_user).exists())
        self.assertIn("company_info", res.data)
        self.assertIn("company_name", res.data)
        self.assertFalse(res.data["verified"])

    @patch("api.views.sent_email_to.delay")
    def test_login_with_unverified_user_sends_otp(self, mock_send_email):
        data = {"email": self.unverified_user.email, "password": self.password}
        res = self.client.post(self.login_url, data, format="json")

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(res.data["success"])
        self.assertEqual(res.data["message"], "We sent an otp to your email! verify your first then login")

        mock_send_email.assert_called_once()
        user = User.objects.get(email=self.unverified_user.email)
        self.assertIsNotNone(user.otp)
        self.assertTrue(len(user.otp) == 6)



class ChangePasswordTests(APITestCase):
    def setUp(self):
        self.password = "OldPass123!"
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password=self.password,
            is_email_varified=True
        )

        self.change_password_url = reverse("change_password")

    def authenticate(self):
        """Helper function to authenticate user using JWT"""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_change_password_success(self):
        """✅ Should change password successfully when old password is correct"""
        self.authenticate()
        data = {
            "old_password": self.password,
            "new_password": "NewStrongPass456!"
        }
        response = self.client.post(self.change_password_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["message"], "Password changed successfully!")

        # verify new password actually works
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewStrongPass456!"))

    def test_change_password_wrong_old_password(self):
        self.authenticate()
        data = {
            "old_password": "WrongPass!",
            "new_password": "NewStrongPass456!"
        }
        response = self.client.post(self.change_password_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("worng old password", response.data["message"])

        # ensure password didn’t change
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.password))

    def test_change_password_invalid_serializer(self):
        self.authenticate()
        data = {"old_password": ""}  # new_password missing
        response = self.client.post(self.change_password_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("errors", response.data)

    def test_change_password_unauthenticated(self):
        data = {
            "old_password": self.password,
            "new_password": "NewStrongPass456!"
        }
        response = self.client.post(self.change_password_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)




class ForgetPasswordFlowTests(APITestCase):

    def setUp(self):
        self.password = "Test@12345"
        self.user = User.objects.create_user(
            email="user@example.com",
            password=self.password,
            is_email_varified=True
        )

        # URLs (adjust names according to your urls.py)
        self.forget_password_url = reverse("forget_password")  
        self.verify_otp_url = reverse("verify_user_forget_password", kwargs={"email": self.user.email})

    @patch("api.views.sent_email_to.delay")
    def test_forget_password_sends_otp_email(self, mock_send_email):
        data = {"email": self.user.email}
        response = self.client.post(self.forget_password_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "we sent a otp in your email! verify the otp first")

        user = User.objects.get(email=self.user.email)
        self.assertIsNotNone(user.otp)
        self.assertTrue(len(user.otp) == 6)
        mock_send_email.assert_called_once()

    def test_forget_password_user_not_found(self):
        data = {"email": "notfound@example.com"}
        response = self.client.post(self.forget_password_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["message"], "user not found!")

    def test_forget_password_invalid_serializer(self):
        data = {}  # missing email
        response = self.client.post(self.forget_password_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("errors", response.data)

    def test_verify_user_with_correct_otp(self):
        """✅ Should verify user when correct OTP is provided"""
        otp = "123456"
        self.user.otp = otp
        self.user.save()

        data = {"otp": otp}
        response = self.client.post(self.verify_otp_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "verified successfull!")
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        # Verify OTP changed after success
        self.user.refresh_from_db()
        self.assertNotEqual(self.user.otp, otp)

    def test_verify_user_with_wrong_otp(self):
        self.user.otp = "654321"
        self.user.save()

        data = {"otp": "000000"}
        response = self.client.post(self.verify_otp_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["message"], "wrong varification code!")

    def test_verify_user_not_found(self):
        # Use non-existent email in URL
        invalid_url = reverse("verify_user_forget_password", kwargs={"email": "notfound@example.com"})
        data = {"otp": "123456"}
        response = self.client.post(invalid_url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertEqual(response.data["message"], "User not found!")

    def test_verify_user_invalid_serializer(self):
        response = self.client.post(self.verify_otp_url, {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("errors", response.data)

    @patch("api.views.sent_email_to.delay")
    def test_forget_password_double_submission(self, mock_send_email):
        """
        Test that calling forget_password twice rapidly (within 60s)
        results in the SAME OTP being used, to prevent race conditions.
        """
        # First request
        response1 = self.client.post(self.forget_password_url, {"email": self.user.email}, format="json")
        self.assertEqual(response1.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        otp1 = self.user.otp
        update_time1 = self.user.updated_at
        
        # Second request (simulate immediate retry/double click)
        response2 = self.client.post(self.forget_password_url, {"email": self.user.email}, format="json")
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        
        self.user.refresh_from_db()
        otp2 = self.user.otp
        update_time2 = self.user.updated_at
        
        # KEY ASSERTION: OTPs must match
        self.assertEqual(otp1, otp2, "OTP should be reused if requested immediately again")
        
        # updated_at might strictly be the same if we didn't save, or slightly different if we did?
        # My implementation DOES NOT save the user if reusing OTP, so timestamps should match EXACTLY.
        self.assertEqual(update_time1, update_time2, "User record should not be updated on OTP reuse")



class ResetPasswordTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="OldPassword123!",
            is_email_varified=True
        )
        self.url = reverse("reset_password")  
    def authenticate(self):
        """Helper to authenticate the user using JWT"""
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")

    def test_reset_password_success(self):
        self.authenticate()
        data = {"new_password": "NewPassword456!"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])
        self.assertEqual(response.data["message"], "password reset successfully")

        # Verify password actually changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewPassword456!"))

    def test_reset_password_validation_error(self):
        self.authenticate()
        data = {"new_password": ""}  # empty password should trigger serializer error
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("errors", response.data)
        self.assertEqual(response.data["message"], "validation error!")

    def test_reset_password_unauthenticated(self):
        data = {"new_password": "NewPassword456!"}
        response = self.client.post(self.url, data, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)




