from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Customuser(models.Model):
    class Category(models.IntegerChoices):
        READER = 0
        WRITER = 1
        MODERATOR = 2

    djangouser = models.OneToOneField(User, on_delete=models.CASCADE)
    usertype = models.IntegerField(choices=Category.choices, default=Category.READER)
    name = models.CharField(max_length=100)
    dob = models.DateField()
    frozen = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Application(models.Model):
    class Category(models.IntegerChoices):
        READER = 0
        WRITER = 1
        MODERATOR = 2
    
    djangouser = models.OneToOneField(User, on_delete=models.CASCADE)
    totype = models.IntegerField(choices=Category.choices, default=Category.WRITER)
    req = models.CharField(max_length=500, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.djangouser.username