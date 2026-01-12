from rest_framework import serializers
from .models import *




class UsermodelSignupSerializer(serializers.ModelSerializer): # Serializer for Create User object
    class Meta:
        model = CustomUser
        fields = ['first_name','email', 'password','user_type']

    def create(self, validated_data):
        user = CustomUser.objects.create(
            first_name = validated_data['first_name'],
            email = validated_data['email'],
            user_type = validated_data['user_type']
        )
              
        user.set_password(validated_data['password'])
        user.save()
        return (validated_data)
     
    
class OTPSerializer(serializers.Serializer): # serializer for veryfy otp
    otp = serializers.CharField()

class OTPSerializerandPasswword(serializers.Serializer): # serializer for veryfy otp
    otp = serializers.CharField()
    password = serializers.CharField()

class LoginSerializers(serializers.Serializer):
    email = serializers.CharField()
    password = serializers.CharField()

class ChangePassword_serializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

class ForgetPasswordSerializer(serializers.Serializer):
    email = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField()


# bank info serializer

from .models import  CompanyModel, LicencesModel, Images


class StaticFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = ["file"]
    

class LicenceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        models = LicencesType
        fields = ["id", "title"]
        

class LicenceSerializer(serializers.ModelSerializer):
    licence_images = StaticFileSerializer(many=True, read_only=True)
    # licence_type = LicenceTypeSerializer(read_only=True)
    class Meta:
        model = LicencesModel
        fields = [
            "id",
            "licence_type",
            "licence_no",
            "licence_images",
            "state_or_territory",
            "expire_date"
        ]


class LicenceSerializerView(serializers.ModelSerializer):
    licence_images = StaticFileSerializer(many=True, read_only=True)
    
    class Meta:
        model = LicencesModel
        fields = [
            "id",
            "licence_type",
            "licence_no",
            "licence_images",
            "state_or_territory",
            "expire_date"
        ]
        depth = 1
        



class AccumandationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateModel
        fields = "__all__" 

from user_profile.serializers import UserSerializers

class CompanyinfoSerializer(serializers.ModelSerializer):
    company = UserSerializers() 
    class Meta:
        model = CompanyModel
        fields = [
            "id",
            "company_name",
            "phone_number",
            "company",
            'state',       
        ]


##########################gard serializer###################

class AccreditationsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CertificateModel
        fields = ['id','accreditation_type', 'accreditation', 'expire_date']

    
    def update(self, instance, validated_data):
        image = validated_data.get('accreditation', None)
        if image is not None:
            instance.accreditation.delete(save=False)
            instance.save()
        return super().update(instance, validated_data)

class AccreditationsSerializerView(serializers.ModelSerializer):
    class Meta:
        model = CertificateModel
        fields = ['id','accreditation_type', 'accreditation', 'expire_date']
        depth = 1



class UserSerializersGurdinfo(serializers.ModelSerializer):
    licences = LicenceSerializer(many=True, read_only=True)
    accreditations = AccreditationsSerializer(many=True, read_only=True)
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "first_name",
            "email",
            "phone",
            "user_type",
            "image",
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
            "is_subscribe"
        ]

class Gurd_Application_Details(serializers.ModelSerializer):
    candidate = UserSerializersGurdinfo()
    class Meta:
        model = JobApplications
        fields = ['id','candidate']

        
    
class SubPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubscribtionPlan
        fields = "__all__"