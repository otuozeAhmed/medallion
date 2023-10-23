import smtplib
from email.mime.text import MIMEText

from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth import authenticate, login
from django.contrib import messages

from .models import CustomUser
from .forms import CustomUserCreationForm
from .utils import generate_otp


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Send OTP to the user's email
            # otp = generate_otp()
            # send_otp_email(user.email, otp)
            
            # user.otp = otp  # Save the OTP in the user's profile
            user.save()

            return redirect('login')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/signup.html', {'form': form})

def send_otp_email(email, otp):
    s = smtplib.SMTP('webmail.nlng.com', 25)
    msg = MIMEText("""Dear Recipient,\n\n
Kindly use the OTP below to completed your verification\n """ + otp)
    sender = 'ahmedrufai.otuoze@nlng.com'
    recipients = [email]
    msg['Subject'] = "OTP Verification"
    msg['From'] = sender
    msg['To'] = ", ".join(recipients)
    s.sendmail(sender, recipients, msg.as_string())
    print('*********************************************')
    print(otp)
    print('*********************************************')

@login_required
def otp_verification(request):
    if request.method == 'POST':
        otp_entered = request.POST.get('otp')
        user = request.user  # Assuming the user is already logged in

        if otp_entered == user.otp:  # Check if the entered OTP matches the stored OTP
            user.otp = ''  # Clear the OTP in the user's profile
            user.is_verified = True  # Mark the user as verified (customize your user model accordingly)
            user.save()
            login(request, user)  # Log in the user

            messages.success(request, 'OTP verification successful. You are now logged in.')
            return redirect('djf_surveys:index')
        else:
            messages.error(request, 'OTP verification failed. Please try again.')

    return render(request, 'registration/otp_verification.html')




from django.http import JsonResponse

@login_required
def resend_otp_view(request):
    if request.method == 'POST':
        new_otp = generate_otp()  # Use your OTP generation function
        request.user.otp = new_otp
        request.user.save()
        # Send OTP to the user's email
        send_otp_email(request.user.email, new_otp)
        messages.success(request, 'OTP resent successfully!')
        return HttpResponse({'message': 'OTP resent successfully'})





@login_required
def logout_view(request):
    logout(request)
    return redirect('djf_surveys:home')  


def view_terms_of_service(request):
    return render(request, 'registration/terms_of_service.html')




def custom_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to a success page
            return redirect('djf_surveys:home')
        else:
            messages.error(request, 'Invalid login credentials. Please try again.')

    return render(request, 'registration/login.html')