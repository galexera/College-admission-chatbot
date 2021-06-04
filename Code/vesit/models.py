from django.db import models

# Create your models here.
class UserConversation(models.Model):
    UserQuestion=models.CharField(max_length=2000)
    ChatbotResponse=models.CharField(max_length=10000)

    def __str__(self):
        return self.UserQuestion

class Webdata(models.Model):
    title=models.CharField(max_length=1000)
    address=models.CharField(max_length=2000)
    
    def __str__(self):
        return self.title