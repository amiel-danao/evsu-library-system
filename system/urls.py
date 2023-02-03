from django.urls import path, re_path
from system.forms import LoginForm
from system import views
from django.contrib.auth import views as auth_views

app_name = 'system'

urlpatterns = [
    path('', views.index, name='index'),
    path('qr/<str:pk>/', views.show_qr, name="show-qr"),
    path('login/',
         auth_views.LoginView.as_view(authentication_form=LoginForm, redirect_authenticated_user=True), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('accounts/verify/<str:id>/', views.verify_account_view, name='create'),
    path('accounts/send_verification/', views.send_verification, name='send_verification'),
    path('student_profile/<int:pk>/', views.StudentProfileUpdateView.as_view(), name='student_profile'),
    path('student/books/', views.BookListView.as_view(), name='books'),
    path('outgoingtransaction/create/', views.create_outgoing, name='outgoing_create'),
    path('incomingtransaction/create/', views.create_incoming, name='incoming_create'),
    path('admin/sms/', views.sms_view, name='sms'),
    re_path(
        r'^student-autocomplete/$',
        views.StudentAutocomplete.as_view(),
        name='student-autocomplete',
    ),
    path('admin/send_sms/', views.send_sms, name='send_sms'),
    path('admin/mark_as_paid/<int:id>/', views.mark_as_paid, name='mark_as_paid'),
    path('admin/mark_as_returned/<int:id>/', views.mark_as_returned, name='mark_as_returned'),
    path('admin/transaction_history/', views.TransactionHistoryListView.as_view(), name='transaction_history'),
    path('student/transaction_history/', views.StudentTransactionHistoryListView.as_view(), name='transaction_history_student'),
    path('admin/send_penalty_notification/', views.send_penalty_notification, name='send_penalty_notification')
]
