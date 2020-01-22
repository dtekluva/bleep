from django.db import models
from django.contrib.auth.models import User

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
    plan           = models.ForeignKey(Plan, on_delete=models.CASCADE)
    firstname      = models.CharField( max_length = 30)
    lastname       = models.CharField( max_length = 30)
    twitter_handle = models.CharField( max_length = 150, blank = True, null = True)
    longitude      = models.FloatField()
    latitude       = models.FloatField()

    def __str__(self):
        return self.firstname


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
    lawyer         = models.ManyToManyField(Lawyer)
    plan           = models.ForeignKey(Plan, on_delete=models.CASCADE)
    buddy          = models.ForeignKey(Buddy, on_delete=models.CASCADE)
    firstname      = models.CharField( max_length = 30)
    lastname       = models.CharField( max_length = 30)
    twitter_handle = models.CharField( max_length = 150, blank = True, null = True)
    longitude      = models.FloatField()
    latitude       = models.FloatField()

    def __str__(self):
        return self.firstname
