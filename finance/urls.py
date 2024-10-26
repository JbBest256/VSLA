from django.urls import path
from . import views
from .views import request_loan_step1, request_loan_step2, request_loan_step3
urlpatterns = [
    path('financial-year/create/', views.create_financial_year, name='create_financial_year'),
    path('accounts/<slug:slug>/', views.view_account, name='view_account'),
    path('transaction/create/<slug:slug>/', views.process_transaction, name='create_transaction'),
    path('newaccount',views.create_account_settings,name ='newaccount'),
    path('financial_year_list',views.financial_year_list,name ='financial_year_list'),
    
    path('delete_transaction/<slug:slug>/', views.view_account, name='delete_transaction'),

    path('edit_transaction/<slug:slug>/', views.view_account, name='edit_transaction'),
    
    
    path('loanrequests/<slug:slug>/', views.list_loan_requests, name='loanrequests'),    
    path('loan/request/<slug:slug>/', request_loan_step1, name='request_loan_step1'),
    path('loan/request/<int:loan_request_id>/guarantors/', request_loan_step2, name='request_loan_step2'),
    path('loan/request/<int:loan_request_id>/approval/', request_loan_step3, name='request_loan_step3'),
    
    
    
    
    path('edit_loan_request/<slug:slug>/', views.view_account, name='edit_loan_request'),
    path('delete_loan_request/<slug:slug>/', views.view_account, name='delete_loan_request'),
    
    
    path('guarantor/accept/<int:guarantor_id>/', views.accept_guarantor_request, name='accept_guarantor_request'),
    path('guarantor/reject/<int:guarantor_id>/', views.reject_guarantor_request, name='reject_guarantor_request'),
    path('guarantor/requests/', views.guarantor_requests_view, name='guarantor_requests_view'),
    
    path('loan/approve/<int:loan_request_id>/', views.approve_loan_request, name='approve_loan_request'),
]




