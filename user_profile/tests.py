from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from api.models import CustomUser, CompanyModel, LicencesModel, CertificateModel, Images, LicencesType
from rest_framework_simplejwt.tokens import RefreshToken
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image


def generate_image_file():
   
    file = BytesIO()
    image = Image.new('RGB', (100, 100), color='blue')
    image.save(file, 'jpeg')
    file.seek(0)
    return SimpleUploadedFile('test.jpg', file.read(), content_type='image/jpeg')

class BaseAuthTestCase(APITestCase):
    def authenticate(self):
        refresh = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")


class CompanyAndProfileTests(BaseAuthTestCase):
    def setUp(self):
        self.company_user = CustomUser.objects.create_user(
            email="company@example.com",
            password="password123",
            user_type="company"
        )
        self.user = self.company_user
        self.authenticate()
        self.company_url = reverse("mycompany-details")
        self.profile_url = reverse("user-profile-change")

    def test_get_company_details_creates_if_not_exists(self):
        response = self.client.get(self.company_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertTrue(CompanyModel.objects.filter(company=self.company_user).exists())

    def test_put_company_update(self):
        """Should update company info successfully"""
        CompanyModel.objects.get_or_create(company=self.company_user)
        data = {
            "company_name": "SecureTech Ltd",
            "phone_number": "01710000000",
            "address": "Dhaka, Bangladesh",
            "state": "BD"
        }
        response = self.client.put(self.company_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['company_name'], "SecureTech Ltd")

    def test_user_profile_update(self):
        data = {"first_name": "Nahid", "email": "newmail@example.com"}
        response = self.client.put(self.profile_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.company_user.refresh_from_db()
        self.assertEqual(self.company_user.first_name, "Nahid")
        self.assertFalse(self.company_user.is_email_varified)




class LicenceTests(BaseAuthTestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="user1@example.com",
            password="password123",
        )
        self.authenticate()
        self.url = reverse("user-licence-create")  # adjust to your URL name

    def test_create_licence_with_images(self):
        """Should create a licence with multiple images"""
        img1 = generate_image_file()
        img2 = generate_image_file()
        data = {
            "state_or_territory": "Dhaka",
            "licence_type": "Armed",
            "licence_no": "ABCD123",
            "expire_date": "2030-01-01",
            "licence_images": [img1, img2],
        }
        response = self.client.post(self.url, data, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        licence = LicencesModel.objects.first()
        self.assertEqual(licence.licence_images.count(), 2)

    def test_get_licences(self):
        self.test_create_licence_with_images()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertGreater(len(response.data['data']), 0)

    def test_update_licence(self):
        self.test_create_licence_with_images()
        licence = LicencesModel.objects.first()

        update_url = reverse("user-licence-update", kwargs={"pk": licence.id})
        data = {"licence_type": "Unarmed"}
        response = self.client.put(update_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        licence.refresh_from_db()
        self.assertEqual(licence.licence_type, "Unarmed")


class CertificateTests(BaseAuthTestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            email="certuser@example.com",
            password="password123",
        )
        self.authenticate()
        self.url = reverse("user-certificate-create")

    def test_create_and_get_certificates(self):
        """Should create and list certificates"""
        data = {
            "certificate_name": "First Aid",
            "issued_by": "Red Cross",
            "valid_till": "2030-12-31"
        }
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])

    def test_update_and_delete_certificate(self):
        """Should update and delete certificate correctly"""
        cert = CertificateModel.objects.create(
            certificate_name="CPR",
            issued_by="Govt"
        )
        self.user.accreditations.add(cert)

        update_url = reverse("user-certificate-update", kwargs={"pk": cert.id})
        data = {"certificate_name": "Advanced CPR"}
        response = self.client.put(update_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        cert.refresh_from_db()
        self.assertEqual(cert.certificate_name, "Advanced CPR")

        delete_url = reverse("user-certificate-delete", kwargs={"pk": cert.id})
        response = self.client.delete(delete_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(CertificateModel.objects.filter(id=cert.id).exists())
