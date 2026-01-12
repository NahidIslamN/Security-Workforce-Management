from managements.serializers import UserSerialzars

from api.models import *
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers


class InvoicesSerializers(ModelSerializer):
    user = UserSerialzars()
    class Meta:
        model = Invoices
        fields = [
            'id',
            'user',
            'invoice_date',
            'plan',
            'price',
            'end_date',
            'is_finished',
            'is_earned',
            'created_at',
            'updated_at'
        ]

    

class UserDetailsSerializer(ModelSerializer):
   
    class Meta:
        model=CustomUser
        fields = [
            "id",
            "email",
            "status",
            "phone",
            "is_email_varified",
            "is_phone_verified",
            "image",
            "last_activity",
            "latitude",
            "longitude",
            "user_type",
            "licences",
            "accreditations",
            "gender",
            "language",
            "exprience_in_years",
            "exprience_summary",
            "user_redus",
            "bank_name",
            "account_holder_name",
            "account_no",
            "bank_branch",
            "is_applied",
            "is_admin_aproved",
            "is_admin_rejected",
            "is_subscribe",
            "create_at",
            "updated_at",
        ]

        depth=1


class licence_serializer(ModelSerializer):
    class Meta:
        model=LicencesModel
        fields="__all__"
        depth=1



class UserDetailsSerializerVC(ModelSerializer):
    licences = licence_serializer(many=True, read_only=True)
   
    class Meta:
        model=CustomUser
        fields = [
            "id",
            "email",
            "status",
            "phone",
            "is_email_varified",
            "is_phone_verified",
            "image",
            "last_activity",
            "latitude",
            "longitude",
            "user_type",
            "licences",
            "accreditations",
            "gender",
            "language",
            "exprience_in_years",
            "exprience_summary",
            "user_redus",
            "bank_name",
            "account_holder_name",
            "account_no",
            "bank_branch",
            "is_applied",
            "is_admin_aproved",
            "is_admin_rejected",
            "is_subscribe",
            "create_at",
            "updated_at",
        ]

        depth=1






class CompanySerializer(ModelSerializer):
    company = UserDetailsSerializerVC()
    invoices = serializers.SerializerMethodField()
    class Meta:
        model=CompanyModel
        fields = [
            'company_name',
            'company',
            'average_rating_main',
            'invoices'
        ]

    def get_invoices(self, obj):
        invoices = Invoices.objects.filter(user=obj.company, is_deleted=False).order_by('-created_at')
        return InvoicesSerializers(invoices, many=True).data



class GuardSerializer(ModelSerializer):
    candidate = UserDetailsSerializerVC()
    class Meta:
        model=JobApplications
        fields = [
            'candidate',
            'avg_rating_main'
        ]



class UserDetailsSerializerJM(ModelSerializer):
   
    class Meta:
        model=CustomUser
        fields = [
            "id",
            "first_name",
        ]

        depth=1

class CompanyJobSerializer(ModelSerializer):
    company = UserDetailsSerializerJM()
    class Meta:
        model=CompanyModel
        fields = [
            'company',         
            'average_rating_main',
            
        ]
       


class JobSerializers(ModelSerializer):
    job_provider = CompanyJobSerializer()
    selected_list = serializers.SerializerMethodField()
    class Meta:
        model = JobModel
        fields = [
            'id',
            'job_title',
            'selected_list',
            'job_provider',
            'pay_rate',
            'job_duration',
            'is_application_complete',
            'created_at',
        ]

    def get_selected_list(self, obj):
        return obj.selected_list.count()




from rest_framework import serializers

class CompanyReportSerializer(serializers.Serializer):
    company_name = serializers.CharField()
    total_jobs = serializers.IntegerField()
    total_operatives = serializers.IntegerField()
    total_hours = serializers.FloatField()
    total_pay = serializers.FloatField()
    status = serializers.CharField()



class UserRefarralReportSerializer(serializers.Serializer):
    name = serializers.CharField()
    email_address = serializers.EmailField()
    total_raffaral = serializers.IntegerField()
    total_subscribtion = serializers.IntegerField()


class licence_serializer(serializers.ModelSerializer):
    class Meta:
        model=LicencesModel
        fields="__all__"
        depth=1

class UserDetailsSerializerVC(ModelSerializer):
    licences = licence_serializer(many=True, read_only=True)
   
    class Meta:
        model=CustomUser
        fields = [
            "id",
            "email",
            "status",
            "phone",
            "is_email_varified",
            "is_phone_verified",
            "image",
            "last_activity",
            "latitude",
            "longitude",
            "user_type",
            "licences",
            "accreditations",
            "gender",
            "language",
            "exprience_in_years",
            "exprience_summary",
            "user_redus",
            "bank_name",
            "account_holder_name",
            "account_no",
            "bank_branch",
            "is_applied",
            "is_admin_aproved",
            "is_admin_rejected",
            "is_subscribe",
            "create_at",
            "updated_at",
        ]

        depth=1


from managements.models import PaymentController


class PaymentControllerSerializer(ModelSerializer):
    class Meta:
        model = PaymentController
        fields = "__all__"



from rest_framework.serializers import ModelSerializer

class SubPlanSerializer(ModelSerializer):
    class Meta:
        model = SubscribtionPlan
        exclude = ['benefits']
