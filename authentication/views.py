from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser
from django.template.loader import get_template, render_to_string
from django.core import mail
from django.http.response import JsonResponse
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import authenticate, login
from django.utils.crypto import get_random_string
import os.path

from authentication.models import User
from authentication.serializers import UserSerializer, MyTokenObtainPairSerializer, VerifyTokenSerializer, CheckEmailSerializer


@api_view(['POST', 'DELETE'])
@permission_classes([AllowAny])
def user_list(request):

    if request.method == 'POST':
        user_data = JSONParser().parse(request)
        user_serializer = UserSerializer(data=user_data)

        if user_serializer.is_valid():
            user_serializer.save()

            subject = 'Email verification'
            user = User.objects.get(email=user_serializer.data['email'])

            verify_email_template = get_template('verification_email.html').render(
                {'name': user_serializer.data['name'], 'verify_token': user.verify_token})

            client_side_host = os.getenv("CLIENT_SIDE_HOST")
            plain_message = render_to_string('verification_email.html', {
                'name': user_serializer.data['name'], 'verify_token': user.verify_token, 'client_side_host': client_side_host
            })

            from_email = 'info@timeTracker.com'
            to = user_serializer.data['email']

            mail.send_mail(
                subject,
                plain_message,
                from_email,
                [to],
                html_message=verify_email_template,
                fail_silently=False
            )

            new_user = authenticate(
                email=user_data['email'], password=user_data['password'])
            login(request, new_user)
            return JsonResponse(user_serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def verify_token(request):
    user_data = JSONParser().parse(request)
    token_serializer = VerifyTokenSerializer(data=user_data)

    if token_serializer.is_valid():
        try:
            user = User.objects.get(verify_token=user_data['verify_token'])
            user_serializer = UserSerializer(user)

            user.email_verified = True
            user.verify_token = ''
            user.save()

        except User.DoesNotExist:
            return JsonResponse({'error': 'user doesn`t exist'}, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse(user_serializer.data, status=status.HTTP_200_OK)

    return JsonResponse(token_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def check_email_before_login(request):

    user_data = JSONParser().parse(request)
    check_email_serializer = CheckEmailSerializer(data=user_data)

    if check_email_serializer.is_valid():
        try:
            user = User.objects.get(email=check_email_serializer.data['email'])
            if user.email_verified == False:
                return JsonResponse({'status': 2}, status=status.HTTP_200_OK)
            return JsonResponse({'status': 3}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return JsonResponse({'status': 1}, safe=False, status=status.HTTP_200_OK)
    return JsonResponse(check_email_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def resend_verification_email(request):

    user_data = JSONParser().parse(request)
    check_email_serializer = CheckEmailSerializer(data=user_data)

    if check_email_serializer.is_valid():
        try:
            user = User.objects.get(email=check_email_serializer.data['email'])
            if user.email_verified == True:
                return JsonResponse({'status': 1}, status=status.HTTP_200_OK)

            verify_email_template = get_template('verification_email.html').render(
                {'name': user.name, 'verify_token': user.verify_token})

            subject = 'Email verification'

            client_side_host = os.getenv("CLIENT_SIDE_HOST")
            plain_message = render_to_string('verification_email.html', {
                'name': user.email, 'verify_token': user.verify_token, 'client_side_host': client_side_host
            })

            from_email = os.getenv("FROM_EMAIL_ADDRESS")
            to = user.email

            mail.send_mail(
                subject,
                plain_message,
                from_email,
                [to],
                html_message=verify_email_template,
                fail_silently=False
            )

            return JsonResponse({'status': 2}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return JsonResponse({'status': 3}, safe=False, status=status.HTTP_200_OK)
    return JsonResponse(check_email_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password(request):
    
    user_data = JSONParser().parse(request)
    check_email_serializer = CheckEmailSerializer(data=user_data)
    
    if check_email_serializer.is_valid():
        try: 
            user = User.objects.get(email=check_email_serializer.data['email'])
            
            if user.verify_token == '':
                user.verify_token = get_random_string(length=32)
                user.save()
            
            forgot_password_template = get_template('forgot_password_email.html').render(
                {'name': user.name, 'reset_token': user.verify_token})
            
            subject = 'Forgot Password'
            to = user.email
            
            client_side_host = os.getenv("CLIENT_SIDE_HOST")
            plain_message = render_to_string('forgot_password_email.html', {
                'name': user.name, 'reset_token': user.verify_token, 'client_side_host': client_side_host
            })
            
            from_email = os.getenv("FROM_EMAIL_ADDRESS")
            to = user.email
            
            mail.send_mail(
                subject,
                plain_message,
                from_email,
                [to],
                html_message=forgot_password_template,
                fail_silently=False
            )
            
            return JsonResponse({'status': 1}, status=status.HTTP_200_OK)
    
        except User.DoesNotExist:
            return JsonResponse({'status':2}, safe=False, status=status.HTTP_200_OK)
    return JsonResponse(check_email_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
