from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Story(models.Model):
    class Pg(models.IntegerChoices):
        UNIVERSAL = 0
        ADOLESCENT = 1
        ADULT = 2

    title = models.CharField(max_length=50)
    summary = models.CharField(max_length=200)
    approved = models.BooleanField(default=False)
    rating = models.IntegerField(choices=Pg.choices, default=Pg.UNIVERSAL)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

class Section(models.Model):
    is_starting = models.BooleanField(default=False)
    is_ending = models.BooleanField(default=False)
    text = models.TextField(max_length=3000)
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    storypos = models.CharField(max_length=20)

class Sectionlink(models.Model):
    fromsection = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='fromsection')
    tosection = models.ForeignKey(Section, on_delete=models.CASCADE, related_name='tosection')
    button = models.CharField(max_length=50)

class Userdata(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    story = models.ForeignKey(Story, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.CASCADE)




