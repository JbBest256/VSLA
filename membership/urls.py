from django.urls import path
from . import views


urlpatterns = [

    
    path('members',views.MembersView,name ='members'),
    path('addmember',views.AddMemberView,name ='addmember'),
    path('confirmremovemember',views.ConfirmRemoveMemberView,name ='confirmremovemember'),
    
    path('leaders',views.LeadersView,name ='leaders'),
    path('assignstaff/<int:pk>',views.AssignStaff,name ='assignstaff'),
    path('removestaff/<int:pk>',views.ConfirmRemoveMemberView,name ='removestaff'),
 
]