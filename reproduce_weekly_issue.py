import os
import django
from datetime import timedelta
from django.utils import timezone
import sys

# Add project root to path
sys.path.append('/home/lazy_aliyen/Desktop/JVAI_PROJECTS/Guard_PROJ/SecurityGuard')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SecurityGuard.settings')
django.setup()

from api.models import CompanyModel, JobModel, EngagementModel, CustomUser, JobApplications

def run_test():
    # Setup data
    email = "company_test_weekly_v1@example.com"
    if CustomUser.objects.filter(email=email).exists():
        user = CustomUser.objects.get(email=email)
        # Clean up previous runs
        CompanyModel.objects.filter(company=user).delete()
        JobModel.objects.filter(job_provider__company=user).delete()
    else:
        user = CustomUser.objects.create_user(email=email, password="password", user_type="company")

    company, _ = CompanyModel.objects.get_or_create(company=user, defaults={"company_name": "Test Company"})

    # Create a job for TODAY
    today = timezone.now().date()
    job_today = JobModel.objects.create(
        job_provider=company,
        job_title="Test Job Today",
        job_date=today,
        start_time="09:00",
        end_time="17:00",
        pay_rate=20.00
    )

    # Create a job for YESTERDAY
    yesterday = today - timedelta(days=1)
    job_yesterday = JobModel.objects.create(
        job_provider=company,
        job_title="Test Job Yesterday",
        job_date=yesterday,
        start_time="09:00",
        end_time="17:00",
        pay_rate=20.00
    )

    # Create engagements
    candidate_email = "guard_test_weekly_v1@example.com"
    if CustomUser.objects.filter(email=candidate_email).exists():
        candidate = CustomUser.objects.get(email=candidate_email)
    else:
        candidate = CustomUser.objects.create_user(email=candidate_email, password="password", user_type="guard")

    app, _ = JobApplications.objects.get_or_create(candidate=candidate)

    EngagementModel.objects.create(job_details=job_today, application=app)
    EngagementModel.objects.create(job_details=job_yesterday, application=app)

    # Run logic from view
    week_data = []
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    
    # Logic from views.py
    start_of_week = today - timedelta(days=today.weekday()) # Monday of current week
    current_day_date = start_of_week

    print(f"Today: {today}")
    print(f"Start of week (Mon): {start_of_week}")

    for i in range(7):
        day_count = EngagementModel.objects.filter(
            job_details__job_provider=company,
            job_details__job_date=current_day_date,
            is_deleted=False
        ).count()
        
        day_name = days[current_day_date.weekday()]
        print(f"Day: {day_name} ({current_day_date}): {day_count}")
        
        week_data.append({
            "day": day_name,
            "value": day_count,
            "date": current_day_date.strftime("%Y-%m-%d")
        })
        current_day_date += timedelta(days=1)

    print("\nWeek Data:", week_data)

if __name__ == "__main__":
    run_test()
