from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Avg
from django.contrib.auth.base_user import BaseUserManager
from decimal import Decimal
import uuid



# Create your models here.

class Images(models.Model):
    file = models.FileField(upload_to="licesces", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Image {self.created_at} - {self.updated_at}"


class LicencesType(models.Model):
    title = models.CharField(max_length=25)
    discription = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Licence type - {self.title}"


class LicencesModel(models.Model):
    state_or_territory = models.CharField(max_length=250, null=True, blank=True)
    licence_type = models.ForeignKey(LicencesType, related_name="licence_type", on_delete=models.CASCADE, null=True, blank=True)
    licence_no = models.CharField(max_length=250, unique=True, null=True, blank=True)
    licence_images = models.ManyToManyField(Images, blank=True)
    expire_date = models.DateField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Licence - {self.licence_no}"
    
    class Meta:
        ordering = ['-created_at']


class CertificateType(models.Model):
    title = models.CharField(max_length=25)
    discription = models.TextField()
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Certificate type - {self.title}"


class CertificateModel(models.Model):

    accreditation_type = models.ForeignKey(CertificateType, related_name="accreditation_type", on_delete=models.CASCADE, null=True, blank=True)
    accreditation = models.FileField(upload_to="accreditations")
    expire_date = models.DateField(null=True, blank=True, default=None)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Certificate - {self.accreditation_type}"


# ---------------- Custom User Manager ----------------
class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None
    USER_TYPE_CHOICES = (
        ("admin", "Admin"),
        ("company", "Security Company"),
        ("guard", "Security Guard"),
    )

    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=8, null=True, blank=True)
    status = models.BooleanField(default=False)

    phone = models.CharField(max_length=15, null=True, blank=True)
    is_email_varified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=True)

    create_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(null=True, blank=True, upload_to="profile")
    
    last_activity = models.DateTimeField(null=True, blank=True)

    latitude = models.FloatField(null=True, blank=True)    
    longitude = models.FloatField(null=True, blank=True)

    user_type = models.CharField(max_length=8, choices=USER_TYPE_CHOICES, default="guard")
    
    licences = models.ManyToManyField(LicencesModel, related_name='licences', blank=True)

    accreditations = models.ManyToManyField(CertificateModel, related_name='accreditations', blank=True)

    gender = models.CharField(max_length=100)
    language = models.CharField(max_length=250, null=True, blank=True)
    exprience_in_years = models.IntegerField(default=0)
    exprience_summary = models.TextField(blank=True)
    address = models.TextField(blank=True)
    user_redus = models.FloatField(default=10)

    #bank info
    bank_name = models.CharField(max_length=250, null=True, blank=True)
    account_holder_name = models.CharField(max_length=255, null=True, blank=True)
    account_no = models.CharField(max_length=250, unique=True, null=True, blank=True)
    bank_branch = models.CharField(max_length=250, null=True, blank=True)

    is_applied = models.BooleanField(default=False)
    is_admin_aproved = models.BooleanField(default=False)
    is_admin_rejected = models.BooleanField(default=False)
    is_subscribe = models.BooleanField(default=False)
    is_earned = models.BooleanField(default=False)

    is_deleted = models.BooleanField(default=False)



    tax_file_number = models.CharField(unique=True, null=True, blank=True)
    fund_name = models.CharField(null=True, blank=True)
    fund_usi = models.CharField(unique=True, null=True, blank=True)
    sup_member_no = models.CharField(unique=True, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)



    USERNAME_FIELD = "email"
    
    REQUIRED_FIELDS = []

    objects = CustomUserManager() 
    
    def __str__(self):
        return f"{self.email}"



class BankCardinfo(models.Model):
    card_holder_info = models.OneToOneField(CustomUser, on_delete=models.CASCADE, default=None, null=True, blank=True) 
    card_holder = models.CharField(max_length=250, null=True, blank=True)
    card_number = models.IntegerField(unique=True, null=True, blank=True)
    expire_date = models.CharField(null=True, blank=True)
    cvc = models.IntegerField(null=True, blank=True)
    billing_address = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"CardInfo - {self.card_number}"





class GaurdRating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    presentation_grooming = models.DecimalField(max_digits=5, decimal_places=2)
    communication = models.DecimalField(max_digits=5, decimal_places=2)
    reports_administration = models.DecimalField(max_digits=5, decimal_places=2)
    punctuality_reliability = models.DecimalField(max_digits=5, decimal_places=2)
    skills_attributes = models.DecimalField(max_digits=5, decimal_places=2)

    text = models.TextField()
    main_rating = models.DecimalField(max_digits=5, decimal_places=2)
 
    def save(self, *args, **kwargs):
        # Calculate average rating
        total = (
            Decimal(self.presentation_grooming) +
            Decimal(self.communication) +
            Decimal(self.reports_administration) +
            Decimal(self.punctuality_reliability) +
            Decimal(self.skills_attributes)
        )

        self.main_rating = total / Decimal(5)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Rating: {self.main_rating}"
    


 


class ComapnyRating(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)

    comunication =  models.DecimalField(max_digits=5, decimal_places=2)
    reliability  =  models.DecimalField(max_digits=5, decimal_places=2)
    pay_rate = models.DecimalField(max_digits=5, decimal_places=2)
    professionalism = models.DecimalField(max_digits=5, decimal_places=2)
    job_support = models.DecimalField(max_digits=5, decimal_places=2)
    text = models.TextField()
    main_rating = models.DecimalField(max_digits=5, decimal_places=2)

    
    def save(self, *args, **kwargs):
        # Calculate average rating
        total = (
            Decimal(self.comunication) +
            Decimal(self.reliability) +
            Decimal(self.pay_rate) +
            Decimal(self.professionalism) +
            Decimal(self.job_support)
        )

        self.main_rating = total / Decimal(5)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Rating: {self.main_rating}"
    


 

class JobApplications(models.Model):
    CURRENCY_CHOICES = (
        ('aud', 'AUD'),
        ('nzd', 'NZD'),
        ('pgk', 'PGK'),
        ('idr', 'IDR'),
        ('sgd', 'SGD'),
        ('myr', 'MYR'),
    )
    
    OPERATIVE_STATUS = (
        ("unavailable","Unavailable"),
        ('selected','selected'),
        ("tasked","Tasked"),
        ("untasked","Untasked"),   
    )

    status = models.CharField(max_length=100, choices=OPERATIVE_STATUS, default='unavailable')
    candidate = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default="aud")
    refaral_users = models.ManyToManyField(CustomUser, related_name='refaral_users')
    refaral_token = models.CharField(max_length=25, unique=True, null=True, blank=True)
    is_admin_aproved = models.BooleanField(default=False)


    # for rating
    rating = models.ManyToManyField(GaurdRating, related_name='operative_ratings', blank=True)   

    avg_rating_main = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    avg_presentation_grooming = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    avg_communication = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    avg_reports_administration = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    avg_punctuality_reliability = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    avg_skills_attributes = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    def generate_referral_token(self):
        """Generate a unique token"""
        return uuid.uuid4().hex[:12]

    def update_average_rating(self):

        if not self.pk:
            return 


        averages = self.rating.aggregate(
            avg_main=Avg('main_rating'),
            avg_presentation_grooming=Avg('presentation_grooming'),
            avg_communication=Avg('communication'),
            avg_reports_administration=Avg('reports_administration'),
            avg_punctuality_reliability=Avg('punctuality_reliability'),
            avg_skills_attributes=Avg('skills_attributes'),
        )

        self.avg_rating_main = round(averages['avg_main'] or 0, 2)
        self.avg_presentation_grooming = round(averages['avg_presentation_grooming'] or 0, 2)
        self.avg_communication = round(averages['avg_communication'] or 0, 2)
        self.avg_reports_administration = round(averages['avg_reports_administration'] or 0, 2)
        self.avg_punctuality_reliability = round(averages['avg_punctuality_reliability'] or 0, 2)
        self.avg_skills_attributes = round(averages['avg_skills_attributes'] or 0, 2)

        return self.avg_rating_main

    def save(self, *args, **kwargs):
        # Generate referral token only when object is first created
        if not self.refaral_token:
            self.refaral_token = self.generate_referral_token()

        # Update averages before saving
        self.update_average_rating()

        super().save(*args, **kwargs)


    def __str__(self):
        return f"Candidate - {self.id}"


    

class CompanyModel(models.Model):
    CURRENCY_CHOICES = (
        ('aud', 'AUD'),
        ('nzd', 'NZD'),
        ('pgk', 'PGK'),
        ('idr', 'IDR'),
        ('sgd', 'SGD'),
        ('myr', 'MYR'),
    )
    company_name = models.CharField(max_length=250, null=True, blank=True) 
    phone_number=models.CharField(max_length=20, null=True, blank=True)   
    company = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    currency = models.CharField(max_length=10, choices=CURRENCY_CHOICES, default="aud")
    abn_number = models.IntegerField(unique=True, null=True, blank=True) #company abn number

    state = models.CharField(max_length=250, null=True, blank=True)
    address = models.TextField(blank=True)
    

    PreferredOperatives = models.ManyToManyField(JobApplications, related_name='preferredoperatives', blank=True)
    

    # for rating
    rating = models.ManyToManyField(ComapnyRating, related_name='company_ratings', blank=True)

    average_rating_main = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    average_comunication = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    average_reliability = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    average_pay_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    average_professionalism = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    average_job_support = models.DecimalField(max_digits=5, decimal_places=2, default=0)

    refaral_users = models.ManyToManyField(CustomUser, related_name='refaral_users_company', blank=True)
    refaral_token = models.CharField(max_length=25, unique=True, null=True, blank=True)
    

    def generate_referral_token(self):
        """Generate a unique token"""
        return uuid.uuid4().hex[:12]
    

    def update_average_rating(self):
        
        if not self.pk:
            return 

        averages = self.rating.aggregate(
            avg_main=Avg('main_rating'),
            avg_comunication=Avg('comunication'),
            avg_reliability=Avg('reliability'),
            avg_pay_rate=Avg('pay_rate'),
            avg_professionalism=Avg('professionalism'),
            avg_job_support=Avg('job_support')
        )

        self.average_rating_main = round(averages.get('avg_main') or 0, 2)
        self.average_comunication = round(averages.get('avg_comunication') or 0, 2)
        self.average_reliability = round(averages.get('avg_reliability') or 0, 2)
        self.average_pay_rate = round(averages.get('avg_pay_rate') or 0, 2)
        self.average_professionalism = round(averages.get('avg_professionalism') or 0, 2)
        self.average_job_support = round(averages.get('avg_job_support') or 0, 2)

        return self.average_rating_main


    def save(self, *args, **kwargs):
        # Generate referral token only when object is first created
        if not self.refaral_token:
            self.refaral_token = self.generate_referral_token()
        # update averages before saving in DB
        self.update_average_rating()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Company - {self.company_name} - {self.average_rating_main}"
    
from django.utils import timezone
from datetime import timedelta
class JobModel(models.Model):
    PAYTYPE_CHOICES = (
        ("nominated", "Nominated"),
        ("award", "Award"),
        ("negotiation", "By Negotiation"),
    )
    RATING_REQUIREMENTS = (
        (0,0),
        (1,1),
        (2,2),
        (3,3),
        (4,4),
        (5,5)
    )
    YES_NO_CHOICES = (
        ('yes',"Yes"),
        ('no',"No")
    )
    GENDER_CHOICES = (
        ("male","Male"),
        ("female","Female"),
        ("other","Other")
    )
    STATUS_CHOICES = (
        # ('pushed', 'Pushed'),
        ('published', 'Published'),
        ('untasked', 'Untasked'),
        ('tasked', 'Tasked'),
        ('finished', 'Finished'),
    )
    ENGAGEMENT_TYPE_CHOICE = (
        ('casual', "Casual"),
        ('part-time', "Part-Time"),
        ('permanent', "Permenent")
    )

    #job info   
    job_provider = models.ForeignKey(CompanyModel, on_delete=models.CASCADE)
    applications = models.ManyToManyField(JobApplications, related_name='applications', blank=True)
    selected_list = models.ManyToManyField(JobApplications, related_name='selected_applications', blank=True)

    job_title = models.CharField(max_length=250)
    job_role = models.CharField(max_length=250, null=True, blank=True)

    latitude = models.FloatField(null=True, blank=True)   #for job location 
    longitude = models.FloatField(null=True, blank=True) #for job location
    address = models.TextField(blank=True)

    job_date = models.DateField()
    job_expire = models.DateField(null=True, blank=True)

    start_time = models.TimeField()
    end_time = models.TimeField()
    job_duration = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    pay_type = models.CharField(max_length=11, choices=PAYTYPE_CHOICES, default="negotiation")
    pay_rate = models.DecimalField(max_digits=6,decimal_places=2 )
    
    #requirements
    operative_required = models.IntegerField(default=0)
    licence_type_requirements = models.ForeignKey(LicencesType, on_delete= models.CASCADE, null=True, blank=True)
    min_rating_requirements = models.IntegerField(choices=RATING_REQUIREMENTS, default=0)
    accreditations_requirements = models.ForeignKey(CertificateType, on_delete=models.CASCADE, null=True, blank=True)
    is_preferred_guard = models.CharField(max_length=3, choices=YES_NO_CHOICES, default="no")    
    gender_requirements = models.CharField(max_length=10, choices=GENDER_CHOICES, default="male")
    language_requirements = models.CharField(max_length=250, default="english")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="published")

    #engangement type
    engagement_type = models.CharField(max_length=100, choices=ENGAGEMENT_TYPE_CHOICE, default='casual')
    provident_fund = models.IntegerField(default=0)
    job_details = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_deleted = models.BooleanField(default=False)
    is_application_complete = models.BooleanField(default=False)

    def __str__(self):
        return f"Job-{self.id} {self.job_title}"



class EngagementModel(models.Model):
    AMED_STATUS = (
        ("not_amend","Not Amend"),
        ("pending","Pending"),
        ("accepted","Accepted"),
        ('rejected',"Rejected")
    )
    OPERATIVE_STATUS = (
        ('notstartyet',"Not Start Yet"),
        ('on_duty',"On Duty"),
        ('shift_completed',"Shift Completed")
    )

    ENGAGEMENT_STATUS = (
        ("pending","Processing"),
        ("cancelled", "Cancelled"),
        ('is_signed',"Signed"),
        ("not_pay","Not Pay"),
        ("completed","Completed Everything")
    )


    operative_trackers = models.CharField(max_length=100, choices=OPERATIVE_STATUS, default="notstartyet")

    contacts_trackers = models.CharField(max_length=100, choices=ENGAGEMENT_STATUS, default='pending')

    amend_trackers = models.CharField(max_length=100, choices=AMED_STATUS, default='not_amend')
    amend_details = models.TextField(blank=True)
    
    job_details = models.ForeignKey(JobModel, on_delete=models.CASCADE)
    
    application = models.ForeignKey(JobApplications, on_delete=models.CASCADE)
    
    new_end_time = models.TimeField(null=True, blank=True, default=None)
    new_job_duration = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
   
    total_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)

    signature_party_a = models.ImageField(upload_to="signutures", null=True, blank=True)
    signature_party_b = models.ImageField(upload_to="signutures", null=True, blank=True)



    is_deleted = models.BooleanField(default=False)  

    is_deleted_perfomed_operatives = models.BooleanField(default=False)

    is_company_reted = models.BooleanField(default=False)
    is_guard_reted = models.BooleanField(default=False)

    is_shift_end = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def calculate_total_pay(self):
        old_duration = self.job_details.job_duration or 0
        new_duration = self.new_job_duration or 0
        pay_rate = self.job_details.pay_rate or 0

        total_durations = old_duration + new_duration 
        return total_durations * pay_rate

    def save(self, *args, **kwargs):
        self.total_amount = self.calculate_total_pay()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Engagement for {self.job_details.job_title} - Total: {self.total_amount}"






######################## subscription plan ############

from django.core.exceptions import ValidationError

class Benefits(models.Model):
    text = models.TextField()


class SubscribtionPlan(models.Model):
    PLNAN_CHOICES = (
        ('company',"Company"),
        ('guard',"Operatives"),

    )
    duraton_day = models.IntegerField(default=30)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discriptions = models.TextField()
    benefits = models.ManyToManyField(Benefits,related_name='benefits', blank=True)

    plan_for = models.CharField(max_length=100, choices=PLNAN_CHOICES, default='guard')    

    def delete(self, *args, **kwargs):
        # Prevent deletion anywhere
        raise ValidationError("Deletion is not allowed for this object.")

    def __str__(self):
        return f"Subscrib Plan {self.price}-{self.duraton_day}"




class Invoices(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    invoice_date = models.DateField()
    plan = models.ForeignKey(SubscribtionPlan, on_delete=models.CASCADE, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    end_date = models.DateField(null=True, blank=True)
    is_finished = models.BooleanField(default=False)
    is_earned = models.BooleanField(default=False)

    is_deleted = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):

        return f"Invoice - {self.id}-{self.end_date}"









class SupportMessage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    full_name = models.CharField(max_length=250)
    email = models.EmailField()
    message = models.TextField(default="")
    created_at = models.DateField(auto_now_add=True)
    
    def __str__(self):

        return f"SupportMessage - {self.id}-{self.created_at}"



    




class OperativeNote(models.Model):
    company = models.ForeignKey(CompanyModel, on_delete=models.CASCADE, related_name='operative_notes')
    operative = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='notes_from_companies')
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Note for {self.operative} by {self.company}"
