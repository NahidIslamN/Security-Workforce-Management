from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from api.models import CustomUser, Invoices, SubscribtionPlan
from django.contrib.auth import get_user_model

User = get_user_model()

class AdminDashboardAnalyticsTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='password123'
        )
        self.client.force_authenticate(user=self.admin_user)

        # Create dummy users
        User.objects.create_user(email='guard1@example.com', password='pw', user_type='guard', is_deleted=False)
        User.objects.create_user(email='guard2@example.com', password='pw', user_type='guard', is_deleted=False)
        User.objects.create_user(email='company1@example.com', password='pw', user_type='company', is_deleted=False)

        # Create dummy invoice
        plan = SubscribtionPlan.objects.create(price=100.00, discriptions='Test Plan')
        Invoices.objects.create(user=self.admin_user, invoice_date='2025-01-01', end_date='2026-01-01', price=100.00, plan=plan)

    def test_dashboard_summary(self):
        url = reverse('dashboard-summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        data = response.data['data']
        
        self.assertEqual(data['total_earnings'], 100.0)
        self.assertEqual(data['total_companies'], 1)
        self.assertEqual(data['total_guards'], 3)
        self.assertTrue(len(data['recent_users']) >= 3)

    def test_company_management_with_invoices(self):
        # Create a company and associate an invoice
        company_user = User.objects.create_user(email='company_test@example.com', password='pw', user_type='company')
        from api.models import CompanyModel
        CompanyModel.objects.create(company=company_user, company_name='Test Company')
        
        plan = SubscribtionPlan.objects.get(discriptions='Test Plan')
        Invoices.objects.create(user=company_user, invoice_date='2025-01-01', end_date='2026-01-01', price=50.00, plan=plan)

        url = reverse('company-managements')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['success'])
        
        # Check if invoice data is present in at least one company
        has_invoices = False
        for company in response.data['companies']:
            if company['company_name'] == 'Test Company':
                self.assertTrue(len(company['invoices']) > 0)
                self.assertEqual(float(company['invoices'][0]['price']), 50.0)
                has_invoices = True
        
        self.assertTrue(has_invoices)
