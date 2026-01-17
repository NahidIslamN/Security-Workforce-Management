
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from SecurityGuard.custom_permissions import IsCompany, IsSubscribe, IsEmailVerified, IsGuard, Is_Admin_Verified
from rest_framework.permissions import IsAuthenticated
from .serializers import *
from api.models import CompanyModel, JobModel, JobApplications, EngagementModel, OperativeNote, SupportMessage
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from math import cos, radians
from datetime import datetime, date
from decimal import Decimal
from managements.models import *
from chat_app.tasks import sent_note_to_user
from django.db.models import Sum, Avg
from django.utils import timezone
from datetime import timedelta




# write your views here
class Guard_Dashboard(APIView):
    permission_classes = [IsGuard]

    def get(self, request):
        user = request.user

        # Get application for this user
        application, create = JobApplications.objects.get_or_create(candidate=user)

        # Actual rating value (NOT the field)
        avg_rating = application.avg_rating_main  # fixed

        # Imports
        from django.db.models import Sum
        from django.utils import timezone
        from datetime import timedelta

        today = timezone.now().date()
        start_of_week = today - timedelta(days=today.weekday())

        # Weekly completed engagements count
        total_earnings_this_week = EngagementModel.objects.filter(
            application=application,
            contacts_trackers='completed',
            is_deleted=False,
            created_at__date__gte=start_of_week,
            created_at__date__lte=today,
        ).aggregate(total=Sum('total_amount')).get('total') or 0.00

        # Applied jobs
        total_applied_jobs = JobModel.objects.filter(
            applications=application,
            is_deleted=False
        ).count()

        # Selected jobs (upcoming)
        total_selected_jobs = JobModel.objects.filter(
            selected_list=application,
            is_deleted=False
        ).count()

        # Completed jobs
        total_completed_jobs = EngagementModel.objects.filter(
            application=application,
            contacts_trackers='completed',
            is_deleted=False
        ).count()
        try:

            return Response(
                {
                    "success": True,
                    "message": "data fetched!",

                    "dashboard_data": {
                        "total_earnings_this_week": total_earnings_this_week,
                        "total_applied_jobs": total_applied_jobs,
                        "total_completed_jobs": total_completed_jobs,
                        "total_upcoming_jobs": total_selected_jobs,
                        "past_jobs": total_completed_jobs,
                        "avg_rating": avg_rating
                    },
                },
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {
                    "success": False,
                    "message": "error occurred!",
                    "errors": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )









class PostJobs(APIView):
    permission_classes = [IsCompany, IsSubscribe]
    def get_permissions(self):
        # Enforce admin verification only for POST requests
        if self.request.method == "POST":
            return [IsCompany(), IsSubscribe(), Is_Admin_Verified()]
        # For other methods, keep existing company+subscribe checks
        return [IsCompany(), IsSubscribe()]


    def get(self, request):
        user = request.user
        company, create = CompanyModel.objects.get_or_create(company = user)
        jobs = JobModel.objects.filter(job_provider=company, is_deleted = False).order_by("-id")

        serializer = JobModelDetailsCompanyPointSerializer(jobs, many=True)

        return Response({
            "success": True,
            "message": "data fetched!",
            "jobs_posts": serializer.data
        }
        )

    
    def post(self, request):
        user = request.user
        company, create = CompanyModel.objects.get_or_create(company = user)
        data = request.data.copy()
        data['job_provider'] = company.id
        serializer = JobModelSerializer(data = data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success":True,"message":"Job posted!", 'data':serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({'success':False,"message":"validation errors!", 'errors':serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

    def put(self, request, pk):
        try:
            user = request.user
            company, create = CompanyModel.objects.get_or_create(company = user)
            job = JobModel.objects.get(id=pk)
            if job.job_provider == company and job.is_deleted == False:           
                serializer = JobModelSerializer(instance=job, data = request.data, partial=True)      
                if serializer.is_valid():
                    serializer.save()          
                    return Response({"success":True,"message":"update successfull!", 'data':serializer.data}, status=status.HTTP_200_OK) 
                else:
                    return Response({'success':False,"message":"validation errors!", "errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)        
            else:
                return Response({'success':False,"message":"you are not the creator of the post!"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'success':False,"message":"job not found!"}, status=status.HTTP_404_NOT_FOUND)


    def delete(self, request, pk):
        try:
            user = request.user
            company, create = CompanyModel.objects.get_or_create(company = user)
            job = JobModel.objects.get(id=pk)
            if job.job_provider == company and job.is_deleted == False:
                job.is_deleted = True
                job.save()
                return Response({"success":True, 'message':"delete successful!"}, status=status.HTTP_200_OK)
            else:
                return Response({'success':False,"message":"you are not the creator of the post!"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({'success':False,"message":"job not found!"}, status=status.HTTP_404_NOT_FOUND)




class JobDetailsCompanyPoint(APIView):
    permission_classes = [IsCompany, IsSubscribe]
    def get(self, request, pk):

        try:
            user = request.user
            company, create = CompanyModel.objects.get_or_create(company = user)
            job = JobModel.objects.get(id=pk)
           
            if job.job_provider == company and job.is_deleted == False:  
                          
                serializer = JobModelDetailsCompanyPointSerializer(job)


                return Response({"success":True,"message":"data fatched!", 'data':serializer.data}, status=status.HTTP_200_OK)            
            else:
                return Response({'success':False,"message":"you are not the creator of the post!"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
           
            return Response({'success':False,"message":"job not found!","errors":e}, status=status.HTTP_404_NOT_FOUND)


    def put(self, request, pk, apk):
        try:
            user = request.user
            company, create = CompanyModel.objects.get_or_create(company = user)
            job = JobModel.objects.get(id=pk)
            application = JobApplications.objects.get(id=apk)
    
            if job.job_provider == company and job.is_deleted == False and job.is_application_complete == False and (application in job.applications.all()): 
                job.selected_list.add(application)
                job.applications.remove(application)
                if EngagementModel.objects.filter(job_details = job, application = application).exists():
                    eng = EngagementModel.objects.filter(job_details = job, application = application).first()

                    eng.application.status = 'selected'
                    eng.application.save()
                    
                    eng.is_deleted = False
                    eng.save()
                    serializer = EngagementModelSerializersViews(eng)  
                    sent_note_to_user.delay(user_id=application.candidate.id, title=f"Job Assigned by {company.company_name}!", content = f"You’ve been selected for a new job,Please review and sign the contract.", note_type='success')     
                     
                    return Response({"success":True,"message":"data fatched!", 'engagements':serializer.data}, status=status.HTTP_200_OK)
                
                else:
                    eng = EngagementModel.objects.create(
                        job_details = job,
                        application = application
                    ) 
                    eng.application.status = 'selected'
                    eng.application.save()
                    eng.save()
                    job.save()
                    sent_note_to_user.delay(user_id=application.candidate.id, title=f"Job Assigned by {company.company_name}!", content = f"You’ve been selected for a new job,Please review and sign the contract.", note_type='success')

                    serializer = EngagementModelSerializersViews(eng)                
                    return Response({"success":True,"message":"data fatched!", 'engagements':serializer.data}, status=status.HTTP_200_OK)            
            else:
                return Response({'success':False,"message":"you are not the creator of the post!/ already selected!"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
         
            return Response({'success':False,"message":"job not found!","errors":f"{e}"}, status=status.HTTP_404_NOT_FOUND)


    def patch(self, request, pk, apk):
        try:
            user = request.user
            company, create = CompanyModel.objects.get_or_create(company = user)
            job = JobModel.objects.get(id=pk)
            application = JobApplications.objects.get(id=apk)
    
            if job.job_provider == company and job.is_deleted == False and job.is_application_complete == False and (application in job.selected_list.all()): 
                job.selected_list.remove(application)
                job.applications.add(application)
                eng = EngagementModel.objects.filter(job_details = job, application = application).first()
                eng.is_deleted = True
                eng.save()                
                # Notify guard about removal from selected list
                sent_note_to_user.delay(user_id=application.candidate.id, title=f"Job Selection Cancelled", content=f"You've been removed from the selected list for job '{job.job_title}'", note_type='warning')
              
                return Response({"success":True,"message":"user removed form selected list!"}, status=status.HTTP_200_OK)            
            else:
                return Response({'success':False,"message":"you are not the creator of the post!"}, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
         
            return Response({'success':False,"message":"job not found!","errors":f"{e}"}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk):
        user = request.user
        company, create = CompanyModel.objects.get_or_create(company = user)
        job = JobModel.objects.get(id=pk)

        if job.job_provider == company and  job.status == 'published':
            job.is_application_complete = True
            job.status = "untasked"
            job.save()
            return Response({"success":True,"message":"this application will not appere to the user",}, status= status.HTTP_200_OK)
        else:
            return Response({"success":False,"message":"you are not the creator of the job/ already marked!"}, status=status.HTTP_400_BAD_REQUEST)
            




class EngagementsViews(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        if user.user_type == "company":
            company, create = CompanyModel.objects.get_or_create(company = user)
            eng = EngagementModel.objects.filter(
                job_details__job_provider = company,
                is_deleted = False,
            ).order_by('-id')


            serializer = EngagementModelSerializersViews(eng, many=True)

            return Response({
                "success": True,
                "message": "data fetched!",
                "engagements": serializer.data
            })
        elif user.user_type == "guard":
            application, create = JobApplications.objects.get_or_create(candidate = user)
           
            eng = EngagementModel.objects.filter(
                application = application,
                is_deleted = False,
            ).order_by('-id')

            serializer = EngagementModelSerializersViewsGurd(eng, many=True)

            return Response({
                "success": True,
                "message": "data fetched!",
                "engagements": serializer.data
            })



class EngagementsViewsAmmend(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        
        application, create = JobApplications.objects.get_or_create(candidate = user)
        
        eng = EngagementModel.objects.filter(
            application = application,
            amend_trackers="pending",
            
            is_deleted = False,
        ).order_by('-id')

        serializer = EngagementModelSerializersViewsGurd(eng, many=True)

        return Response({
            "success": True,
            "message": "data fetched!",
            "engagements": serializer.data
        })



class OperativeViews(APIView):
    permission_classes = [IsCompany]
    def get(self, request):
        user = request.user
        company, create = CompanyModel.objects.get_or_create(company = user)
        eng = EngagementModel.objects.filter(
            Q(job_details__job_provider=company, is_deleted=False)
            &
            (
                Q(contacts_trackers='is_signed')|
                Q(contacts_trackers='not_pay')  
            )
            &
            (
                Q(is_shift_end=False)|
                Q(is_company_reted=False)  
            )

        )

        paginator = PageNumberPagination()
        paginator.page_size = int(request.GET.get("page_size", 100))  # dynamic page size optional
        result_page = paginator.paginate_queryset(eng, request)
        serializer = OperativeTrackersSerializersViews(result_page, many=True)
        return paginator.get_paginated_response({
            "success": True,
            "message": "data fetched!",
            "operatives": serializer.data
        })
       
    





class PayRollManagementViews(APIView):
    permission_classes = [IsCompany]
    def get(self, request):
        user = request.user
        company, create = CompanyModel.objects.get_or_create(company = user)
        eng = EngagementModel.objects.filter(
            job_details__job_provider=company, is_shift_end=True, is_deleted=False
            
        )
        paginator = PageNumberPagination()
        paginator.page_size = int(request.GET.get("page_size", 20000000000000000))  # dynamic page size optional
        result_page = paginator.paginate_queryset(eng, request)

        serializer = Payroll_Management_SerializersViews(eng, many=True)

        return paginator.get_paginated_response({
            "success": True,
            "message": "data fetched!",
            "pay_roles": serializer.data
        }
        )
       
        
      

class PerferetOperativeViews(APIView):
    permission_classes = [IsCompany]
    def get(self, request):
        user = request.user
        company, create = CompanyModel.objects.get_or_create(company = user)
        eng = EngagementModel.objects.filter(
            job_details__job_provider = company,
            is_deleted = False,
            is_shift_end = True,
            is_deleted_perfomed_operatives = False           
        )

        paginator = PageNumberPagination()
        paginator.page_size = int(request.GET.get("page_size", 100))  # dynamic page size optional
        result_page = paginator.paginate_queryset(eng, request)

        serializer = PerpormedOperativesSerializersViews(result_page, many=True)

        return paginator.get_paginated_response({
            "success": True,
            "message": "data fetched!",
            "operatives": serializer.data
        }
    )
     

    def put(self, request, pk=None):
        try:
            user = request.user
            if pk is None:
                 return Response({"success":False,"message":"Engagement ID (pk) is required"}, status=status.HTTP_400_BAD_REQUEST)

            eng = EngagementModel.objects.get(id=pk)
            
            if eng.job_details.job_provider.company != user:
                return Response({"success":False,"message":"You are not authorized to add notes for this operative"}, status=status.HTTP_403_FORBIDDEN)
            
            company = eng.job_details.job_provider
            operative = eng.application.candidate
            note_content = request.data.get('note')
            
            if note_content is None:
                 return Response({"success":False,"message":"'note' field is required"}, status=status.HTTP_400_BAD_REQUEST)

            OperativeNote.objects.update_or_create(
                company=company,
                operative=operative,
                defaults={'note': note_content}
            )
            
            return Response({"success":True,"message":"Note updated successfully"}, status=status.HTTP_200_OK)

        except EngagementModel.DoesNotExist:
            return Response({"success":False,"message":"Engagement not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"success":False,"message":str(e)}, status=status.HTTP_400_BAD_REQUEST)
   
    def delete(self, request, pk):
        try:
            user = request.user 
            eng = EngagementModel.objects.get(id=pk)
            if eng.job_details.job_provider.company == user:
                application = eng.application
                
                engs = EngagementModel.objects.filter(
                    job_details__job_provider__company = user,
                    application = application,
                    is_deleted_perfomed_operatives = False  
                )
                if engs.exists():
                    for eng in engs:
                        eng.is_deleted_perfomed_operatives = True
                        eng.save()
                    return Response({"success":True,"message":"delete successfull!"}, status=status.HTTP_200_OK)   
                else:
                    return Response({"success":False,"message":"already deleted!"}, status=status.HTTP_400_BAD_REQUEST)
                                             
            else:
                return Response({"success":False,"message":"you are not a member or this chat!",}, status=status.HTTP_400_BAD_REQUEST)

        except:
            return Response({"success":False,"message":"not found!",}, status=status.HTTP_404_NOT_FOUND)

    

class EngagementsDetailsViews(APIView):
    permission_classes = [IsAuthenticated, IsSubscribe]
    def get(self, request, pk):
        user = request.user
        try:
            eng = EngagementModel.objects.get(id=pk)                
            if request.user.user_type == "company":          
                company, create = CompanyModel.objects.get_or_create(company = user)
                
                if eng.job_details.job_provider == company and eng.is_deleted == False:
                    serializer = EngagementModelSerializersViews(eng)                
                    return Response({"success":True,"message":"data fatched!", 'engagements':serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"success":False,"message":"your are not a member of eng"}, status=status.HTTP_400_BAD_REQUEST)
                
            elif request.user.user_type == "guard":
                if eng.application.candidate == user and eng.is_deleted == False:
                    serializer = EngagementModelSerializersViews(eng)                
                    return Response({"success":True,"message":"data fatched!", 'engagements':serializer.data}, status=status.HTTP_200_OK)
                else:
                    return Response({"success":False,"message":"your are not a member of eng"}, status=status.HTTP_400_BAD_REQUEST)
                
            elif request.user.user_type == "admin":
                serializer = EngagementModelSerializersViews(eng)                
                return Response({"success":True,"message":"data fatched!", 'engagements':serializer.data}, status=status.HTTP_200_OK)
            else:
                return Response({"success":False,"message":"your are not a user"}, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({"success":False,"message":"data fatched!", 'errors':f"{e}"}, status=status.HTTP_400_BAD_REQUEST)



    def put(self, request, pk):
        user = request.user
        try:
            eng = EngagementModel.objects.get(id=pk)
            
            if request.user.user_type == "company":  
        
                company, create = CompanyModel.objects.get_or_create(company = user)
                if eng.job_details.job_provider == company and eng.is_deleted == False:
                    data = request.data
                    serializer = CompanyEngUpdateSerializer(data=request.data)
                    
                    if serializer.is_valid():

                        paid_a_gaurd = serializer.validated_data.get('paid_a_gaurd', None)
                        if paid_a_gaurd:
                            eng.contacts_trackers = 'completed'
                            eng.save()
                            # Notify guard about payment
                            sent_note_to_user.delay(user_id=eng.application.candidate.id, title=f"Payment Received", content=f"Payment for job '{eng.job_details.job_title}' has been processed", note_type='success')
                            srl = EngagementModelSerializersViews(eng)
                            return Response({"success":True,"message":"aproved successfull!", 'engagements':srl.data}, status=status.HTTP_200_OK)


                        is_shift_end = serializer.validated_data.get('is_shift_end', None)
                        if is_shift_end :
                            eng.is_shift_end = True
                            eng.save()
                            # Notify guard about shift end
                            sent_note_to_user.delay(user_id=eng.application.candidate.id, title=f"Shift Ended", content=f"Your shift for job '{eng.job_details.job_title}' has been marked as ended", note_type='normal')
                            srl = EngagementModelSerializersViews(eng)
                            return Response({"success":True,"message":"aproved successfull!", 'engagements':srl.data}, status=status.HTTP_200_OK)
                      
                        new_end_time = serializer.validated_data.get('new_end_time', None)
                        detail_amendment = serializer.validated_data.get('detail_amendment', None)

                        if (new_end_time is not None) and (detail_amendment is not None):
                            db_end_time = eng.job_details.end_time
                            db_dt = datetime.combine(date.today(), db_end_time)
                            new_dt = datetime.combine(date.today(), new_end_time)
                            duration = new_dt - db_dt
                            hours_decimal = Decimal(round(duration.total_seconds() / 3600))
                            eng.new_job_duration = hours_decimal
                            eng.new_end_time = new_end_time
                            eng.amend_details = detail_amendment
                            eng.amend_trackers = "pending"
                            eng.save() 
                            # Notify guard about amendment request
                            sent_note_to_user.delay(user_id=eng.application.candidate.id, title=f"Contract Amendment Request", content=f"The company has requested a contract amendment. Please review.", note_type='warning')
                            srl = EngagementModelSerializersViews(eng)
                            return Response({"success":True,"message":"amed request sent. wati for approval!", 'engagements':srl.data}, status=status.HTTP_200_OK)

                        signature_party_a = request.FILES.get("signature_party_a", None)
                        if signature_party_a is not None:
                            if eng.contacts_trackers == "is_signed":
                                return Response({"success":False,"message":"you can't update your sign now!", "errors":"already signed!"}, status=status.HTTP_400_BAD_REQUEST) 
                            else:
                                # Notify guard about company signature
                                sent_note_to_user.delay(user_id=eng.application.candidate.id, title=f"Contract Signed", content=f"The company has signed the contract. Please review and sign.", note_type='normal')
                                eng.signature_party_a = signature_party_a
                                eng.save()
                                if eng.signature_party_a and eng.signature_party_b:
                                    eng.contacts_trackers = "is_signed"
                                    eng.save()
                                srl = EngagementModelSerializersViews(eng)
                                return Response({"success":True,"message":"upload image successfull!", 'engagements':srl.data}, status=status.HTTP_200_OK)
     
                        else:
                            pass


                        pay_rate = serializer.data.get('pay_rate', None)
                        # print(type(pay_rate))
                        if pay_rate is not None:
                            if eng.contacts_trackers == "is_signed":
                                return Response({"success":False,"message":"Engagement signed", "errors":"never try change eng after signed"}, status=status.HTTP_400_BAD_REQUEST)
                            else:
                                eng.job_details.pay_rate =  Decimal(round(pay_rate,2))
                                eng.job_details.save()
                                eng.save()

                                srl = EngagementModelSerializersViews(eng)
                                return Response({"success":True,"message":"Update pay-rate success full!", 'engagements':srl.data}, status=status.HTTP_200_OK)


                             
                        return Response({"success":False,"message":"please give a valid data!", 'errors':"pleace give a valid data"}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        return Response({"success":False,"message":"vaidation errors", "errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

                else:
                    return Response({"success":False,"message":"your are not a member of eng"}, status=status.HTTP_400_BAD_REQUEST)


            elif request.user.user_type == "guard":
                serializer = GaurdEngUpdateSerializer(data = request.data)

                if serializer.is_valid():

                    if eng.application.candidate == user and eng.is_deleted == False and eng.contacts_trackers == "is_signed":

                        start_shift = serializer.validated_data.get('start_shift', None)
                        if start_shift is not None and eng.operative_trackers != 'seft_completed' :
                            eng.operative_trackers = "on_duty"
                            eng.application.status = "tasked"
                            eng.save()
                            # Notify company about shift start
                            sent_note_to_user.delay(user_id=eng.job_details.job_provider.company.id, title=f"Shift Started", content=f"{user.first_name} {user.last_name} has started their shift for job '{eng.job_details.job_title}'", note_type='normal')
                            return Response({"success":True,"message":"duty started !"}, status=status.HTTP_200_OK)
                        
                        end_shift = serializer.validated_data.get('end_shift', None)
                        if end_shift is not None:
                            eng.operative_trackers = "seft_completed"
                            eng.contacts_trackers = 'not_pay'
                            eng.save()
                            eng.application.status = "untasked"
                            # Notify company about shift completion
                            sent_note_to_user.delay(user_id=eng.job_details.job_provider.company.id, title=f"Shift Completed - Payment Pending", content=f"{user.first_name} {user.last_name} has completed their shift. Please process payment.", note_type='warning')
                            return Response({"success":True,"message":"shift completed !"}, status=status.HTTP_200_OK)
                        else:
                            return Response({"success":False,"message":"some thing want to be worng!", }, status=status.HTTP_400_BAD_REQUEST)


                    if eng.application.candidate == user and eng.is_deleted == False:
                        signature_party_b = request.FILES.get("signature_party_b", None)
                        if signature_party_b is not None:
                            # Notify company about guard signature
                            sent_note_to_user.delay(user_id=eng.job_details.job_provider.company.id, title=f"Contract Signed", content=f"{user.first_name} {user.last_name} has signed the contract for job '{eng.job_details.job_title}'", note_type='normal')
                            eng.signature_party_b = signature_party_b
                            eng.save()
                            if eng.signature_party_a and eng.signature_party_b:
                                eng.contacts_trackers = "is_signed"
                                eng.save()
                            return Response({"success":True,"message":"signature uploded !"}, status=status.HTTP_200_OK)
                    
                    else:
                        return Response({"success":False,"message":"can't get any request", }, status=status.HTTP_400_BAD_REQUEST)

                else:
                    return Response({"success":False,"message":"validation errrors", "errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

            else:
                return Response({"success":False,"message":"not a valid user", }, status= status.HTTP_400_BAD_REQUEST)    

        except Exception as e:
            return Response({"success":False,"message":"errors get!", 'errors':f"{e}"}, status=status.HTTP_400_BAD_REQUEST)
            



############################################# Guard views ###########################################


class GuardsJobPostSection(APIView):
    permission_classes = [IsAuthenticated, IsEmailVerified]
    def get_permissions(self):
        # Enforce admin verification only for POST requests
        if self.request.method == "POST":
            return [IsAuthenticated(), IsEmailVerified(), Is_Admin_Verified()]
        return [IsAuthenticated(), IsEmailVerified()]
    def get(self, request):
        try:
            query_per_redius = int(request.GET.get('redius', 10000))  
            user = request.user
            if not user.latitude or not user.longitude:
                return Response({"success":False,"message": "User location not set "}, status=status.HTTP_400_BAD_REQUEST)
            
            radius_km = user.user_redus
            if query_per_redius == 0:
                radius_km = user.user_redus
            else:
                radius_km = query_per_redius

            user_lat = user.latitude
            user_lon = user.longitude
            
            lat_diff = radius_km / 111
            lon_diff = radius_km / (111 * cos(radians(user_lat)))

            min_lat = user_lat - lat_diff
            max_lat = user_lat + lat_diff
            min_lon = user_lon - lon_diff
            max_lon = user_lon + lon_diff
            from django.utils import timezone
            today = timezone.now().date()
            jobs_qs = JobModel.objects.filter(
                latitude__gte=min_lat, latitude__lte=max_lat,
                longitude__gte=min_lon, longitude__lte=max_lon,
                is_application_complete = False
                 
            ).order_by('-created_at')
            
            #  job_date__gte=today,


            query_per_ln_type_id = int(request.GET.get('ln_type_id', 0))
            query_per_acc_type_id = int(request.GET.get('acc_type_id', 0))

            query_per_pay_rate_min = int(request.GET.get('pay_rate_min', 0))
            query_per_pay_rate_max = int(request.GET.get('pay_rate_max', 0))

            query_per_title = request.GET.get('title')
            
            # Apply OR filter if filters are provided
            filters = Q()


            if query_per_title:
                filters |= Q(job_title__icontains=query_per_title)


            
            if query_per_ln_type_id:
                filters |= Q(licence_type_requirements__id=query_per_ln_type_id)

            if query_per_acc_type_id:
                filters |= Q(accreditations_requirements__id=query_per_acc_type_id)

            if query_per_pay_rate_min and query_per_pay_rate_max:
                filters |= Q(pay_rate__gte=query_per_pay_rate_min, pay_rate__lte=query_per_pay_rate_max)

            jobs_qs = jobs_qs.filter(filters)
            
            
            serializer = JobModelDetailsSerializer(jobs_qs, many=True)

            return Response(
                {"success":True,"message":"data fatched!", "data":serializer.data}
            )
        except Exception as e:
            return Response({"success":False,"message": "data not fatched!","errors":e}, status=status.HTTP_400_BAD_REQUEST)
        
    
    def post(self, request, pk):
        try:
            user = request.user  
                   
            application, create = JobApplications.objects.get_or_create(candidate = user)           
            job_post = JobModel.objects.get(id=pk)            
            if (application in job_post.applications.all()) or (application in job_post.selected_list.all()):
                serialzer = JobModelDetailsSerializer(job_post)                
                return Response({"success":False, "message":'already applied!', "job_details":serialzer.data}, status=status.HTTP_400_BAD_REQUEST)

            serialzer = JobModelDetailsSerializer(job_post)
            job_post.applications.add(application)
            job_post.save()
            # Notify company about new job application
            sent_note_to_user.delay(user_id=job_post.job_provider.company.id, title=f"New Job Application", content=f"{user.first_name} {user.last_name} applied for job '{job_post.job_title}'", note_type='normal')

            return Response({"success":True, "message":'application successfull!', "job_details":serialzer.data}, status= status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"success":False, "message":'somthing want to worng !', 'message':f'{e}'}, status=status.HTTP_404_NOT_FOUND)
        




from rest_framework.pagination import PageNumberPagination



class Gard_Jobs_Section(APIView):
    permission_classes = [IsGuard]

    def get(self, request):
        user = request.user
        application, create = JobApplications.objects.get_or_create(candidate = user)
        is_amend = request.GET.get('is_amend', None)
        if is_amend is None:
            eng = EngagementModel.objects.filter(
                job_details__selected_list = application,
                job_details__is_application_complete = True,
                job_details__is_deleted = False  

            )
        else:
            eng = EngagementModel.objects.filter(
                job_details__selected_list = application,
                job_details__is_application_complete = True,
                job_details__is_deleted = False  
            )

            eng = eng.filter(
                Q(amend_trackers='pending') | Q(amend_trackers='rejected')
            )


        paginator = PageNumberPagination()
        paginator.page_size = int(request.GET.get("page_size", 10))  # dynamic page size optional
        result_page = paginator.paginate_queryset(eng, request)

        serializer = EngagementModelGuardSerializersViews(result_page, many=True)

        return paginator.get_paginated_response({
            "success": True,
            "message": "data fetched!",
            "my_jobs": serializer.data
        })

        
    def put(self, request, pk):
        user = request.user
        try:
            eng = EngagementModel.objects.get(id=pk)

            serializer = EmandSerialzers(data = request.data)
            if serializer.is_valid():
                if eng.application.candidate == user:
                    if eng.amend_trackers == "pending" or eng.amend_trackers == "rejected":

                        is_accept = serializer.validated_data.get('accept', None)
                        is_rejected = serializer.validated_data.get('rejected', None)

                        if is_accept==True:
                            eng.amend_trackers = 'accepted'
                            eng.save()
                            return Response({"success":True,"message":"Accepted ammend request successfull!"}, status=status.HTTP_200_OK)
                        
                        if is_rejected==True and not(eng.amend_trackers == 'accepted'):
                            eng.amend_trackers = 'rejected'
                            eng.save()
                            return Response({"success":True,"message":"rejected ammend request successfull!"}, status=status.HTTP_200_OK)

                        else:
                            return Response({"success":False,"message":"you can't reject amend!"}, status=status.HTTP_400_BAD_REQUEST)
                    
                    else:
                        return Response({"success":False,"message":"you can't perfrom action here!"}, status=status.HTTP_400_BAD_REQUEST)

                else:
                    return Response({"success":False,"message":"you are not a memeter of the contact!"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"success":False,"message":"validation errors!"}, status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"success":False,"message":"something want to worng!"}, status=status.HTTP_400_BAD_REQUEST)








class Gard_Jobs_History(APIView):
    permission_classes = [IsGuard]

    def get(self, request):
        user = request.user
        application, create = JobApplications.objects.get_or_create(candidate = user)
        is_amend = request.GET.get('is_amend', None)
        if is_amend is None:
            eng = EngagementModel.objects.filter(
                job_details__selected_list = application,
                job_details__is_application_complete = True,
                job_details__is_deleted = False ,
                is_shift_end = True

            )
        else:
            eng = EngagementModel.objects.filter(
                job_details__selected_list = application,
                job_details__is_application_complete = True,
                job_details__is_deleted = False ,
                is_shift_end = True
            )

            eng = eng.filter(
                Q(amend_trackers='pending') | Q(amend_trackers='rejected')
            )


        paginator = PageNumberPagination()
        paginator.page_size = int(request.GET.get("page_size", 10))  # dynamic page size optional
        result_page = paginator.paginate_queryset(eng, request)

        serializer = EngagementModelGuardSerializersViews(result_page, many=True)

        return paginator.get_paginated_response({
            "success": True,
            "message": "data fetched!",
            "my_jobs": serializer.data
        })











########################## Rate of a Engagement Guard & Company #####################


class Rate_On_Engagement(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        user = request.user
        try:
            eng= EngagementModel.objects.get(id=pk)

            if user.user_type == 'company':
                if eng.job_details.job_provider.company == user and eng.is_shift_end :
                    if  eng.is_company_reted:
                        return Response({"success":False,"message":"already rated!"}, status=status.HTTP_400_BAD_REQUEST)
                    else:
                        data = request.data
                        serializer = Guard_Rating_Serializers(data = data)
                        if serializer.is_valid():
                            rate = serializer.save()
                            rate.user = user
                            rate.save()
                            application = eng.application
                            application.rating.add(rate)
                            application.save()
                            eng.is_company_reted = True
                            eng.save()
                            # Notify guard about rating
                            try:
                                company_name = eng.job_details.job_provider.company_name
                                sent_note_to_user.delay(user_id=application.candidate.id, title=f'New Rating Received', content=f'You received a {rate.main_rating}-star rating from {company_name}', note_type='normal')
                            except Exception as e:
                                print(f'Error sending notification: {e}')
                            return Response({"success":True,"message":"rate given successfull!", "rate":f"{rate.main_rating}"}, status=status.HTTP_200_OK)
                        else:
                            return Response({'success':False, "message":"validation erros!", "errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
      
                else:
                    return Response({"success":False,"message":"you are not a member of the eng and shift not end yet"}, status=status.HTTP_400_BAD_REQUEST)
                

            elif user.user_type == 'guard':
                
                if eng.application.candidate == user:

                    if  eng.is_guard_reted:
                            # Notify company about rating

                        return Response({"success":False,"message":"already rated!"}, status=status.HTTP_400_BAD_REQUEST)
                    
                    else:
                        data = request.data
                        serializer = Company_Rating_Serializers(data = data)
                        if serializer.is_valid():
                            rate = serializer.save()
                            rate.user = user
                            rate.save()
                            job_company = eng.job_details.job_provider
                            job_company.rating.add(rate)
                            job_company.save()
                            eng.is_guard_reted = True
                            eng.save()
                            # Notify company about rating
                            sent_note_to_user.delay(user_id=job_company.company.id, title=f'New Rating Received', content=f'You received a {rate.main_rating}-star rating from {user.first_name} {user.last_name}', note_type='normal')
                            return Response({"success":True,"message":"rate given successfull!", "rate":f"{rate.main_rating}"}, status=status.HTTP_200_OK)
                        else:
                            return Response({'success':False, "message":"validation erros!", "errors":serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"success":False,"message":"you are not a member of the engagement!"}, status=status.HTTP_400_BAD_REQUEST)
                    
            else:
                return Response({"success":False,"message":"un authorize user!"}, status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            return Response({"success":False,"message":"something want to worng!", 'errors':f"{e}"}, status=status.HTTP_400_BAD_REQUEST)





#################################### subscribetions ############################

import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
from .models import PaymentController
from django.utils import timezone
from datetime import timedelta

class SubscribeNow(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request,plan_id):
        user = request.user
        PRODUCT_ID = "prod_TQZ4I5PRgaDbC8"
        try:
            subscribe_plan = SubscribtionPlan.objects.get(id=plan_id)
        except:
            return Response({"success":False,"message":"not found any plan"}, status=status.HTTP_400_BAD_REQUEST)
        
        is_reffaral_bounus = request.GET.get('ref_bonus', None)

        if is_reffaral_bounus is not None and is_reffaral_bounus == 'true':
            user_type = user.user_type
            controller = PaymentController.objects.filter().order_by('-id').first()
            if user_type == 'company' and subscribe_plan.plan_for =='company':
                company = CompanyModel.objects.get(company = user)
                total=company.refaral_users.filter(is_subscribe = True,  is_earned = False).count()
                if total >= controller.min_referral_user_of_company:
                    reward_type = controller.is_percentage_company
                    if reward_type:
                        price_usd = subscribe_plan.price 
                        discount_price = (price_usd * controller.percentage_company) / 100
                        final_price_usd = price_usd - discount_price
                        unit_amount = int(final_price_usd * 100)

                        price = stripe.Price.create(
                            unit_amount=unit_amount,   # price in cents
                            currency="usd",
                            product=PRODUCT_ID,        # existing product
                            # Do NOT include recurring => one-time payment
                        )
                        checkout_session = stripe.checkout.Session.create(
                            payment_method_types=["card"],
                            line_items=[{
                                "price": price.id,
                                "quantity": 1,
                            }],
                            mode="payment",  
                            success_url="https://5r6mdm6l-8001.inc1.devtunnels.ms/",
                            cancel_url="https://5r6mdm6l-8001.inc1.devtunnels.ms/",
                            client_reference_id=str(user.id),
                            metadata={  
                                "subscribe_plan_id": str(plan_id),
                                "is_reffaral":True,
                                'discount_price': str(discount_price),
                                
                            }
                            
                        )

                        return Response({
                            "success":True,
                            "payment_url":checkout_session.url,
                            
                        }, status=status.HTTP_200_OK)
                    else:
                        invoice = Invoices.objects.create(
                            user = user,
                            invoice_date = timezone.now().date(),
                            plan = subscribe_plan,
                            price = 0.00,
                            end_date = timezone.now().date() + timedelta(days=controller.total_free_days_company)                    
                        )
                        invoice.save()
                        gard_refaral_user = company.refaral_users.filter(is_subscribe = True,  is_earned = False)[0:controller.min_referral_user_of_company]
                        for users in gard_refaral_user:
                            users.is_earned = True
                            users.save()
                        
                        user.is_subscribe = True
                        user.save()
                        
                        return Response({"success":True, "message":"subscribe successfull!"}, status=status.HTTP_200_OK)
                else:
                    return Response({"success":False, "message":"target not fill up"}, status=status.HTTP_400_BAD_REQUEST)
                

            elif user_type == 'guard' and subscribe_plan.plan_for =='guard' :
                guard = JobApplications.objects.get(candidate = user)
                total=guard.refaral_users.filter(is_subscribe = True,  is_earned = False).count()
                if total>= controller.min_referral_user_of_guard:
                    reward_type = controller.is_percentage_guard
                    if reward_type:

                        price_usd = subscribe_plan.price 
                        discount_price = (price_usd * controller.percentage_guard) / 100
                        final_price_usd = price_usd - discount_price
                        unit_amount = int(final_price_usd * 100)

                        price = stripe.Price.create(
                            unit_amount=unit_amount,   # price in cents
                            currency="usd",
                            product=PRODUCT_ID,        # existing product
                            # Do NOT include recurring => one-time payment
                        )
                        checkout_session = stripe.checkout.Session.create(
                            payment_method_types=["card"],
                            line_items=[{
                                "price": price.id,
                                "quantity": 1,
                            }],
                            mode="payment",  
                            success_url="https://5r6mdm6l-8001.inc1.devtunnels.ms/",
                            cancel_url="https://5r6mdm6l-8001.inc1.devtunnels.ms/",
                            client_reference_id=str(user.id),
                            metadata={  
                                "subscribe_plan_id": str(plan_id),
                                "is_reffaral":True,
                                'discount_price': str(discount_price)
                            }
                            
                        )

                        return Response({
                            "success":True,
                            "payment_url":checkout_session.url,
                            
                        }, status=status.HTTP_200_OK)
                    

                    else:
                        invoice = Invoices.objects.create(
                            user = user,
                            invoice_date = timezone.now().date(),
                            plan = subscribe_plan,
                            price = 0.00,
                            end_date = timezone.now().date() + timedelta(days=controller.total_free_days_guard)                    
                        )
                        invoice.save()
                        gard_refaral_user = guard.refaral_users.filter(is_subscribe = True,  is_earned = False)[0:controller.min_referral_user_of_guard]
                        for users in gard_refaral_user:
                            users.is_earned = True
                            users.save()
                        
                        user.is_subscribe = True
                        user.save()
                        


                        return Response({"success":True, "message":"subscribe successfull!"}, status=status.HTTP_200_OK)
                else:
                    return Response({"success":False, "message":"target not fill up"}, status=status.HTTP_400_BAD_REQUEST)
                

            else:
                return Response({"success":False, 'message':'worng request'}, status=status.HTTP_400_BAD_REQUEST)

        



        elif user.user_type == 'company' and subscribe_plan.plan_for =='company':

            unit_amount = int(subscribe_plan.price * 100)

            price = stripe.Price.create(
                unit_amount=unit_amount,   # price in cents
                currency="usd",
                product=PRODUCT_ID,        # existing product
                # Do NOT include recurring => one-time payment
            )
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price": price.id,
                    "quantity": 1,
                }],
                mode="payment",  
                success_url="https://5r6mdm6l-8001.inc1.devtunnels.ms/",
                cancel_url="https://5r6mdm6l-8001.inc1.devtunnels.ms/",
                client_reference_id=str(user.id),
                metadata={   # <-- use this section
                    "subscribe_plan_id": str(plan_id),
                }
                
            )

            return Response({
                "success":True,
                "payment_url":checkout_session.url,
                
            }, status=status.HTTP_200_OK)
                        
        elif user.user_type == 'guard' and subscribe_plan.plan_for =='guard':

            unit_amount = int(subscribe_plan.price * 100)

            price = stripe.Price.create(
                unit_amount=unit_amount,   # price in cents
                currency="usd",
                product=PRODUCT_ID,        # existing product
               
            )
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price": price.id,
                    "quantity": 1,
                }],
                mode="payment",  
                success_url="https://5r6mdm6l-8001.inc1.devtunnels.ms/",
                cancel_url="https://5r6mdm6l-8001.inc1.devtunnels.ms/",
                client_reference_id=str(user.id),
                metadata={   # <-- use this section
                    "subscribe_plan_id": str(plan_id),
                }    
            )
            return Response({
                "success":True,
                "payment_url":checkout_session.url,
                
            }, status=status.HTTP_200_OK)
        
        return Response({"success":False,"message":"worong plan!"}, status= status.HTTP_400_BAD_REQUEST)
    




# ######################################## End subscribetions ############################
from api.models import LicencesType

class Licence_Types_List(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            ln_types = LicencesType.objects.filter(is_active=True)
            serializer = LicenceTypeSerializer(ln_types, many=True)
            return Response({"success":True,"message":"data fatched!", 'licence_types':serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success":False,"message":"data not fatched!", 'errors':f"{e}"}, status=status.HTTP_400_BAD_REQUEST)




class Certificate_Types_List(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        try:
            crtificate_types = CertificateType.objects.filter(is_active=True)
            serializer = CertificateTypeSerializer(crtificate_types, many=True)
            return Response({"success":True,"message":"data fatched!", 'certificate_types':serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"success":False,"message":"data not fatched!", 'errors':f"{e}"}, status=status.HTTP_400_BAD_REQUEST)


from api.models import CompanyModel    
class Company_Dashboard_Analytics(APIView):
    permission_classes = [IsAuthenticated, IsCompany]

    def get(self, request):
        user = request.user
        try:
            company = CompanyModel.objects.get(company = user)
        except CompanyModel.DoesNotExist:
            return Response({"success": False, "message": "Company profile not found"}, status=status.HTTP_404_NOT_FOUND)

        # Job Counters
        # "Unticked" -> Published + Untasked
        unticked_jobs = JobModel.objects.filter(
            job_provider=company, 
            status__in=['published', 'untasked'],
            is_deleted=False
        ).count()

        # "In Progress" -> Tasked
        jobs_in_progress = JobModel.objects.filter(
            job_provider=company, 
            status='tasked',
            is_deleted=False
        ).count()

        # "Completed" -> Finished
        completed_jobs = JobModel.objects.filter(
            job_provider=company, 
            status='finished',
            is_deleted=False
        ).count()

        # Ratings
        avg_rating = company.average_rating_main
        
        # Industry Rating (Average of all companies)
        industry_avg = CompanyModel.objects.aggregate(Avg('average_rating_main'))['average_rating_main__avg'] or 0
        industry_rating = round(industry_avg, 2)

        # Weekly Job Activity (Last 7 days)
        # We'll count engagements created per day for the last 7 days as a proxy for "activity"
        # Or we can count Active Jobs per day. Correct interpretation of "Activity" bar chart usually implies volume.
        # Let's count *Engagements* (Shifts) scheduled/active for each day.
        
        today = timezone.now().date()
        week_data = []
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        # Get start of the week (or just last 7 days)
        # Let's go with last 7 days for a rolling window, or standard Mon-Sun week. 
        # Dashboard usually shows "This Week" implying current week Mon-Sun.
        
        start_of_week = today - timedelta(days=today.weekday()) # Monday of current week
        
        current_day_date = start_of_week
        for i in range(7):
            # Count engagements that fall on this day
            # An engagement is active on a day if job_date matches
            # engagement -> job_details -> job_date
            
            # Note: EngagementModel links to JobDetails (JobModel). JobModel has job_date.
            # We want to count how many engagements the company has on this specific date.
            
            day_count = EngagementModel.objects.filter(
                job_details__job_provider=company,
                job_details__job_date=current_day_date,
                is_deleted=False
            ).count()
            
            week_data.append({
                "day": days[current_day_date.weekday()],
                "value": day_count,
                "date": current_day_date.strftime("%Y-%m-%d")
            })
            current_day_date += timedelta(days=1)


        # Rating Performance Breakdown
        rating_performance = {
            "communication": company.average_comunication,
            "payment_reliability": company.average_pay_rate, # Mapping pay_rate to payment reliability
            "pay_rates": company.average_pay_rate, # Duplicate or maybe reliability is different?
          
            "Professionalism": company.average_professionalism,
            "Job Support": company.average_job_support
        }

        data = {
            "overview": {
                "unticked_jobs": unticked_jobs,
                "jobs_in_progress": jobs_in_progress,
                "completed_jobs": completed_jobs,
                "average_rating": avg_rating,
                "industry_rating": industry_rating
            },
            "weekly_activity": week_data,
            "rating_performance": rating_performance
        }

        return Response({"success": True, "data": data}, status=status.HTTP_200_OK)
    


class SupportView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if request.user.user_type == "admin":
            messages = SupportMessage.objects.all().order_by("-id")
        else:
            messages = SupportMessage.objects.filter(user=request.user).order_by("-id")
        serializer = SupportMessageSerializer(messages, many=True)
        return Response({"success": True, "messages": serializer.data}, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = SupportMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response({"success": True, "message": "Message sent successfully!"}, status=status.HTTP_201_CREATED)
        return Response({"success": False, "message": "Invalid data", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
