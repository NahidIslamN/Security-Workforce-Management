from rest_framework import serializers
from api.models import *

# write your serializer


from api.serializers import LicenceSerializer

class UserSerializers(serializers.ModelSerializer):
    licences = LicenceSerializer(many=True, read_only=True)
    class Meta:
        model = CustomUser
        fields = ['id','email','licences']
    



class CompanyinfoSerializer(serializers.ModelSerializer):
    company = UserSerializers(read_only=True)  # show but not editable

    class Meta:
        model = CompanyModel
        fields = [
            "id",
            "company_name",
            "company",
            "phone_number",
            "address",
            "state",
        ]

    def update(self, instance, validated_data):
        # Simply ignore 'company' if present
        validated_data.pop('company', None)

        # Update all other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance



class UserProfileUpdateSerializers(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "first_name",
            "email",
            "phone",
            "image",
            "gender",
            "language",
            "exprience_in_years",
            "exprience_summary",
            "address",
            "user_redus",
            "bank_name",
            "account_holder_name",
            "account_no",
            "bank_branch",
            'is_email_varified',

            "tax_file_number",
            "fund_name",
            "fund_usi",
            "sup_member_no",
            "date_of_birth",
            "latitude",
            "longitude"

        ]
    
    def update(self, instance, validated_data):
        email = validated_data.get('email', None)
        if email is not None:
            if instance.email == email:
                pass
            else:
                instance.is_email_varified = False
                instance.save()
        return super().update(instance, validated_data)
    




class GetMy_card_info(serializers.ModelSerializer):
    class Meta:
        model = BankCardinfo
        fields = [
            'id',
            'card_holder',
            'card_number',
            'expire_date',
            'cvc',
            'billing_address'
        ]



#################################licence and Certificate create and updates######################




class LicencesCreateUpdateSerializers(serializers.ModelSerializer):
    licence_images = serializers.ListField(
        child=serializers.ImageField(),  # Accept multiple images
        write_only=True
    )

    class Meta:
        model = LicencesModel
        fields = ["state_or_territory", "licence_type", "licence_images", "licence_no", "expire_date"]

    def create(self, validated_data):
        images_data = validated_data.pop('licence_images', [])
        licence = LicencesModel.objects.create(**validated_data)

        for image in images_data:
            img_obj = Images.objects.create(file=image)  # Assuming Images model has 'image' field
            licence.licence_images.add(img_obj)

        return licence

    def update(self, instance, validated_data):
            images_data = validated_data.pop('licence_images', None)

            # Update other fields
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            if images_data is not None:
                # Optional: clear old images if you want to replace them
                licences = instance.licence_images.all()
                for licence in licences:
                    licence.file.delete(save=False)
                    licence.delete()

                for image in images_data:
                    img_obj = Images.objects.create(file=image)
                    instance.licence_images.add(img_obj)

            return instance

from api.serializers import AccumandationSerializer



class UserProfileSerialiser(serializers.ModelSerializer):
    accreditations = AccumandationSerializer(many=True)
    licences = LicenceSerializer(many=True)
    
    class Meta:
        model = CustomUser
        fields = [
                "id",
                "email",
                "first_name",
                "phone",
                "is_email_varified",
                "image",
                "user_type",

                "gender",
                "language",
                "exprience_in_years",
                "exprience_summary",
                "address",
                "user_redus",

                "bank_name",
                "account_holder_name",
                "account_no",
                "bank_branch",
                "accreditations",
                "licences",


                "tax_file_number",
                "fund_name",
                "fund_usi",
                "sup_member_no",
                "date_of_birth",

                "is_subscribe",

            ]



class InvoicesSerializers(serializers.ModelSerializer):
    class Meta:
        model = Invoices
        exclude = ['user']
        depth=1


class ReferralListSerializeer(serializers.ModelSerializer):
    
    class Meta:
        model = CustomUser
        fields = [
                "id",
                "email",
                "first_name",
                "phone",
                "is_email_varified",
                "user_type",
                "is_subscribe",
                "is_earned",
                "gender",
                "language",
                "address",
                "create_at"

            ]





