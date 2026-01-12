



from rest_framework import serializers
from api.models import *



class JobModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobModel
        fields = [
            'id',
            "job_provider",
            "job_title",
            "job_role",
            "latitude",
            "longitude",
            "address",
            "job_date",
            "job_expire",
            "start_time",
            "end_time",
            "job_duration",
            "pay_type",
            "pay_rate",
            "operative_required",
            "licence_type_requirements",
            "min_rating_requirements",
            "accreditations_requirements",
            "is_preferred_guard",
            "gender_requirements",
            "language_requirements",
            "status",
            "engagement_type",
            "provident_fund",
            "job_details",
            "is_application_complete",
            'created_at',
            'updated_at'
        ]

        read_only_fields = ['id', 'created_at', 'updated_at']




class UserSerialzars(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "first_name",
            "email",
            "is_email_varified",
            "create_at",
            "updated_at",
            "image",
            "last_activity",
            "user_type",
            "gender",
            "is_admin_aproved",
            "is_admin_rejected",
            "is_subscribe",
            "exprience_in_years",
            "create_at",
        ]
        read_only_fields = ['id', 'create_at']

class LicenceSerializers(serializers.ModelSerializer):
    class Meta:
        model = LicencesModel
        fields = "__all__"
        depth =1
    

class CertificateSerializers(serializers.ModelSerializer):
    class Meta:
        model = CertificateModel
        fields = "__all__"
        depth =1


class UserSerialzarsPO(serializers.ModelSerializer):
    licences = LicenceSerializers(many=True, read_only=True)
    accreditations = CertificateSerializers(many=True, read_only=True)
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "first_name",
            "email",
            "phone",
            "is_email_varified",
            "create_at",
            "updated_at",
            "image",
            "last_activity",
            "user_type",
            "gender",
            "is_admin_aproved",
            "is_admin_rejected",
            "is_subscribe",
            "exprience_in_years",
            "licences",
            "accreditations",
            "bank_name",
            "account_holder_name",
            "account_no",
            "bank_branch",
            "create_at"
        ]
        depth=1
        read_only_fields = ['id', 'create_at']  



class JobProviderSerialzer(serializers.ModelSerializer):
    company = UserSerialzarsPO()
    class Meta:
        model = CompanyModel
        fields =[        
            "id",
            "company",

            "company_name",
            "phone_number",
            'abn_number',
            
            "average_rating_main",
            "average_comunication",
            "average_reliability",
            "average_pay_rate",
            "average_professionalism",
            "average_job_support"
        ]



########## company serializers ##########


class JobApplicationsSerializer(serializers.ModelSerializer):
    candidate = UserSerialzarsPO()
    class Meta:
        model = JobApplications
        fields = [
            "id",
            "status",
            "candidate",
            "currency",
            "is_admin_aproved",
            "avg_rating_main",
            "avg_presentation_grooming",
            "avg_communication",
            "avg_reports_administration",
            "avg_punctuality_reliability",
            "avg_skills_attributes",
        ]




class JobModelDetailsCompanyPointSerializer(serializers.ModelSerializer):
    applications = JobApplicationsSerializer(many=True)
    selected_list = JobApplicationsSerializer(many=True)
    job_provider = JobProviderSerialzer()
   
    class Meta:
        model = JobModel
        fields = [
            'id',
            "applications",
            "job_provider",
            "selected_list",
            "job_title",
            "latitude",
            "longitude",
            "address",
            "job_date",
            "start_time",
            "end_time",
            "job_duration",
            "pay_type",
            "pay_rate",
            "operative_required",
            "licence_type_requirements",
            "min_rating_requirements",
            "accreditations_requirements",
            "is_preferred_guard",
            "gender_requirements",
            "language_requirements",
            "status",
            "engagement_type",
            "provident_fund",
            "job_details",
            'created_at',
            'updated_at'
        ]

        read_only_fields = ['id', 'created_at', 'updated_at', 'applications', 'selected_list']




class JobModelDetailsCompanyPointSerializerGurd(serializers.ModelSerializer):
    job_provider = JobProviderSerialzer()
   
    class Meta:
        model = JobModel
        fields = [
            'id',
            "job_provider",
            "job_title",
            "latitude",
            "longitude",
            "address",
            "job_date",
            "start_time",
            "end_time",
            "job_duration",
            "pay_type",
            "pay_rate",
            "operative_required",
            "licence_type_requirements",
            "min_rating_requirements",
            "accreditations_requirements",
            "is_preferred_guard",
            "gender_requirements",
            "language_requirements",
            "status",
            "engagement_type",
            "provident_fund",
            "job_details",
            'created_at',
            'updated_at'
        ]

        read_only_fields = ['id', 'created_at', 'updated_at']



class JobModelDetailsGuardSerializer(serializers.ModelSerializer):
    job_provider = JobProviderSerialzer()

    class Meta:
        model = JobModel
        fields = [
            'id',
            "job_title",
            "job_provider",
            "latitude",
            "longitude",
            "address",
            "job_date",
            "start_time",
            "end_time",
            "job_duration",
            "pay_type",
            "pay_rate",
            "operative_required",
            "licence_type_requirements",
            "min_rating_requirements",
            "accreditations_requirements",
            "is_preferred_guard",
            "gender_requirements",
            "language_requirements",
            "status",
            "engagement_type",
            "provident_fund",
            "job_details",
            'created_at',
            'updated_at'
        ]

        read_only_fields = ['id', 'created_at', 'updated_at']


# EngageMent Model Serialisers for update
class EngagementModelSerializersUpdate(serializers.ModelSerializer):
    class Meta:
        model=EngagementModel
        fields = [
            'id',       
            'new_end_time',
            'new_job_duration',
            'total_amount',
            'signature_party_a',
            'signature_party_b'
            ]
        
        read_only_fields = ['id', 'created_at', 'updated_at']



#engangement model serializers for view details
class EngagementModelSerializersViews(serializers.ModelSerializer):
    job_details = JobModelDetailsCompanyPointSerializer(read_only=True)
    application = JobApplicationsSerializer(read_only=True)
    
    class Meta:
        model=EngagementModel
        fields = [
            'id',
            'job_details',
            'application',
            'operative_trackers',
            'contacts_trackers', 
            'amend_trackers',
            'amend_details',
            'new_end_time',
            'total_amount',
            'new_job_duration',
            
            'signature_party_a',
            'signature_party_b',
            "created_at",
            ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'job_details', 'application']





#engangement model serializers for view details
class EngagementModelSerializersViewsGurd(serializers.ModelSerializer):
    job_details = JobModelDetailsCompanyPointSerializerGurd(read_only=True)
    application = JobApplicationsSerializer(read_only=True)
    
    class Meta:
        model=EngagementModel
        fields = [
            'id',
            'job_details',
            'application',
            'operative_trackers',
            'contacts_trackers', 
            'amend_trackers',
            'amend_details',
            'new_end_time',
            'total_amount',
            'new_job_duration',
            
            'signature_party_a',
            'signature_party_b'
            ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'job_details', 'application']









class OperativeTrackerjobDetailsSerializer(serializers.ModelSerializer):
   
   
    class Meta:
        model = JobModel
        fields = [
            'id',
            "job_title",
            "latitude",
            "longitude",
            "address",
            "job_date",
            "start_time",
            "end_time",
            "job_duration",
            "pay_type",
            "pay_rate",
            "operative_required",
            "licence_type_requirements",
            "min_rating_requirements",
            "accreditations_requirements",
            "is_preferred_guard",
            "gender_requirements",
            "language_requirements",
            "status",
            "engagement_type",
            "provident_fund",
            "job_details",
            'created_at',
            'updated_at'
        ]

        read_only_fields = ['id', 'created_at', 'updated_at']

#engangement model serializers for view details
class OperativeTrackersSerializersViews(serializers.ModelSerializer):
    job_details = OperativeTrackerjobDetailsSerializer(read_only=True)
    application = JobApplicationsSerializer(read_only=True)
    
    class Meta:
        model=EngagementModel
        fields = [
            'id',
            'job_details',
            'application',
            'operative_trackers',
            'contacts_trackers', 
            'amend_trackers',
            'amend_details',
            'job_details', 
            'new_end_time',
            'total_amount',
            'new_job_duration',
            "is_shift_end",
            "is_company_reted",
            'signature_party_a',
            'signature_party_b'
            ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'job_details', 'application']



class PayrolJobDetailsSerializer(serializers.ModelSerializer):
     
    class Meta:
        model = JobModel
        fields = [
            'id',
            "job_date",
            "start_time",
            "end_time",
            "job_duration",
            "provident_fund",
            "job_details",
            'pay_rate',
            'created_at',
            'updated_at'
        ]

        read_only_fields = ['id', 'created_at', 'updated_at']


class Payroll_Management_SerializersViews(serializers.ModelSerializer):
    job_details = PayrolJobDetailsSerializer(read_only=True)
    application = JobApplicationsSerializer(read_only=True)
    
    class Meta:
        model=EngagementModel
        fields = [
            'id',
            'job_details',
            'application',
            'operative_trackers',
            'contacts_trackers', 
            'amend_trackers',
            'amend_details',
            'new_end_time',
            'total_amount',
            'new_job_duration',
            'signature_party_a',
            'signature_party_b'
            ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'job_details', 'application']





#engangement model serializers for view details
class PerpormedOperativesSerializersViews(serializers.ModelSerializer):
    application = JobApplicationsSerializer(read_only=True)
    note = serializers.SerializerMethodField()
    
    class Meta:
        model=EngagementModel
        fields = [
            'id',
            'application',
            'operative_trackers',
            'contacts_trackers', 
            'amend_trackers',
            'amend_details',
            'job_details', 
            'new_end_time',
            'total_amount',
            'new_job_duration',
            
            'signature_party_a',
            'signature_party_b',
            'note'
            ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'application']

    def get_note(self, obj):
        try:
            company = obj.job_details.job_provider
            operative = obj.application.candidate
            note_obj = OperativeNote.objects.filter(company=company, operative=operative).last()
            return note_obj.note if note_obj else ""
        except:
            return ""



class CompanyEngUpdateSerializer(serializers.Serializer):
    pay_rate = serializers.FloatField(required=False, allow_null=True)
    new_end_time = serializers.TimeField(required=False, allow_null=True)
    detail_amendment = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    signature_party_a = serializers.ImageField(required=False, allow_null=True)
    is_shift_end = serializers.BooleanField(required=False, allow_null=True)
    paid_a_gaurd = serializers.BooleanField(required=False, allow_null=True)


class GaurdEngUpdateSerializer(serializers.Serializer):
    start_shift = serializers.BooleanField(required=False, allow_null=True)
    end_shift = serializers.BooleanField(required=False, allow_null=True)
    signature_party_b = serializers.ImageField(required=False, allow_null=True)



class EmandSerialzers(serializers.Serializer):
    accept = serializers.BooleanField(required=False, allow_null=True)
    rejected = serializers.BooleanField(required=False, allow_null=True)






################### for gaurd#####################

class JobModelDetailsSerializer(serializers.ModelSerializer):
    job_provider = JobProviderSerialzer()

    class Meta:
        model = JobModel
        fields = [
            'id',
            "job_provider",
            "job_title",
            "job_role",
            "latitude",
            "longitude",
            "address",
            "job_date",
            "job_expire",
            "start_time",
            "end_time",
            "job_duration",
            "pay_type",
            "pay_rate",
            "operative_required",
            "licence_type_requirements",
            "min_rating_requirements",
            "accreditations_requirements",
            "is_preferred_guard",
            "gender_requirements",
            "language_requirements",
            "status",
            "engagement_type",
            "provident_fund",
            "job_details",
            'created_at',
            'updated_at'
        ]

        read_only_fields = ['id', 'created_at', 'updated_at']






class EngagementModelGuardSerializersViews(serializers.ModelSerializer):
    job_details = JobModelDetailsGuardSerializer(read_only=True)
   
    class Meta:
        model=EngagementModel
        fields = [
            'id',
            'job_details',
            'operative_trackers',
            'contacts_trackers', 
            'amend_trackers',
            'amend_details',
            'job_details', 
            'new_end_time',
            'total_amount',
            'new_job_duration',
            
            'signature_party_a',
            'signature_party_b'
            ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'job_details', 'application']









# rating system serializers


class Company_Rating_Serializers(serializers.ModelSerializer):
    class Meta:
        model=ComapnyRating
        fields =[
            'comunication',
            'reliability',
            'pay_rate',
            'professionalism',
            'job_support',
            'text'
        ]


class Guard_Rating_Serializers(serializers.ModelSerializer):
    class Meta:
        model=GaurdRating
        fields = [
            'presentation_grooming',
            'communication',
            'reports_administration',
            'punctuality_reliability',
            'skills_attributes',
            'text'
        ]

    


from api.models import LicencesType

class LicenceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LicencesType
        fields = [
            "id",
            "title"
        ]

class CertificateTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateType
        fields = [
            "id",
            "title"
        ]
class SupportMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = SupportMessage
        fields = ['id', 'full_name', 'email', 'message', 'created_at']
