from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.models import *
from .serializers import *

from rest_framework.permissions import IsAuthenticated
from chat_app.tasks import sent_note_to_user
from SecurityGuard.custom_permissions import IsCompany

# Create your views here.






class MyProfileData(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        serializer = UserProfileSerialiser(user)
        return Response({"success":True, "message":"data fatched", "data":serializer.data}, status=status.HTTP_200_OK)


class Myrefarral_link(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        referral_code = None
        if user.user_type =="guard":
            referral_code = JobApplications.objects.get(candidate=user).refaral_token
        elif user.user_type =="company":
            referral_code = CompanyModel.objects.get(company=user).refaral_token
        
        if referral_code is not None:
            return Response({"success":True, "message":"code fatched !", "code":referral_code}, status=status.HTTP_200_OK)
        else:
            return Response({"success":False, "message":"somthing want to worng !", }, status=status.HTTP_400_BAD_REQUEST)



class Myrefarral_User(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        referral_users = None
        if user.user_type =="guard":
            referral_users = JobApplications.objects.get(candidate=user).refaral_users.all()
        elif user.user_type =="company":
            referral_users = CompanyModel.objects.get(company=user).refaral_users.all()

        serializer = ReferralListSerializeer(referral_users, many=True)

        if referral_users is not None:
            return Response({"success":True, "message":"code fatched !", "users":serializer.data}, status=status.HTTP_200_OK)
        
        else:
            return Response({"success":False, "message":"somthing want to worng !", }, status=status.HTTP_400_BAD_REQUEST)

    
   





class MycompanyDetails(APIView):
    permission_classes = [IsCompany]
    def get(self, request):
        company_data,create = CompanyModel.objects.get_or_create(company = request.user)
        serializer = CompanyinfoSerializer(company_data)
        return Response({"success":True, "message":"data fatched", "data":serializer.data}, status=status.HTTP_200_OK)
    
    def put(self, request):
        company_data,create = CompanyModel.objects.get_or_create(company = request.user)
        serializer = CompanyinfoSerializer(instance=company_data, data= request.data)
        if serializer.is_valid():
            user = request.user
            user.first_name = serializer.validated_data.get("company_name")
            user.save()
            serializer.save()
            return Response({"success":True, "message":"update successfull", "data":serializer.data}, status=status.HTTP_200_OK)
        else:
            return Response({"success":False, "message":"validation errors", "errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)



class UserProfileChangeView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request):
        serialiser = UserProfileUpdateSerializers(instance = request.user, data = request.data, partial=True)
        if serialiser.is_valid():
            serialiser.save()

            # Notify user about profile update
            sent_note_to_user.delay(user_id=request.user.id, title=f"Profile Updated", content=f"Your profile has been updated successfully", note_type='success')
            return Response({"success":True, "message":"data fatched", "data":serialiser.data}, status=status.HTTP_200_OK)
        else:
            return Response({'success':False,"message":"validation errors", "errors":serialiser.errors}, status=status.HTTP_400_BAD_REQUEST)
        
    
class Location_update(APIView):
    permission_classes = [IsAuthenticated]
    def put(self, request):
        serialiser = UserProfileUpdateSerializers(instance = request.user, data = request.data, partial=True)
        if serialiser.is_valid():
            serialiser.save()

            return Response({"success":True, "message":"location set successfully!"}, status=status.HTTP_200_OK)
        else:
            return Response({'success':False,"message":"validation errors", "errors":serialiser.errors}, status=status.HTTP_400_BAD_REQUEST)


class Get_myCard_info(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        card_info, create = BankCardinfo.objects.get_or_create(card_holder_info = request.user)
        serialiser = GetMy_card_info(card_info)

        return Response({"success":True, "message":"data fatched!", "card_details":serialiser.data}, status=status.HTTP_200_OK)

    def put(self, request):
        card_info, create = BankCardinfo.objects.get_or_create(card_holder_info = request.user)
        serialiser = GetMy_card_info(instance=card_info, data = request.data, partial=True)
        if serialiser.is_valid():
            serialiser.save()
            return Response({"success":True, "message":"card update successfull!", "card_details":serialiser.data}, status=status.HTTP_200_OK)
        else:
            return Response({"success":False, "message":"invalid data!", "errors":serialiser.errors}, status=status.HTTP_400_BAD_REQUEST)



class Get_My_Invoices(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        invoices = Invoices.objects.filter(user=  request.user).order_by('-id')
        serialiser = InvoicesSerializers(invoices, many=True)

        return Response({"success":True, "message":"data fatched!", "data":serialiser.data}, status=status.HTTP_200_OK)

     

from api.serializers import LicenceSerializerView

class UserLicenceCreateView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        licences = user.licences.all()
        serializer = LicenceSerializerView(licences, many=True)
        return Response({"success":True,"message":"data fatched!", "data":serializer.data})
    
    def post(self, request):
        serializer = LicencesCreateUpdateSerializers(data = request.data)
        if serializer.is_valid():
            license = serializer.save()
            user = request.user
            user.licences.add(license)
            user.save()

            # Notify user about license addition
            sent_note_to_user.delay(user_id=request.user.id, title=f"License Added", content=f"Your license has been added successfully", note_type='success')
            return Response({"success":True,"message":"licence created success!", "data":serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"success":False,"message":"validation errors!", "errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        try:
            ln = LicencesModel.objects.get(id = pk)
            user = request.user            
            if ln in user.licences.all():
                serializer = LicencesCreateUpdateSerializers(instance =ln,  data = request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    # Notify user about license update
                    sent_note_to_user.delay(user_id=request.user.id, title=f"License Updated", content=f"Your license has been updated successfully", note_type='success')
                    return Response ({"success":True,"message":"update successfull !"}, status=status.HTTP_200_OK)
                else:
                    return Response ({"success":False,"message":"validation errors", "errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response ({"success":False,"message":"this is not your Licence"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response ({"success":False,"message":"Licence Not found"}, status=status.HTTP_404_NOT_FOUND)



from api.serializers import AccreditationsSerializer, AccreditationsSerializerView


class UsersCertificatesCreateUpdateView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user= request.user
        certificets = user.accreditations.all()
        serializer = AccreditationsSerializerView(certificets, many=True)
        return Response({"success":True,"message":"data fatched!", 'data':serializer.data}, status=status.HTTP_200_OK)
    def post(self, request):
        serializer = AccreditationsSerializer(data=request.data)
        if serializer.is_valid():
            ln = serializer.save()
            # Notify user about certificate addition
            sent_note_to_user.delay(user_id=request.user.id, title=f"Certificate Added", content=f"Your certificate has been added successfully", note_type='success')
            user= request.user
            user.accreditations.add(ln)
            return Response({"success":True,"message":"licence created success fully!", 'data':serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"success":False,"message":"validation errors!", 'errors':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        try:
            user = request.user
            certificate = CertificateModel.objects.get(id=pk)
            if certificate in  user.accreditations.all():
                serializer = AccreditationsSerializer(instance =certificate, data=request.data, partial=True)
                if serializer.is_valid():
                    ln = serializer.save()
                    user= request.user
                    user.accreditations.add(ln)
                    # Notify user about certificate update
                    sent_note_to_user.delay(user_id=request.user.id, title=f"Certificate Updated", content=f"Your certificate has been updated successfully", note_type='success')
                    return Response({"success":True,"message":"licence created success fully!", 'data':serializer.data}, status=status.HTTP_201_CREATED)
                else:
                    return Response({"success":False,"message":"validation errors!", 'errors':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"success":False,"message":"it is not your certificate!"}, status=status.HTTP_404_NOT_FOUND)
        except:
            return Response({"success":False,"message":"Certificate not found!"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            user = request.user
            certificate = CertificateModel.objects.get(id=pk)
            if certificate in  user.accreditations.all():
                certificate.accreditation.delete(save=False)
                # Notify user about certificate deletion
                sent_note_to_user.delay(user_id=request.user.id, title=f"Certificate Deleted", content=f"Your certificate has been deleted", note_type='normal')
                certificate.delete()
                return Response({"success":True,"message":"Delete successfull!"}, status=status.HTTP_200_OK)
            else:
                return Response({"success":False,"message":"it is not your certificate!"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:

            return Response({"success":False,"message":"Certificate not found!","errors":e}, status=status.HTTP_404_NOT_FOUND)

