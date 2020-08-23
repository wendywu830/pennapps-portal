from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from core.models import Application
import pandas as pd
import random
import os
import csv
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import decimal
import json

# Create your views here.

def dashboard(request):
  if request.user.is_authenticated:
    apps = Application.objects.all()
    return render(request, "dashboard.html", {"user": request.user, "apps": apps})
  else:
    return redirect('/login')

#validates login and redirects 
def login_view(request):
  if request.method == "POST":
    user = authenticate(username=request.POST['username'], password=request.POST['password'])
    if user is not None:
      login(request, user)
      return redirect('/')
  return render(request, "login.html", {})

def signup_view(request):
  if request.method == "POST":
    user = User.objects.create_user(email=request.POST['email'], username=request.POST['username'], password=request.POST['password'])
    user.first_name = request.POST['first_name']
    user.last_name = request.POST['last_name']
    user.save()
    login(request, user)
    return redirect('/')
  return render(request, "signup.html", {})

#log out and redirect to login/splash page
def logout_view(request):
  logout(request)
  return redirect("/")


def stats(request):
  if request.user.is_authenticated:
    stats_list = []
    users = User.objects.all()
    for u in users:
      term = u.username + ','
      obj = {'name': u.first_name, 'num': Application.objects.filter(graders__contains=term).count()}
      stats_list.append(obj)
    return render(request, "stats.html", {'stats_list': stats_list})

  return render(request, "stats.html", {})

def grade(request):
  if request.user.is_authenticated:
    user = request.user
    if request.method == "POST":
      graded_app = Application.objects.get(email=request.POST['email'])
      if graded_app.num_graders < 2:
        #if not already graded somehow
        graded_app.graders += user.username + ','
        graded_app.num_graders += 1
        if graded_app.rating == 0:
          graded_app.rating = int(request.POST['rating'])
        else:
          graded_app.rating = (graded_app.rating + int(request.POST['rating'])) / graded_app.num_graders
        graded_app.comments += request.POST['comments'] + " "
        graded_app.save()
        messages.success(request, 'Previous app graded!')
      else:
        messages.info(request, 'Previous app already graded >2 times, sorry your grade did not go through')
    
    # display new application
    try:
      #get app without 2 graders and user not already graded
      term = user.username + ','
      apps = Application.objects.all().exclude(num_graders=2).exclude(graders__contains=term).filter(status="N/A")
      num_left = apps.count()
      if num_left == 0:
        context = {
          "name": '',
          "email": '',
          "school": '',
          "app_text1": '',
          "app_text2": '',
          "first_hackathon": '',
          "github": '',
          "num_left": num_left,
          "user": user
        }
        return render(request, "grade.html", context)
      app = apps[random.randrange(num_left)]
      # app = apps[0]
      github_link = app.github if app.github != 'nan' else ''
      context = {
        "name": app.name,
        "email": app.email,
        "school": app.school,
        "app_text1": app.app_text1,
        "app_text2": app.app_text2,
        "first_hackathon": app.first_hackathon,
        "github": github_link,
        "num_left": num_left,
        "user": user
      }
      return render(request, "grade.html", context)
    except IndexError:
      print('none in db')
      return render(request, "grade.html", {"user": user })
  else:
     return redirect("/")
 
def manage(request):
  if request.user.is_authenticated:
    user = request.user
    if request.method == "POST":
      if 'rating' not in request.POST:
        obj = json.loads(request.body)
        for user in obj['people']:
          hacker_app = Application.objects.get(email=user['email'])
          update_status(hacker_app, obj['action'])  
      else:
        apps = Application.objects.filter(Q(num_graders=2) | ~Q(status="N/A")).filter(rating__gte=float(request.POST['rating']))
        if 'is_priority' in request.POST and request.POST['is_priority']:
          opp = not request.POST['is_priority']
          apps = apps.filter(is_CA=opp)
        num_acc = Application.objects.filter(status='Accepted').count()
        num_rej = Application.objects.filter(status='Rejected').count()
        num_wait = Application.objects.filter(status='Waitlisted').count()
        total = Application.objects.all().count()
        num_left = Application.objects.filter(status='N/A').exclude(num_graders=2).count()
        graded = Application.objects.filter(num_graders=2).count()
        return render(request, "manage.html", {"user": user, "apps": apps, "num_acc": num_acc, "num_rej": num_rej, "num_wait": num_wait, "total": total, "graded":graded, "num_left": num_left})

    # apps = Application.objects.filter(Q(num_graders=2) | ~Q(status="N/A"))
    apps = Application.objects.all()
    num_acc = Application.objects.filter(status='Accepted').count()
    num_rej = Application.objects.filter(status='Rejected').count()
    num_wait = Application.objects.filter(status='Waitlisted').count()
    total = Application.objects.all().count()
    graded = Application.objects.filter(num_graders=2).count()
    num_left = Application.objects.filter(status='N/A').exclude(num_graders=2).count()
    return render(request, "manage.html", {"user": user, "apps": apps, "num_acc": num_acc, "num_rej": num_rej, "num_wait": num_wait, "total": total, "graded":graded, "num_left": num_left})
  else:
     return redirect("/")


def update_status(hacker_app, action):
  if action == 'Reset':
    hacker_app.num_graders = 0
    hacker_app.status = 'N/A'
    hacker_app.rating = 0
    hacker_app.comments = ''
    hacker_app.graders = ''
  else:
    if action == 'Accept':
      hacker_app.status = 'Accepted'
    elif action == 'Reject':
      hacker_app.status = 'Rejected'
    elif action == 'Waitlist':
      hacker_app.status = 'Waitlisted'
    else:
      hacker_app.status = 'N/A'
  hacker_app.save()

def add_apps(request):
  if request.user.is_authenticated and request.method == 'POST' and request.FILES['myfile']:
    IS_LATE_APP = True
    df = pd.read_csv(request.FILES['myfile'].temporary_file_path(), delimiter = ',')
    df.set_axis(['Timestamp','email','name','school','Age','why1','why2','first_hackathon','CA','resume','github','timezone','workshops'], axis='columns', inplace=True)
    df.apply(lambda row: Application.objects.create(email=row['email'], name=row['name'], \
    app_text1=row['why1'], app_text2=row['why2'], github=row['github'], school=row['school'], \
    first_hackathon=row['first_hackathon'], timezone=row['timezone'], is_CA=IS_LATE_APP), axis = 1)
    return render(request, 'add_apps.html', {
        'uploaded_file_url': 'sd'
    })
  return render(request, 'add_apps.html')

def clear(request):
  Application.objects.all().delete()





def export_graded(request):
    model_class = Application
    field_names = ['name', 'email', 'school', 'timezone', 'rating', 'status', 'comments']

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="graded.csv"'    
    writer = csv.writer(response)
    writer.writerow(field_names)
    for obj in model_class.objects.filter(num_graders=2):
        row = writer.writerow([getattr(obj, field) for field in field_names])

    return response

def export_accepted(request):
    model_class = Application
    field_names = ['name', 'email', 'school', 'timezone', 'rating', 'status', 'comments']

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="accepted.csv"'    
    writer = csv.writer(response)
    writer.writerow(field_names)
    for obj in model_class.objects.filter(status='Accepted'):
        row = writer.writerow([getattr(obj, field) for field in field_names])
    return response

def export_rejected(request):
    model_class = Application
    field_names = ['name', 'email', 'school', 'rating', 'status', 'timezone', 'comments']

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="rejected.csv"'    
    writer = csv.writer(response)
    writer.writerow(field_names)
    for obj in model_class.objects.filter(status='Rejected'):
        row = writer.writerow([getattr(obj, field) for field in field_names])
    return response

def export_waitlisted(request):
    model_class = Application
    field_names = ['name', 'email', 'school', 'rating', 'status', 'timezone', 'comments']

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="waitlisted.csv"'    
    writer = csv.writer(response)
    writer.writerow(field_names)
    for obj in model_class.objects.filter(status='Waitlisted'):
        row = writer.writerow([getattr(obj, field) for field in field_names])
    return response

def export_total(request):
    model_class = Application
    field_names = ['name', 'email', 'school', 'rating', 'status', 'timezone', 'comments']

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="waitlisted.csv"'    
    writer = csv.writer(response)
    writer.writerow(field_names)
    for obj in model_class.objects.all():
        row = writer.writerow([getattr(obj, field) for field in field_names])
    return response
