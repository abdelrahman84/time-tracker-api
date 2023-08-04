from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser
from django.template.loader import get_template, render_to_string
from django.core import mail
from django.http.response import JsonResponse
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth.hashers import make_password

from authentication.models import User
from authentication.serializers import UserSerializer, MyTokenObtainPairSerializer, VerifyTokenSerializer, CheckEmailBeforeLoginSerializer


@api_view(['POST', 'DELETE'])
@permission_classes([AllowAny])
def user_list(request):

    if request.method == 'POST':
        user_data = JSONParser().parse(request)
        user_serializer = UserSerializer(data=user_data)

        if user_serializer.is_valid():
            user_serializer.save()

            verify_email_template = get_template('verification_email.html').render(
                {'name': user_serializer.data['name'], 'verify_token': user_serializer.data['verify_token']})

            subject = 'Email verification'
            plain_message = render_to_string('verification_email.html', {
                'name': user_serializer.data['name'], 'verify_token': user_serializer.data['verify_token']
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

            user.password = make_password(user_data['password'])
            user.email_verified = True
            user.save()

        except User.DoesNotExist:
            return JsonResponse({'error': 'user doesn`t exist'}, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse(user_serializer.data, status=status.HTTP_400_BAD_REQUEST)

    return JsonResponse(token_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def check_email_before_login(request):

    user_data = JSONParser().parse(request)
    check_email_serializer = CheckEmailBeforeLoginSerializer(data=user_data)

    if check_email_serializer.is_valid():
        try:
            user = User.objects.get(email=check_email_serializer.data['email'])
            if user.email_verified == False:
                return JsonResponse({'status': 2}, status=status.HTTP_200_OK)
            return JsonResponse({'status': 3}, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return JsonResponse({'status': 1}, safe=False, status=status.HTTP_200_OK)
    return JsonResponse(check_email_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
