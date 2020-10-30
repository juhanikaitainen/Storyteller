from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Wallet(models.Model):
    balance = models.DecimalField(max_digits=8, decimal_places=2)
    owner = models.OneToOneField(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.owner.username

class Transaction(models.Model):
    person = models.ForeignKey(User, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    withdrawn = models.BooleanField(default=True)
    amount = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return  self.person.username + " " + str(self.timestamp)

    

