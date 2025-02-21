from django.db import models
from django.contrib.auth.hashers import check_password

# Create your models here.

class UserInfo(models.Model):
    name=models.CharField(max_length=30)
    email=models.EmailField(unique=True)
    password=models.CharField(max_length=16)

    def is_authenticated(self,email,password):
       try:
            if self.email==email and check_password(password,self.password):
                return True
       except:
         return False 