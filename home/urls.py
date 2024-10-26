from django.urls import path
from . import views


urlpatterns = [
   
    
    path('',views.Home,name ='home'),
    
    path('login',views.UserLogin,name ='login'),
    path('logout',views.UserLogout,name ='logout'),
    path('register',views.UserRegister,name ='register'),
    path('myprofile',views.UserProfile,name ='myprofile'),
    path('editprofile',views.EditUserProfile,name ='editprofile'),
    
    path('notifications',views.notifications_view,name ='notifications'),
]