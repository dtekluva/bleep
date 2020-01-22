from django.contrib import admin
from .models import *

class CivilianAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'twitter_handle',)

class LawyerAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'twitter_handle')

class BuddyAdmin(admin.ModelAdmin):
    list_display = ('firstname', 'lastname', 'phonenumber')

class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('plan',)

class PlanAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(Civilian, CivilianAdmin)
admin.site.register(Lawyer, LawyerAdmin)
admin.site.register(Buddy, BuddyAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Plan, PlanAdmin)
