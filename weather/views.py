from django.shortcuts import render,redirect
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse
import requests
import random
from django.contrib.auth.hashers import make_password,check_password
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import UserInfo
import datetime
from smtplib import SMTPRecipientsRefused


#home view
def home_view(request):
    return render(request,'weather/home.html')

def index_view(request):
    return render(request,'weather/index.html')


# login view 

def login_view(request):
    if request.method=='POST':
        email=request.POST.get('email')
        password=request.POST.get('password')
        try:
            user=UserInfo.objects.get(email=email)
            if user:
                if user.is_authenticated(email,password):
                        request.session['user_id']=user.id
                        return redirect('/weather')               
        except:    
            error_msg='wrong password or email'
            return render(request,'weather/login.html',{'error_msg':error_msg})
    error_msg=request.GET.get('error_msg',None)    
    return render(request,'weather/login.html',{'error_msg':error_msg})

def signup_view(request):
    return render(request,'weather/signup.html')

def email_varification_view(request):
    if request.method=='POST':
        email=request.POST.get('email')
        if UserInfo.objects.filter(email=email):
             error_msg={'error_msg':'this email already exists'}
             return render(request,'weather/signup.html',error_msg)
        subject='email verfication'
        code=''.join([str(random.randint(0,9)) for _ in range(4)])
        otp=code
        from_email=settings.EMAIL_HOST_USER
       
        set_password=request.POST.get('password')
        name=request.POST.get('name')
        print(email)
        recipient=[email]
        try:
            send_mail(subject,otp,from_email,recipient) 
            success_msg=f'otp sent succesfully at {email} please enter opt'
            return render(request,'weather/verify_otp.html',{'success_msg':success_msg,'otp':otp,'email':email,'password':set_password,'name':name})
        except SMTPRecipientsRefused:
               error_msg={'error_msg':'wrong email plz enter a valid email'}
               return render(request,'weather/signup.html',error_msg)
        except Exception as e:
            error_msg={'error_msg':'wrong email plz enter a valid email'}
            return render(request,'weather/signup.html',error_msg)
    else:
        return render(request,'weather/signup.html')    
    
def otp_verify_view(request):
      if request.method=='POST':
          otp=request.POST.get('otp')
          sent_code=request.POST.get('msg')
         
          if otp==sent_code:
              success_msg={'verify_msg':'accoutn verification successfull plz login'}
              email=request.POST.get('email')
              password=request.POST.get('password')
              name=request.POST.get('name')
              password=make_password(password)
              user=UserInfo.objects.create(name=name,email=email,password=password)
              user.save()
              return render(request,'weather/login.html',success_msg)
          else:
               msg={'verify_msg':'wrong otp'}
               return render(request,'weather/signup.html')  
      else:
          return render(request,'weather/verify_otp.html')   
      
    
def forecast_view(request,index):
        if 'user_id' in request.session:
            key='f095c27d00b647ce93c90328240810'
            location= request.session.get('location','delhi')
            weekdays=request.session.get('weekdays')
            weekdays.insert(0,"Today")
            weekdays.insert(1,"Tomorrow")
            
            try:
                country=request.session.get('region')
                Base_URL=f"https://restcountries.com/v3.1/name/{country}"
                flag_request=requests.get(Base_URL)
                flag_response=flag_request.json()[0]['flags']['png']

            except:
                flag_response=None   
            Base_URL= f"http://api.weatherapi.com/v1//forecast.json?key={key}&q={location}&days=4" 
            print(Base_URL)
            try:
                    response=requests.post(Base_URL)
                    data = response.json()
                    forecast = data.get('forecast').get('forecastday')
                    astro= data.get('forecast').get('forecastday')[0]['astro']
                    sunset=astro['sunset']
                    sunrise=astro['sunrise']
                    moonset=astro['moonset']
                    moonrise=astro['moonrise']
                    day_data=forecast[index]
                    date=day_data['date']
                    max_temp=day_data['day']['maxtemp_c']
                    min_temp=day_data['day']['mintemp_c']
                    avg_temp=day_data['day']['avgtemp_c']
                    max_wind=day_data['day']['maxwind_kph']
                    my_dict={'time':[],'temp':[],'precip':[],'cloud':[],'humidity':[],'feels_like':[],'wind_mph':[],'pressure':[],'gust':[],'wind_dir':[],'icon':[],'date':date}
                    for x in range(0,24,3): 
                        hour_data=day_data['hour'][x]
                        datetime_obj=datetime.datetime.strptime(hour_data['time'], '%Y-%m-%d %H:%M')
                        time=datetime_obj.strftime('%H:%M')
                        temp=hour_data['temp_c']
                        precip=hour_data['precip_in']
                        cloud=hour_data['cloud']
                        humidity=hour_data['humidity']
                        feels_like=hour_data['feelslike_c']
                        wind_mph=hour_data['wind_mph']
                        pressure=hour_data['pressure_in']
                        gust=hour_data['gust_mph']
                        wind_dir=hour_data['wind_dir']
                        icon=day_data['hour'][x]['condition']['icon']
                        my_dict['time'].append(time)
                        my_dict['temp'].append(temp)
                        my_dict['precip'].append(precip)
                        my_dict['cloud'].append(cloud)
                        my_dict['humidity'].append(humidity)
                        my_dict['feels_like'].append(feels_like)
                        my_dict['wind_mph'].append(wind_mph)
                        my_dict['pressure'].append(pressure)
                        my_dict['gust'].append(gust)
                        my_dict['wind_dir'].append(wind_dir)
                        my_dict['icon'].append(icon)
                    weather_data={
                        'date':date,
                        'max_temp':max_temp,
                        'avg_temp':avg_temp,
                        'max_wind':max_wind,
                        'min_temp':min_temp,
                        'sunset':sunset,
                        'sunrise':sunrise,
                        'moonrise':moonrise,
                        'moonset':moonset,
                        'flag':flag_response,
                        'weather_detail':my_dict
                    }
                    day=weekdays[index]
                    return render(request,'weather/forecast.html',{'weather_data':weather_data,'weekdays':weekdays,'location':location,'day':day})
            except:
                  return render(request,'weather/forecast.html')
        else:    
           return redirect('/login')


def weather_view(request):
    if 'user_id' in request.session:
        today=datetime.date.today()
        weekdays=[]
        for x in range(11):
            date=today+datetime.timedelta(x)
            weekday_name=date.strftime('%A')
            weekdays.append(weekday_name)
        key='f095c27d00b647ce93c90328240810'
        location=request.POST.get('name','delhi india')
        Base_URL= f"http://api.weatherapi.com/v1//current.json?key={key}&q={location}"
        print(Base_URL)
        try:
            response=requests.get(Base_URL)
            weather_data=response.json()
            data={
                    'city':weather_data.get('location')['name'],
                    'region':weather_data.get('location')['country'],
                    'time':weather_data.get('location')['localtime'],
                    'temp':weather_data.get('current')['temp_c'],
                    'text':weather_data.get('current')['condition']['text'],
                    'wind_mph':weather_data.get('current')['wind_mph'],
                    'pressure_in':weather_data.get('current')['pressure_in'],
                    'humidity':weather_data.get('current')['humidity'],
                    'feelslike':weather_data.get('current')['feelslike_c']
            }
            request.session['location']=location
            request.session['weekdays']=weekdays[2:]
            request.session['region']=data['region']
            return render(request,'weather/weather.html',{'weather_data':data,'weekday_name':weekdays[2:]})
        except:
            return HttpResponse('data not found')
    else:
         error_msg="you are not logged in"
         return redirect(f"/login?/error_msg={error_msg}") 
     
def logout_view(request):
   
    request.session.pop('user_id',None)
    return redirect('/index')
            
        