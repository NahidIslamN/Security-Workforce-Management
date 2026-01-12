
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from SecurityGuard.custom_permissions import IsCompany, IsSubscribe, IsEmailVerified, IsGuard
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .serializers import *
from api.models import *
from managements.serializers import EngagementModelSerializersViews

## write your view here






from rest_framework.pagination import PageNumberPagination

class Recent_User(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        users = CustomUser.objects.filter(is_deleted=False).order_by('-create_at')

        serializer = UserDetailsSerializerVC(users, many=True)

        
        return Response(
            {
                "success":True,
                "message":"data fatched!",
                "results" : serializer.data
            }
        )
    
    def put(self, request, pk):
        try:
            users = CustomUser.objects.get(id=pk)
            users.is_admin_aproved = True
            users.save()
            return Response({"success":True,"message":"aproved by admin!"}, status= status.HTTP_200_OK)
        except Exception as e:       
            return Response({"success":False,"message":"user not found!", "errors":f"{e}"}, status= status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            users = CustomUser.objects.get(id=pk)
            users.is_deleted = True
            users.save()
            return Response({"success":True,"message":"delete successfull!"}, status= status.HTTP_200_OK)
        except Exception as e:       
            return Response({"success":False,"message":"user not found!", "errors":f"{e}"}, status= status.HTTP_404_NOT_FOUND)
    
    



class Subscribtions(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        invoices = Invoices.objects.filter(is_deleted=False).order_by('-created_at')

        paginator = PageNumberPagination()
        paginator.page_size = 100

        result_page = paginator.paginate_queryset(invoices, request)

        serializer = InvoicesSerializers(result_page, many=True)

        return paginator.get_paginated_response(serializer.data)
    
    def delete(self, request, pk):
        try:
            invoice = Invoices.objects.get(id=pk)
            invoice.is_deleted=True
            invoice.save()
            return Response({"success":True,"message":"delete successfull!"}, status= status.HTTP_200_OK)
        except Exception as e:       
            return Response({"success":False,"message":"user not found!", "errors":f"{e}"}, status= status.HTTP_404_NOT_FOUND)





class UserDetails(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request, pk):
        try:
            user = CustomUser.objects.get(id = pk)
            serilizer = UserDetailsSerializer(user)
            return Response({"success":True,"message":"data fatched!", "data":serilizer.data}, status= status.HTTP_200_OK)
        except:
            return Response({"success":False,"message":"user not found!"}, status= status.HTTP_400_BAD_REQUEST)
    
    def put(self, request, pk):
        try:
            user = CustomUser.objects.get(id = pk)
            user.is_admin_aproved = True
            user.is_admin_rejected = False
            user.save()
            return Response({"success":True,"message":"aproved by admin!"}, status= status.HTTP_200_OK)
        except:
            return Response({"success":False,"message":"user not found!"}, status= status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request, pk):
        try:
            user = CustomUser.objects.get(id = pk)
            user.is_admin_rejected = True
            user.is_admin_aproved = False
            user.save()
            return Response({"success":True,"message":"rejected by admin!"}, status= status.HTTP_200_OK)
        except:
            return Response({"success":False,"message":"user not found!"}, status= status.HTTP_400_BAD_REQUEST)
       




class Operative_Management(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        operatives = JobApplications.objects.filter(candidate__is_deleted=False).order_by('-id')

  

        serializer = GuardSerializer(operatives, many=True)

       
        return Response(
            {
                "success":True,
                "message":"data fatched!",
                "data":serializer.data
            }
        )
    


class Company_Management(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        companies = CompanyModel.objects.filter(company__is_deleted=False).order_by('-id')

     

        serializer = CompanySerializer(companies, many=True)

        # DRF pagination auto structure response তৈরি করে
        return Response(
            {
                "success":True,
                "message":"data fatched!",
                "companies":serializer.data
            }
        )



class JobManagement(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):

       

        jobs = JobModel.objects.filter(is_deleted = False).order_by('created_at')

        
        serializer = JobSerializers(jobs, many=True)

        return Response({"success":True,"message":"data fatched !", "data":serializer.data}, status= status.HTTP_200_OK)
    
    
    def delete(self, request, pk):
        try:
            jobs = JobModel.objects.get(id = pk)
            jobs.is_deleted = True
            jobs.save()

            return Response({"success":True,"message":"delte successfull!"}, status= status.HTTP_200_OK)
        except:
            return Response({"success":False,"message":"data not found!"}, status= status.HTTP_400_BAD_REQUEST)



class ContactManagementAdmin(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):

        engagements = EngagementModel.objects.filter(is_deleted = False).order_by('-id')
        
        serializer = EngagementModelSerializersViews(engagements, many=True)

        return Response({"success":True,"message":"data fatched !", "data":serializer.data}, status= status.HTTP_200_OK)
    
    def delete(self, request, pk):
        try:
            jobs = EngagementModel.objects.get(id = pk)
            jobs.is_deleted = True
            jobs.save()

            return Response({"success":True,"message":"delte successfull!"}, status= status.HTTP_200_OK)
        except:
            return Response({"success":False,"message":"data not found!"}, status= status.HTTP_400_BAD_REQUEST)









from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Sum, F
from api.models import EngagementModel, CompanyModel
from .serializers import CompanyReportSerializer


class PayrollReportAPIView(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        companies = CompanyModel.objects.all()
        report_data = []

        for company in companies:
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')


            filters = {"is_deleted": False, "job_details__job_provider":company}
            if start_date and end_date:
                filters["job_details__job_date__range"] = [start_date, end_date]
            elif start_date:
                filters["job_details__job_date__gte"] = start_date
            elif end_date:
                filters["job_details__job_date__lte"] = end_date
            engagements = EngagementModel.objects.filter(**filters).order_by('-created_at')


            filterss = {"is_deleted": False,"job_provider":company}
            if start_date and end_date:
                filterss["job_date__range"] = [start_date, end_date]
            elif start_date:
                filterss["job_date__gte"] = start_date
            elif end_date:
                filterss["job_date__lte"] = end_date


   

            total_jobs = JobModel.objects.filter(**filterss).count()

           

            total_operatives = engagements.values(
                'application__candidate'
            ).distinct().count()

            # Total Hours = old_duration + new_duration
            total_hours = engagements.aggregate(
                hours=Sum(F('job_details__job_duration') + F('new_job_duration'))
            )['hours'] or 0

            # Total Pay = Sum total_amount
            total_pay = engagements.aggregate(
                pay=Sum('total_amount')
            )['pay'] or 0

            # Pick one status (customize based on your need)
            engagement = engagements.first()
            status = engagement.contacts_trackers if engagement else "N/A"

            report_data.append({
                "company_name": company.company_name,
                "total_jobs": total_jobs,
                "total_operatives": total_operatives,
                "total_hours": float(total_hours),
                "total_pay": float(total_pay),
                "status": status,
            })

        serializer = CompanyReportSerializer(report_data, many=True)
        return Response({'success':True, 'message':"data fatched", "data":serializer.data})






class Refarral_Reprt(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):
        report_data = []

        # Process Guards
        guards = JobApplications.objects.select_related('candidate').prefetch_related('refaral_users')
        for guard_app in guards:
            referral_users = guard_app.refaral_users.all()
            report_data.append({
                "name": guard_app.candidate.first_name,
                "email_address": guard_app.candidate.email,
                "total_raffaral": referral_users.count(),
                "total_subscribtion": Invoices.objects.filter(user__in=referral_users).count(),
            })

        # Process Companies
        companies = CompanyModel.objects.select_related('company').prefetch_related('refaral_users')
        for company_model in companies:
            referral_users = company_model.refaral_users.all()
            report_data.append({
                "name": company_model.company.first_name,
                "email_address": company_model.company.email,
                "total_raffaral": referral_users.count(),
                "total_subscribtion": Invoices.objects.filter(user__in=referral_users).count(),
            })

        serializer = UserRefarralReportSerializer(report_data, many=True)
        return Response({'success': True, 'message': "data fatched", "data": serializer.data})






class Verification_center(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):

        return Response({"success":True,"message":"data fatched !", "data":{}}, status= status.HTTP_200_OK)


class AdminDashboardAnalytics(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        total_earnings = Invoices.objects.filter(is_deleted=False).aggregate(total=Sum('price'))['total'] or 0
        total_companies = CustomUser.objects.filter(user_type='company', is_deleted=False).count()
        total_guards = CustomUser.objects.filter(user_type='guard', is_deleted=False).count()

        recent_users = CustomUser.objects.filter(is_deleted=False).order_by('-create_at')[:10]
        recent_users_serializer = UserDetailsSerializerVC(recent_users, many=True)

        return Response({
            "success": True,
            "message": "Dashboard analytics fetched successfully",
            "data": {
                "total_earnings": float(total_earnings),
                "total_companies": total_companies,
                "total_guards": total_guards,
                "recent_users": recent_users_serializer.data
            }
        }, status=status.HTTP_200_OK)
    
from managements.models import PaymentController

class Payment_Crontrollers(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        pay_controller = PaymentController.objects.filter().order_by("-id").first()
        serializer = PaymentControllerSerializer(pay_controller)
        return Response({
            "success": True,
            "message": "Dashboard analytics fetched successfully",
            "data": serializer.data
        }, status=status.HTTP_200_OK)


    def put(self, request):
        pay_controller = PaymentController.objects.filter().order_by("-id").first()
        serializer = PaymentControllerSerializer(instance=pay_controller, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "success": True,
                "message": "Dashboard analytics fetched successfully",
                "data": serializer.data,
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "success": True,
                "message": "Dashboard analytics fetched successfully",
                "data": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)





class SubscribtionPlans(APIView):
    permission_classes = [IsAdminUser]
    def get(self, request):

        palns = SubscribtionPlan.objects.all()

        serializer = SubPlanSerializer(palns, many=True)


        return Response(
            {
                "success":True,
                "message":"data fatched!",
                "data":serializer.data
            }
        )

    def put(self, request, pk):

        try:
            plan = SubscribtionPlan.objects.get(id=pk)
        except:
            return Response(
                {
                    "success":False,
                    "message":"plan not found"
                },
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = SubPlanSerializer(instance = plan, data = request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            return Response(
                {
                    "success":True,
                    "message":"Update plan successfull!",
                    "data":serializer.data
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {
                    "success":False,
                    "message":"validation erros"
                },
                status=status.HTTP_400_BAD_REQUEST
            )


