from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from about.models import Application
import pandas as pd
import random


# Create your views here.

def dashboard(request):
  if request.user.is_authenticated:

    return render(request, "dashboard.html", {})
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
      print("post - submit rate")
      graded_app = Application.objects.get(email=request.POST['email'])
      if graded_app.num_graders < 2:
        #if not already graded somehow
        graded_app.graders += user.username + ','
        graded_app.num_graders += 1
        if graded_app.rating == 0:
          graded_app.rating = request.POST['rating']
        else:
          graded_app.rating = (graded_app.rating + request.POST['rating']) / graded_app.num_graders
        print(graded_app.graders)
        print(graded_app.num_graders)
        graded_app.save()
    
    # display new application
    try:
      #get app without 2 graders and user not already graded
      term = user.username + ','
      apps = Application.objects.all().exclude(num_graders=2).exclude(graders__contains=term)
      num_left = apps.count()
      app = apps[random.randrange(num_left)]
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
 

def add_apps(request):
  df = pd.read_csv("/Users/wendywu/Downloads/Projects/apps/apps/about/resp.csv", encoding='utf-8', delimiter = ',')
  df.apply(lambda row: Application.objects.create(email=row['email'], name=row['name'], \
  app_text1=row['why1'], app_text2=row['why2'], github=row['github'], school=row['school'], first_hackathon=row['first_hackathon'], timezone=['timezone']), axis = 1)
  return redirect("/grade")