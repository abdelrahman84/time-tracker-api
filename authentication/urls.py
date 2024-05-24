from django.urls import re_path as url

from authentication.views import MyTokenObtainPairView
from authentication import views

app_name = 'authentication'

urlpatterns = [
    url(r'^api/users$', views.user_list),
    url(r'^api/login', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    url(r'^api/verify_token', views.verify_token),
    url(r'^api/check_email_before_login', views.check_email_before_login),
    url(r'^api/resend_verification_email', views.resend_verification_email),
    url(r'^api/forgot_password', views.forgot_password),
    url(r'^api/reset_password', views.reset_password),
]
