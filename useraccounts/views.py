from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
# from useraccounts.models import UserAccount, Token_man, Session
from main.models import *
from main import views
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers
from django.shortcuts import get_object_or_404
import json
from helpers.http_codes import http_codes
# from snippet import helpers
import ast

from django.shortcuts import render



def login_view(request):

        if request.method == 'POST':

                if True:

                        email    = request.POST.get("email", "")
                        username = request.POST.get("username", "").lower()
                        email = email.lower()
                        password    = request.POST.get("password", "")

                        try:
                                #GET CORRESPONDING USERNAME FROM EMAIL POSTED
                                # username = User.objects.get(email = email).username
                                # user = User.objects.get(username=username)
                                user = authenticate(username = username.lower(), password = password)

                                if (user.username == username): #allows user to login using username
                                        # No backend authenticated the credentials

                                        user = User.objects.get(username=username)
                                        login(request, user)

                                        return HttpResponse(json.dumps({"response":"success"}))
                        except:
                                return HttpResponse(json.dumps({"response":"failure"}))   
                else:
                        return HttpResponse(json.dumps({"response":"failure"}))    

        else:
                return render(request, "login.html")

def login_as_view(request, id):

        # form = LoginForm(request.POST)

        if True:

                
                #GET CORRESPONDING USERNAME FROM EMAIL POSTED
                customer = Customer.objects.get(id = id)

                user = customer.user
                login(request, user)

                
                return redirect(views.index)
        else:
                return HttpResponse(json.dumps({"response":"failure"}))    



def update_password(request):

        user = User.objects.get(pk = request.user.id)

        if request.method == 'POST':
                # # print(request.POST)
                old = request.POST.get("old")
                new = request.POST.get("new")
                customer_id = request.POST.get("customer_id", False)
                
                if customer_id == False:

                        user = authenticate(username = user.username, password = old)

                        if user:
                                user.set_password(new)
                                user.save()
                                login(request, user)

                                return HttpResponse(json.dumps({"response": "success"}))
                        else:
                                return HttpResponse(json.dumps({"response": "failure"}))
                else:
                        customer = Customer.objects.get(id = customer_id)

                        user = authenticate(username = customer.user.username, password = old)


                        if user:
                                user.set_password(new)
                                user.save()

                                return HttpResponse(json.dumps({"response": "success"}))
                        else:
                                return HttpResponse(json.dumps({"response": "failure"}))

 
@csrf_exempt
def mobile_signin(request):

        if request.method == 'POST':

                data     = json.loads(request.body)
                phone    = data["email"]
                password = data["password"]

                try:
                        user_account = UserAccount.objects.get(username = username)
                except:
                        resp = HttpResponse(json.dumps({"response": {
                            "code": http_codes["Unauthorized"],
                            "task_successful": False,
                            "content": {
                                "user": "",
                                "message": f"Authentication credentials mismatch"
                            },
                            "auth_keys": {"access_token": ""}
                        }
                        }))

                        return CORS(resp).allow_all()

                auth_successful = user_account.authenticate(user_account.username, password, request)
                print(auth_successful)

                if auth_successful:                      

                        resp = HttpResponse(json.dumps({"response": {
                            "code": http_codes["ok"],
                            "task_successful": True,
                            "content": {
                                "user": user.firstname,
                                "message": f"created and authenticated new user - ({civilian.firstname})"
                            },
                            "auth_keys": {"access_token": civilian.get_token()}
                        }
                        }))
                        return CORS(resp).allow_all()

                else:
                        resp = HttpResponse(json.dumps({"response": "authentication failure","content": {"user":user_account.email, "message":""}, "auth_keys": {"access_token": ""}}))

                        return CORS(resp).allow_all()

        else:
                resp = HttpResponse(json.dumps({"response": "bad request method","content": {"user":"", "message":""}, "auth_keys": {"access_token": ""}}))

                return CORS(resp).allow_all()

@csrf_exempt
def mobile_register_civilian(request):

        if request.method == 'POST':

                data = json.loads(request.body)
                first_name = data["firstname"]
                last_name = data["lastname"]
                phone = data["phone"]
                password = data["password"]
                
                

                if Civilian.objects.filter(phone = phone).exists() or User.objects.filter(username = phone).exists():

                        resp = (json.dumps({"response": {"task_successful": False, "content": {
                                        "code": http_codes["Precondition Failed"], "user": first_name, "message": "phone number may already exist"}, "auth_keys": {"access_token": "NULL"}}}))
                        
                        return CORS(resp).allow_all()
                        
                else:
                        
                        civilian = Civilian().create(firstname= first_name, lastname= last_name, phone= phone, password= password)

                        civilian.authenticate(civilian.user.username, password, request)

                        resp = (json.dumps({"response": {
                            "code": http_codes["Created"],
                            "task_successful": True,
                            "content": {
                                "user": civilian.firstname,
                                "message": f"created and authenticated new user - ({civilian.firstname})"
                            },
                            "auth_keys": {"access_token": civilian.get_token()}
                        }
                        })
                                        )

                        return CORS(resp).allow_all()


        else:
                resp = (json.dumps({"response": {"task_successful": False, "code": http_codes["Method Not Allowed"], "content": {
                                    "user": "", "message": "bad request method"}, "auth_keys": {"access_token": ""}}}))

                return CORS(resp).allow_all()


@csrf_exempt
def mobile_register_lawyer(request):

        if request.method == 'POST':

                data = json.loads(request.body)
                first_name = data["firstname"]
                last_name = data["lastname"]
                phone = data["phone"]
                password = data["password"]                

                if Lawyer.objects.filter(phone = phone).exists() or User.objects.filter(username = phone).exists():

                        resp = (json.dumps({"response": {"task_successful": False, "content": {
                                        "code": http_codes["Precondition Failed"], "user": first_name, "message": "phone number may already exist"}, "auth_keys": {"access_token": "NULL"}}}))

                        return CORS(resp).allow_all()    
                        
                else:
                        
                        lawyer = Lawyer().create(firstname= first_name, lastname= last_name, phone= phone, password= password)

                        lawyer.authenticate(lawyer.user.username, password, request)

                        resp = (json.dumps({"response": {
                            "code": http_codes["Created"],
                            "task_successful": True,
                            "content": {
                                "user": lawyer.firstname,
                                "message": f"created and authenticated new user - ({lawyer.firstname})"
                            },
                            "auth_keys": {"access_token": lawyer.get_token()}
                        }
                        })
                                        )

                        return CORS(resp).allow_all()                    

        else:
                resp = (json.dumps({"response": {"task_successful": False, "code": http_codes["Method Not Allowed"],                            "content": {
                                        "user": "", "message": "bad request method"}, "auth_keys": {"access_token": ""}}}))

                return CORS(resp).allow_all()
