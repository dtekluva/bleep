from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
import secrets
from cors.models import *

# Create your models here.
class Plan(models.Model):
    name           = models.CharField(max_length = 30)
    num_of_buddies = models.IntegerField()
    num_of_lawyers = models.IntegerField()
    num_of_devices = models.IntegerField()
    price          = models.IntegerField()

    def __str__(self):
        return self.name

class Subscription(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE)
    plan       = models.ForeignKey(Plan, on_delete=models.CASCADE)
    sub_date   = models.DateField()
    duration   = models.DateField()
    expiration = models.DateField()

        # return self.plan

class Lawyer(models.Model):
    user           = models.OneToOneField(User, on_delete=models.CASCADE)
    plan           = models.ForeignKey(Plan, on_delete=models.CASCADE, blank = True, null = True)
    firstname      = models.CharField( max_length = 30)
    lastname       = models.CharField( max_length = 30)
    twitter_handle = models.CharField( max_length = 150, blank = True, null = True)
    address        = models.CharField( max_length = 150, blank = True, null = True)
    email          = models.CharField( max_length = 150, blank = True, null = True)
    phone          = models.CharField( max_length = 150, blank = True, null = True)
    longitude      = models.FloatField(blank = True, null = True)
    latitude       = models.FloatField(blank = True, null = True)
    token          = models.CharField(max_length=200, null=True, blank = True)
    
    def authenticate(self, username, password, request):
        user = authenticate(username = username.lower(), password = password)

        if user and (user.username == username): #allows user to login using username
                # No backend authenticated the credentials

                user = User.objects.get(id=user.id)
                login(request, user)
                self.add_token()

                return True

        else: return False

    def __str__(self):
        return self.firstname

    def create(self, username = "null", firstname = "null", lastname = "null", twitter_handle = "", email = "null@null.com", password = "00000000", address = "none supplied", phone = "0" ):

        user = User.objects.create(first_name = firstname, last_name = lastname, email = email)
        user.set_password(password)
        user.username = phone

        user.save()

        lawyer = Lawyer.objects.create(user = user, username = username, firstname = firstname, lastname = lastname, twitter_handle = twitter_handle, email = email, address = address )

        lawyer.save()

        return lawyer

class Buddy(models.Model):
    CHOICES     = [
        ('father', 'Father'),
        ('mother', 'Mother'),
        ('brother', 'Brother'),
        ('sister', 'Sister'),
        ('uncle', 'Uncle'),
        ('aunty', 'Aunty'),
        ('friend', 'Friend'),
        ('colleague', 'Colleague'),
        ('boss', 'Boss'),
        ('pastor','Pastor'),
        ('mentor', 'Mentor'),
        ('employee', 'Employee'),
    ]
    firstname    = models.CharField(max_length = 30)
    lastname     = models.CharField(max_length = 30)
    phonenumber  = models.IntegerField()
    relationship = models.CharField(max_length = 30, choices = CHOICES )

    def __str__(self):
        return self.firstname

class Civilian(models.Model):
    user           = models.OneToOneField(User, on_delete=models.CASCADE)
    lawyer         = models.ManyToManyField(Lawyer, blank = True, null = True)
    plan           = models.ForeignKey(Plan, on_delete=models.CASCADE, blank = True, null = True)
    buddy          = models.ForeignKey(Buddy, on_delete=models.CASCADE, blank = True, null = True)
    firstname      = models.CharField( max_length = 30)
    lastname       = models.CharField( max_length = 30)
    twitter_handle = models.CharField( max_length = 150, blank = True, null = True)
    address        = models.CharField( max_length = 150, blank = True, null = True)
    email          = models.CharField( max_length = 150, blank = True, null = True)
    phone          = models.CharField( max_length = 150, blank = True, null = True)
    longitude      = models.FloatField(blank = True, null = True)
    latitude       = models.FloatField(blank = True, null = True)
    token          = models.CharField(max_length=200, null=True, blank = True)
    
    def authenticate(self, username, password, request):
        user = authenticate(username = username.lower(), password = password)

        if user and (user.username == username): #allows user to login using username
                # No backend authenticated the credentials

                user = User.objects.get(id=user.id)
                login(request, user)
                self.add_token()

                return True

        else: return False

    def add_token(self):
        Token_man(self).add_token()

    def verify_token(self, token):
        if self.token == token:
            return True
        else:
            return False

    def __str__(self):
        return self.user.username

    def __str__(self):
        return self.firstname

    def create(self, username = "null", firstname = "null", lastname = "null", twitter_handle = "@", email = "null@null.com", password = "00000000", address = "none supplied", phone = "0" ):

        user = User.objects.create(first_name = firstname, last_name = lastname, username = username, email = email)
        user.set_password(password)
        user.username = phone

        user.save()

        civilian = Civilian.objects.create(user = user, firstname = firstname, lastname = lastname, twitter_handle = twitter_handle, email = email, address = address, phone = phone )

        civilian.save()

        return civilian

#USER ACTUALLY REFERS TO USERACCOUNT MODEL OR OBJECT JUST USED USER FOR BETTER UNDERSTANDING 
class Token_man():
    
    def __init__(self, user):
        self.user = user
        
    def generate_token(self):
        return secrets.token_urlsafe(40)

    def add_token(self):
        self.user.token = self.generate_token()
        self.user.save()
        # # print(self.user.token)
