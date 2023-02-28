from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from . import views as a
urlpatterns = [
    path('registration', a.RegistrationView, name = 'reg'),
    path('login', a.LoginView, name = 'login'),
    path('logout', a.LogoutView, name = 'logout'),
    path('validate-username', csrf_exempt( a.UsernameValidationView), name='validate-username'),
    path('validate-email', csrf_exempt(a.EmailValidationView), name='validate-email'),
    path('activate/<uidb64>/<token>', a.VerificationView, name='activate'),
    path('request-reset-link', a.RequestPasswordResetEmail, name='reset'),
    path('set-new-password/<uidb64>/<token>', a.CompletePasswordReset, name='reset-user-password'),
    path('getuserdata', a.getUserDataView, name='getuserdata')
]
