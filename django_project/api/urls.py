from django.urls import path

from .views import *

urlpatterns = [
    path('list_users/', ListUsers.as_view(), name='list_users'),
    path('get_or_edit_user/<str:username>/', GetOrEditUser.as_view(), name='get_or_edit_user'),
    path('create_new_loan/', CreateNewLoan.as_view(), name='create_new_loan'),
    path('edit_loan/<int:id>/', EditLoan.as_view(), name='edit_loan'),
    path('approve_loan/', ApproveLoan.as_view(), name='approve_loan'),
    path('list_loans/', ListLoans.as_view(), name='list_loans'),
]
