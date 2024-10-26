from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_association, name='create_association'),
    path('association', views.active_association, name='association_detail'),
    path('dashboard', views.association_dashboard, name='dashboard'),
    
    
    path('<int:pk>/update/', views.update_association, name='update_association'),
    path('<int:pk>/delete/', views.delete_association, name='delete_association'),
    
    path('association_list/', views.association_list, name='association_list'),
    
    
    path('roles',views.AllRolesView,name ='roles'),
    path('role/<int:pk>',views.SingleRole,name ='role'),
    path('editrole/<int:pk>',views.AllRolesView,name ='editrole'),
    path('newrole',views.AddRolesView,name ='newrole'),
]
