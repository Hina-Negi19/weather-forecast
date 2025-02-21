from django.urls import path
from . import views

urlpatterns=[
    path('home/',views.home_view),
    path('index/',views.index_view),
    path('login/',views.login_view,name='login'),
    path('signup/',views.signup_view),
    path('email_verification/',views.email_varification_view,name='email_verification'),
    path('otp_verification/',views.otp_verify_view,name='otp_verify'),
    path('weather/',views.weather_view,name='weather'),
    path('forecast/<int:index>',views.forecast_view,name='forecast'),
    path('logout/',views.logout_view)
]