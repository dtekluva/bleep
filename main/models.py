import sys
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import json, datetime, random
from beeep.settings import BASE_DIR
# from dateutil import parser

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
    is_verified    = models.BooleanField(default = False)
    token          = models.CharField(max_length=200, null=True, blank = True)
    image          =  models.ImageField(upload_to = 'profile_pics/',blank=False,null=True)

    def save_image(self, *args, **kwargs):

        self.uploadedImage = self.compressImage(self.uploadedImage)
        super(Lawyer, self).save(*args, **kwargs)
        
    def compressImage(self,uploadedImage):

        imageTemporary = Image.open(uploadedImage)
        outputIoStream = BytesIO()
        imageTemporaryResized = imageTemporary.resize( (1020,573) ) 
        imageTemporary.save(outputIoStream , format='JPEG', quality=60)
        outputIoStream.seek(0)
        uploadedImage = InMemoryUploadedFile(outputIoStream, 'ImageField', "%s.jpg" % uploadedImage.name.split('.')[0], 'image/jpeg', sys.getsizeof(outputIoStream), None)

        return uploadedImage

    def __str__(self):
        return self.user.username

    def get_token(self):
        if self.is_verified:
            return self.user.token_set.all().order_by("-id")[0].token
        else:
            return {"token":False, "message": "User Not Yet Verified"}

    def __str__(self):
        return self.firstname

    def create(self, username = "null", firstname = "null", lastname = "null", twitter_handle = "", email = "null@null.com", password = "00000000", address = "none supplied", phone = "0" ):

        user = User.objects.create(username = phone, first_name = firstname, last_name = lastname, email = email)
        user.set_password(password)
        user.username = phone
        user.save()

        lawyer = Lawyer.objects.create(user = user, firstname = firstname, lastname = lastname, twitter_handle = twitter_handle, email = email, address = address )

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

    class Meta:
        verbose_name_plural = "Buddies"

class Civilian(models.Model):
    user           = models.OneToOneField(User, on_delete=models.CASCADE)
    lawyer         = models.ManyToManyField(Lawyer, blank = True)
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
    is_verified    = models.BooleanField(default = False)
    image          =  models.ImageField(upload_to = 'profile_pics/',blank=False,null=True)

    def save_image(self, *args, **kwargs):

        self.uploadedImage = self.compressImage(self.uploadedImage)
        super(Civilian, self).save(*args, **kwargs)
        
    def compressImage(self,uploadedImage):

        imageTemporary = Image.open(uploadedImage)
        outputIoStream = BytesIO()
        imageTemporaryResized = imageTemporary.resize( (1020,573) ) 
        imageTemporary.save(outputIoStream , format='JPEG', quality=60)
        outputIoStream.seek(0)
        uploadedImage = InMemoryUploadedFile(outputIoStream, 'ImageField', "%s.jpg" % uploadedImage.name.split('.')[0], 'image/jpeg', sys.getsizeof(outputIoStream), None)

        return uploadedImage

    def get_token(self):
        if self.is_verified:
            return self.user.token_set.all().order_by("-id")[0].token
        else:
            return {"token":False, "message": "User Not Yet Verified"}

    def create(self, username = "null", firstname = "null", lastname = "null", twitter_handle = "@", email = "null@null.com", password = "00000000", address = "none supplied", phone = "0" ):

        user = User.objects.create(username = phone, first_name = firstname, last_name = lastname, email = email)
        user.set_password(password)

        civilian = Civilian.objects.create(user = user, firstname = firstname, lastname = lastname, twitter_handle = twitter_handle, email = email, address = address, phone = phone )

        return civilian


class Token(models.Model):

    device_id = models.CharField(max_length=200, null=True, blank = True) #mac address preferably
    username  = models.CharField(max_length=200, null=True, blank = True)
    device_name = models.CharField(max_length=200, null=True, blank = True)
    user_agent  = models.CharField(max_length=200, null=True, blank = True)
    token     = models.CharField(max_length=200, null=True, blank = True)
    user      = models.ForeignKey(User, on_delete= models.CASCADE)
    is_active = models.BooleanField(default = False)
    icon      = models.ImageField(upload_to = 'token_icons/',blank=False,null=True)

    def generate_token(self):
        return secrets.token_urlsafe(40)

    def save(self, *args, **kwargs):

        if kwargs.get("is_new"):
            self.token = self.generate_token()

        super(Token, self).save()

    def deactivate(self):
        self.is_active = False
        self.save()

    def activate(self):
        self.is_active = True
        self.save()

    def add_token(self, request = False):
        if request:
            self.device_name = request.META.get("COMPUTERNAME", "")
            self.user_agent = request.META.get("HTTP_USER_AGENT", "")
        self.is_active = True
        self.save(is_new = True)
    
    def verify_token(self, token):
        if self.token_set.filter(token = token).exists():
            return True
        else:
            return False

    @staticmethod
    def authenticate(username, password, request):
        user = authenticate(username = username.lower(), password = password)

        if user and (user.username == username): #allows user to login using username
                # No backend authenticated the credentials

                user = User.objects.get(id=user.id)
                login(request, user)
                Token(user = user).add_token(request)

                return True

        else: return False


class Activation_Code_Manager:

    #MAKE SURE TO IMPORT BASE_DIR FROM SETTINGS
    FILENAME = "/verification_codes.json"
    FILE_DIR = BASE_DIR.replace("\\", "/") + FILENAME

    def __init__(self, user):
        self.username = user.username
        self.user = user

    def gen_code(self):
        code = "".join([str(random.randint(0,9)) for i in range(4)])
        new_code = {"date": datetime.datetime.now().strftime("%d-%m-%Y"), "code":code}
        self.update(new_code)
    
    def read_data(self):

        try:
            file = open(self.FILE_DIR, "r")
            json.loads(file.read())
            file.close()
        except :

            file = open(self.FILE_DIR, "w")
            file.write(json.dumps({"username":{"date":"01/10/2010", "code":"1234"}}))
            file.close()

        file = open(self.FILE_DIR, "r")
        data = json.loads(file.read())

        return data
    
    def write_data(self, data):

        file = open(self.FILE_DIR, "w")
        file.write(json.dumps(data))
        file.close()

        return True

    def update(self, value, timed  = False):

        data = self.read_data()
        data[self.user.username] = value
        self.write_data(data)

        print("Successfully cached")
        return {f"cached-{self.user.username}" : True}


    def get_code(self):

        data = self.read_data().get(self.user.username, [])

        return data

    def verify_code(self, code):

        return self.get_code()['code'] == code
