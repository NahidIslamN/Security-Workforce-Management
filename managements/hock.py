

import stripe
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from api.models import CustomUser, Invoices, SubscribtionPlan, CompanyModel, JobApplications
from managements.models import PaymentController
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

# Set your secret key
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY
@csrf_exempt
def stripe_webhook(request):
    try:
        if request.method == "POST":
            payload = request.body
            sig_header = request.META['HTTP_STRIPE_SIGNATURE']
            endpoint_secret = settings.STRIPE_WEBHOCK_SECRET # Your webhook secret from Stripe

            # Verify the webhook signature
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, endpoint_secret
                )
            except ValueError as e:
                return JsonResponse({'message': 'Invalid payload'}, status=400)
            except stripe.error.SignatureVerificationError as e:
                return JsonResponse({'message': 'Invalid signature'}, status=400)

            # Handle different event types
            if event['type'] == 'checkout.session.completed':
                session = event["data"]["object"]
                payment_intent = event['data']['object']  # Contains the PaymentIntent
                user_id = payment_intent.get('client_reference_id')
                plan_id = session["metadata"]["subscribe_plan_id"]
                is_reffaral = False


                try:
                    is_reffaral = session["metadata"]["is_reffaral"]
                except:
                    pass

                user = CustomUser.objects.get(id = user_id)
                sub_plan = SubscribtionPlan.objects.get(id=plan_id)
                invoice_duration = sub_plan.duraton_day

                if is_reffaral:
                    controller = PaymentController.objects.filter().order_by('-id').first()
                    if user.user_type == "company":
                        company = CompanyModel.objects.get(company = user)
                        r_users = company.refaral_users.filter(is_subscribe = True,  is_earned = False)[0:controller.min_referral_user_of_company]
                        for users in r_users:
                            users.is_earned = True
                            users.save() 
                    else:
                        company = JobApplications.objects.get(candidate = user)
                        r_users = company.refaral_users.filter(is_subscribe = True,  is_earned = False)[0:controller.min_referral_user_of_guard]
                        for users in r_users:
                            users.is_earned = True
                            users.save() 



                    if Invoices.objects.filter(user =user, is_finished = False).exists():
                        last_incoice = Invoices.objects.filter(user =user, is_finished = False).order_by('-created_at').first()
                        end_date = last_incoice.end_date
                        invoices = Invoices.objects.create(
                            user = user,
                            invoice_date = timezone.now().date(),
                            plan = sub_plan                        
                        )
                        invoices.end_date = end_date + timedelta(days=invoice_duration)
                        discount_price = Decimal(session["metadata"]["discount_price"])
                        invoices.price = sub_plan.price - discount_price
                        invoices.save()
                        user.is_subscribe = True
                        
                        user.save()
                        return JsonResponse({"success":True})

                    else:
                        invoices = Invoices.objects.create(
                            user = user,
                            invoice_date = timezone.now().date(),
                            plan = sub_plan                        
                        )
                        invoices.end_date = timezone.now().date() + timedelta(days=invoice_duration)
                        discount_price = Decimal(session["metadata"]["discount_price"])
                        invoices.price = sub_plan.price - discount_price
                        invoices.save()
                        user.is_subscribe = True
                        user.save()
                        return JsonResponse({"success":True})
                    


                else:       
                
                    if Invoices.objects.filter(user =user, is_finished = False).exists():
                        last_incoice = Invoices.objects.filter(user =user, is_finished = False).order_by('-created_at').first()
                        end_date = last_incoice.end_date
                        invoices = Invoices.objects.create(
                            user = user,
                            invoice_date = timezone.now().date(),
                            plan = sub_plan                        
                        )
                        invoices.end_date = end_date + timedelta(days=invoice_duration)
                        invoices.price = sub_plan.price
                        invoices.save()
                        user.is_subscribe = True
                        #if everytime 
                        user.save()
                        return JsonResponse({"success":True})

                    else:
                        invoices = Invoices.objects.create(
                            user = user,
                            invoice_date = timezone.now().date(),
                            plan = sub_plan                        
                        )
                        invoices.end_date = timezone.now().date() + timedelta(days=invoice_duration)
                        invoices.price = sub_plan.price
                        invoices.save()
                        user.is_subscribe = True
                        user.save()
                        return JsonResponse({"success":True})
            
    except Exception as a:
        with open ('error.txt', 'a') as e:
            e.write(f'\n{a}')
        
        return JsonResponse({"success":False})
        
        

           
        
        
        
        