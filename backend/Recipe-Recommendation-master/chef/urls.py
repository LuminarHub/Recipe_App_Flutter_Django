from django.urls import path
from chef import views

app_name = "chef"

urlpatterns = [

    path('register/', views.UserRegisterationAPIView.as_view(), name="create-user"),
    path('login/', views.UserLoginAPIView.as_view(), name="login-user"),


]
