from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import JSONParser
from django.template.loader import get_template, render_to_string
from django.core import mail
from django.http.response import JsonResponse
from rest_framework import status

from authentication.serializers import UserSerializer


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
