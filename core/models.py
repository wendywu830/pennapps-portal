from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Application(models.Model):
  objects = models.Manager()
  name = models.CharField(max_length=200) 
  email = models.CharField(max_length=140, primary_key=True)
  app_text1 = models.TextField()
  app_text2 = models.TextField()
  github = models.CharField(max_length=140)
  school = models.CharField(max_length=200)
  first_hackathon = models.CharField(max_length=5)
  timezone = models.CharField(max_length=50)

  #i'm DUMB and migrations are not working for postgres so repurposing is_CA for priority so is_CA = is_late
  is_CA = models.BooleanField(default=False) 
  
  graders = models.CharField(max_length=140, default='') #this is sketchy but oh well - format is username,username,
  num_graders = models.DecimalField(max_digits=1, decimal_places=0, default=0) #max = 2
  comments = models.TextField(default='')

  status = models.CharField(max_length=30, default='N/A') # Accepted, Rejected, Waitlisted, N/A
  rating = models.DecimalField(max_digits=2, decimal_places=1, default=0) #avg rating of those given
  check_in = models.BooleanField(default=False)


