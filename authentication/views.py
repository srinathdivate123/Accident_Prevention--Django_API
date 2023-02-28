from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth.models import User
from django.contrib import messages
from validate_email import validate_email
import json
import pdb
from django.core.mail import EmailMessage
from django.core.mail import EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from .utils import token_generator
from django.urls import reverse
from django.contrib import auth
import threading
from django.contrib.auth.tokens import PasswordResetTokenGenerator

@api_view(['PUT'])
def getUserDataView(request):
    content = request.data['_content']
    content.replace('\r\n', '')
    content = json.loads(content)
    name = content['name']
    email = content['email']
    password = content['password']
    print(name)
    print(email)
    print(password)
    return Response({"success":True})

class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)
    def run(self):
        self.email.send(fail_silently=False)



@api_view(['PUT'])
def EmailValidationView(request):
    email = request.data['email']
    if not validate_email(email):
        return Response({'email_response': 'Email is invalid!'})
    if User.objects.filter(email=email).exists():
        return Response({'email_response': 'Sorry this email is in use, choose another one!'})
    return Response({'email_response': True})


@api_view(['PUT'])
def UsernameValidationView(request):
    username = request.data['username']
    if not str(username).isalnum():
        return Response({'username_response': 'Username should only contain alphanumeric characters!'})
    exists = User.objects.filter(username=username).exists()
    if exists:
        return Response({'username_response': 'Sorry! This username is in use, choose another one! '})
    return Response({'username_response': True})

@api_view(['PUT'])
def RegistrationView(request):
    try:
        username = request.data['username']
    except Exception as e:
        return Response({'reg_response':'Please enter username!'})
    try:
        email = request.data['email']
    except Exception as a:
        return Response({'reg_response':'Please enter email!'})
    try:
        password = request.data['password']
    except Exception as a:
        return Response({'reg_response':'Please enter password!'})
    if not User.objects.filter(username=username).exists():
        if not User.objects.filter(email=email).exists():
            if len(password) < 6:
                return Response({'reg_response':'Enter a password greater than 6 characters!'})
            user = User.objects.create_user(username=username, email=email)
            user.set_password(password) 
            user.is_active = False
            user.save()
            current_site = get_current_site(request)
            email_body = {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': token_generator.make_token(user),
            }
            link = reverse('activate', kwargs={
                        'uidb64': email_body['uid'], 'token': email_body['token']})
            email_subject = 'Activate your account'
            activate_url = 'http://'+current_site.domain+link
            email = EmailMessage(
                email_subject,
                'Hi '+user.username + ', we\'re glad that you registered your account with us! Please click the below link to activate your account. Hope you have a wonderful experence with us! \n'+activate_url,
                'noreply@semycolon.com',
                [email],
            )
            EmailThread(email).start()
            return Response({'reg_response':'Account Successfully Created'})
        return Response({'reg_response':'This email is in use. Choose another one!'})
    return Response({'reg_response':'This username is in use. Choose another one!'})


def VerificationView(request,uidb64, token):
    try:
        id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=id)
        if not token_generator.check_token(user, token):
            messages.error(request, 'Wrong activation link!')
            return redirect('login')
        if user.is_active:
            messages.error(request, 'This user is already activated! You may proceed to login now!')
            return redirect('login')
        user.is_active = True
        user.save()
        messages.success(request, 'Your account was activated successfully! You can securely login now!')
        return redirect('login')
    except Exception as ex:
        messages.error(request, 'There was some error in the link that you clicked! Please register yourself again!')
        return redirect('login')

@api_view(['PUT'])
def LoginView(request):
    try:
        email = request.data['email']
    except Exception as e:
        return Response({'login_response':'Please enter email!'})
    try:
        password = request.data['password']
    except Exception as a:
        return Response({'login_response':'Please enter password!'})
    try:
        user_name = User.objects.get(email=email).username
    except Exception as a:
        return Response({'login_response':'Wrong credentials!'})
    user = auth.authenticate(username = user_name,password=password)
    if user:
        if user.is_active:
            auth.login(request, user)
            return Response({'login_response':True, 'username':user_name})
        else:
            return Response({'login_response':'Account not activated yet. Please activate your account!'})
    else:
        return Response({'login_response':'Either your credentials are wrong or you haven\'t activated your account!'})


@api_view(['GET'])
def LogoutView(request):
    auth.logout(request)
    return Response({'logout_response':'Logged out successfully'})

@api_view(['PUT'])
def RequestPasswordResetEmail(request):
    try:
        email = request.data['email']
    except Exception as e:
        return Response({'reset_response':'Please enter email!'})
    if not validate_email(email):
        return Response({'reset_response': 'Please enter a valid email.'})
    else:
        if not User.objects.filter(email=email).exists(): 
            return Response({'reset_response': 'This email is not registered with us. Please register yourself first.'})

    current_site = get_current_site(request)
    user = User.objects.filter(email=email)
    if user.exists():
        email_contents = {
                'user': user[0],
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user[0])),
                'token': PasswordResetTokenGenerator().make_token(user[0]),}
        link = reverse('reset-user-password', kwargs={
                           'uidb64': email_contents['uid'], 'token': email_contents['token']})
        email_subject = 'Reset your password'
        reset_url = 'http://'+current_site.domain+link
        email = EmailMessage(
                email_subject,
                'Hi there!, Please click the link below to set a new password for your account \n'+ reset_url,
                'noreply@semycolon.com',
                [email],)
        EmailThread(email).start()
        return Response({'reset_response':'We have sent you an email with the link to reset your password'})

@api_view(['PUT'])
def CompletePasswordReset(request,uidb64, token):
    if request.method=="GET":
        context = {'uidb64':uidb64,'token':token}
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(username=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                messages.info(request, 'Password link is invalid or has been used earlier, please request a new one.')
                return render(request, 'auth/resetpassword.html')
        except Exception as a: 
            messages.info(request, 'Something went wrong, try again.')   
        return render( request, 'auth/setnewpass.html', context)
    if request.method=="POST":
        context = {'uidb64':uidb64,'token':token}
        password = request.POST['password']
        password2 = request.POST['password2']
        if password != password2:
            messages.error(request, 'Passwords do not match. Re-enter both again.')
            return render( request, 'auth/setnewpass.html', context)
        if len(password)<6:
            messages.error(request, 'Enter a password greater than 6 characters.')
            return render( request, 'auth/setnewpass.html', context)
        try:
            id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(username=id)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password reset successful. You can login with the new password.')
            return redirect('login')
        except Exception as ex:
            messages.info(request, 'Something went wrong, try again.')
            return render( request, 'auth/setnewpass.html', context)