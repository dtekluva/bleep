import sys
from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from PIL import Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import json, datetime, random
import pandas as pd
from beeep.settings import BASE_DIR
from scipy.spatial import distance
from django.db.models import F, Func, Value, CharField
from math import radians, cos, sin, asin, sqrt
from helpers.email import send_verification_mail


# from dateutil import parser

import secrets
from cors.models import *

# Create your models here.
class Plan(models.Model):

    CHOICES     = [
        ('civilian', 'civilian'),
        ('lawyer', 'lawyer'),
    ]

    name           = models.CharField(max_length = 30)
    num_of_buddies = models.IntegerField(default=0)
    num_of_lawyers = models.IntegerField(default=0)
    num_of_devices = models.IntegerField(default=0)
    price          = models.IntegerField(default=0)
    type_of_user    = models.CharField(max_length = 30, choices = CHOICES, default = "civilian" )

    @staticmethod
    def get_all_plans():

        civillian_plans = Plan.objects.all().values("name", "num_of_buddies", "num_of_devices", "price", "type_of_user", "id")

        return list(civillian_plans)

    def __str__(self):
        return self.name

class Subscription(models.Model):
    user       = models.OneToOneField(User, on_delete=models.CASCADE)
    plan       = models.ForeignKey(Plan, on_delete=models.CASCADE)
    plan_price = models.IntegerField(default=0)
    sub_date   = models.DateField()
    duration   = models.DateField()
    expiration = models.DateField()

    def __str__(self):
        return self.user.firstname

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

    @staticmethod
    def get_closest(user):

        lawyers = Lawyer.objects.all().values("longitude", "latitude", "firstname", "lastname", "phone")

        lawyer_frame = pd.DataFrame(list(lawyers))

        distances = solve_distances(lawyer_frame, [user.longitude, user.latitude])
        lawyer_frame["distance"] = distances

        return lawyer_frame.sort_values('distance').to_dict(orient="index")

    def get_details(self):
        user_data = self.__dict__
        data = {}

        for key in user_data:
            if key.startswith("_"):
                continue
                
            if key == "image":

                try:
                    data["image"] = user_data[key].url
                except:
                    data["image"] = ""
                    
                continue
            
            data[key] = user_data[key]
        
        return data

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

    def add_location(self, geolocation):

        self.longitude = geolocation["longitude"]
        self.latitude = geolocation["latitude"]
        self.save()

        return True

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
    phonenumber  = models.CharField(max_length = 30)
    relationship = models.CharField(max_length = 30, choices = CHOICES )
    user          = models.ForeignKey(User, on_delete=models.CASCADE, blank = True, null = True)

    def __str__(self):
        return self.firstname

    class Meta:
        verbose_name_plural = "Buddies"

    def get_details(self):
        user_data = self.__dict__
        data = {}

        for key in user_data:
            if key.startswith("_"):
                continue
                
            if key == "image":

                try:
                    data["image"] = user_data[key].url
                except:
                    data["image"] = ""
                    
                continue
            
            data[key] = user_data[key]
        
        return data

class Civilian(models.Model):
    user           = models.OneToOneField(User, on_delete=models.CASCADE)
    lawyer         = models.ManyToManyField(Lawyer, blank = True)
    plan           = models.ForeignKey(Plan, on_delete=models.CASCADE, blank = True, null = True)
    # buddy          = models.ForeignKey(Buddy, on_delete=models.CASCADE, blank = True, null = True)
    firstname      = models.CharField( max_length = 30)
    lastname       = models.CharField( max_length = 30)
    twitter_handle = models.CharField( max_length = 150, blank = True, null = True)
    address        = models.CharField( max_length = 150, blank = True, null = True)
    email          = models.CharField( max_length = 150, blank = True, null = True)
    phone          = models.CharField( max_length = 150, blank = True, null = True)
    longitude      = models.FloatField(blank = True, null = True)
    latitude       = models.FloatField(blank = True, null = True)
    is_verified    = models.BooleanField(default = False)
    is_beeeping    = models.BooleanField(default = False)
    image          =  models.ImageField(upload_to = 'profile_pics/',blank=False,null=True)


    def save_image(self, *args, **kwargs):

        self.uploadedImage = self.compressImage(self.uploadedImage)
        super(Civilian, self).save(*args, **kwargs)

    def get_buddies(self):
        buddies = self.user.buddy_set.all().values("lastname", "firstname", "phonenumber", "relationship", "id", )

        return list(buddies)

    def update_details(self, data):
        
        response = {"status":True, "message":""}
        phone = data.get("phone")
        if phone:
            self.phone = phone
            self.user.username = phone
            self.user.save()

        password = data.get("password")
        if password:
            self.user.set_password(password)
            self.user.save()
            
        firstname = data.get("firstname")
        if firstname:
            self.firstname = firstname

        lastname = data.get("lastname")
        if lastname:
            self.lastname = lastname

        twitter_handle = data.get("twitter_handle")
        if twitter_handle:
            self.twitter_handle = twitter_handle

        address = data.get("address")
        if address:
            self.address = address
        email = data.get("email")

        if email:
            self.email = email
            self.user.email = email
            self.user.save()

        plan_id = data.get("plan")
        if plan_id:
            plan = Plan.objects.filter(id = plan_id)

            if plan and plan[0].type_of_user == "civilian":
                self.plan = plan[0]
                self.save()
            else:
                response["status"] = False
                return response
        
        self.save()

        return response

    def add_buddy(self, data):
        
        # allowed_buddies = self.plan.num_of_buddies
        firstname = data.get("firstname", "")
        lastname = data.get("lastname", "")
        phone =   data.get("phone", "")
        relationship = data.get("relationship", "")

        new_buddy = Buddy(firstname = firstname, lastname = lastname, phonenumber = phone, relationship = relationship, user = self.user)

        new_buddy.save()

        return { "is_added": True, "details" : new_buddy.get_details()}

    def get_details(self):
        user_data = self.__dict__
        data = {}

        for key in user_data:
            if key.startswith("_"):
                continue
                
            if key == "image":

                try:
                    data["image"] = user_data[key].url
                except:
                    data["image"] = ""
                    
                continue
            
            data[key] = user_data[key]
        
        data["buddies"] = self.get_buddies()

        return data
        
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
        user.save(0)
        # print(password)

        civilian = Civilian.objects.create(user = user, firstname = firstname, lastname = lastname, twitter_handle = twitter_handle, email = email, address = address, phone = phone )

        return civilian

    def add_location(self, geolocation):

        self.longitude = geolocation["longitude"]
        self.latitude = geolocation["latitude"]
        self.save()

        return True

    def get_location(self):

        return {
                    "fname": self.lastname,
                    "lname": self.firstname,
                    "lng": self.longitude, 
                    "lat": self.latitude
                }

    def has_active_beeep(self):
        return self.user.beeep_set.filter(is_active = True).exists()
    
    def get_all_beeeps(self):

        raw_query =  list(self.user.beeep_set.all().values())
        
        for i in range(len(raw_query)):
            print(raw_query[i]["beeep_start_time"])
            raw_query[i]["beeep_start_time"] = raw_query[i]["beeep_start_time"].strftime("%m/%d/%Y, %H:%M:%S")
            raw_query[i]["beeep_end_time"] = raw_query[i]["beeep_end_time"].strftime("%m/%d/%Y, %H:%M:%S")

        
        return list(raw_query)

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

            token_exists = True
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
            current_tokens = self.user.token_set.all()

            civilian_or_lawyer = Civilian.objects.filter(user = self.user) or Lawyer.objects.filter(user = self.user)

            try:
                if not (civilian_or_lawyer[0].plan.num_of_devices > current_tokens.count()):## CHECK HOW MANY DEVICES, THE USER'S PLAN ALLOWS HIM TO HAVE
                    current_tokens[0].delete()

            except AttributeError:
                pass

            self.device_name = request.META.get("COMPUTERNAME", "")
            self.user_agent = request.META.get("HTTP_USER_AGENT", "")
        self.is_active = True
        self.save(is_new = True)
    
    @staticmethod
    def verify_token(request):

        user_id  = request.META.get("HTTP_PHONE")

        try:
            user = User.objects.get(username = user_id)
        except:
            return False

        token = request.META.get("HTTP_AUTHORIZATION")
        
        token_exists = user.token_set.filter(token = token).exists()

        if token_exists:
            return {"authenticated": True, "user": user}
        else:
            return False

    @staticmethod
    def authenticate(username, password, request):
        # user_logged = User.objects.get(username = username)
        user_model = Civilian.objects.filter(user__username = username) or Lawyer.objects.filter(user__username = username)
        user = authenticate(username = username , password = password)
        # print(user, username, username.lower())

        if user and (user.username == username): #allows user to login using username
                # No backend authenticated the credentials

                if user_model[0].is_verified:

                    user = User.objects.get(id=user.id)
                    login(request, user)
                    Token(user = user).add_token(request)

                    return {"success" : True, "message":"Verified"}

                else:
                    return {"success" : False, "message":"Not yet Verified"}

        else: return {"success" : False, "message":"Incorrect details"}

    @staticmethod
    def authenticate_from_verify(user, request):

        if user.is_verified:

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
        send_verification_mail(code,self.user)
    
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

        # print("Successfully cached")
        return {f"cached-{self.user.username}" : True}


    def get_code(self):

        data = self.read_data().get(self.user.username, [])

        return data

    def verify_code(self, code):
        # print(self.get_code()['code'] , code)

        return self.get_code()['code'] == code

class Beeep(models.Model):
    user       = models.ForeignKey(User, on_delete=models.CASCADE, blank = True, null = True)
    start_lng  = models.FloatField(default=0)
    start_lat  = models.FloatField(default=0)
    end_lng    = models.FloatField(default=0)
    end_lat    = models.FloatField(default=0)
    plan_price = models.IntegerField(default=0)
    beeep_start_time = models.DateTimeField(auto_now_add=True, blank=True)
    beeep_end_time   = models.DateTimeField(auto_now=True, blank=True)
    is_active        = models.BooleanField(default = True)

    def __str__(self):
        return self.user.username

    @staticmethod
    def handle_beeep(civilian, request):

        data = json.loads(request.body)
        lat = data.get("latitude")
        lng = data.get("longitude")
        action = data.get("action")
        user_type = data.get("user_type")

        if action == "start":
            

            if civilian.has_active_beeep():
                return {"status":True, "message": "Beeep already started"}
            
            Beeep(user = civilian.user, start_lng = lng, start_lat = lat).save()

            return {"status":True, "message": "New Beeep started"}

        else:

            old_beeeps = civilian.user.beeep_set.filter(is_active = "True")
            
            if old_beeeps.exists():

                # old_beeeps.update(is_active = "False")
                # print(last_beeep)

                last_beeep = old_beeeps.last()
                last_beeep.is_active = False
                last_beeep.beeep_end_time = datetime.datetime.now()
                last_beeep.save()

                return {"status":True, "message": "Beeep Successfully Ended Weldone"}

            else:
                return {"status":True, "message": "Sorry No Beeep To Successfully End"}

def solve_distances(dataframe, reference):
    # print("-------------",reference)
    f = lambda row: haversine( row.latitude ,row.longitude,  reference[1], reference[0])

    distances = dataframe.apply(f, axis = 1)
    
    return distances
    
def haversine(lat1, lon1, lat2, lon2):

      R = 6372.8  # this is in kilometers.  For Earth radius in miles use 3959.87433 miles

      dLat = radians(lat2 - lat1)
      dLon = radians(lon2 - lon1)
      lat1 = radians(lat1)
      lat2 = radians(lat2)

      a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
      c = 2*asin(sqrt(a))

      return R * c
