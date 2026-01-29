from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    ROLE_CHOICES = (
        ('admin','Admin'),
        ('teacher','Teacher'),
        ('student','Student'),
    )

    user = models.OneToOneField(User,on_delete=models.CASCADE)
    role = models.CharField(max_length=10,choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

#Making sure that the profile is created every time a user is created
@receiver(post_save, sender=User)
def create_user_profile(sender,instance,created,**kwargs):
    if created:
        Profile.objects.create(user=instance)

#Ensures whenever the user object is saved, the associated profile is also saved
@receiver(post_save,sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

