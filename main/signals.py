from django.dispatch import receiver
from django.core import signals
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from helpers.verification import Verifier

@receiver(post_save, sender=User)
def send_verification_message(sender, **kwargs):

    if kwargs.get('created', False):
        user = kwargs.get("instance")
        verifier = Verifier(user)
        verifier.gen_code()
        print(verifier.get_code())
        print("------------------------------sending code..!!!---------------------------------")


post_save.connect(send_verification_message, sender = User)