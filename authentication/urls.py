from django.conf.urls import url

from authentication import views

app_name = 'authentication'

urlpatterns = [
    url(r'^api/users$', views.user_list),
]
