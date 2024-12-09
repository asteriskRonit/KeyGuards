from django.shortcuts import render
from django.urls import path
from . import views

urlpatterns = [
    path('send-otp/', views.request_otp_view, name='request_otp'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('api/create-user/', views.create_user, name='create_user_form'),
    path('register_face/', views.register_face, name='register_face'),
    path('api-register-fetch/', views.RegisterFaceListView.as_view(), name='register-faces'),
    path('register-face-by-email/', views.RegisterFaceByEmailView.as_view(), name='register-face-by-email'),
    path('update-register-face/', views.UpdateRegisterFaceView.as_view(), name='update-register-face'),
    path('api/create-department/', views.create_department, name='create_department'),
    path('authenticate-face/', views.authenticate_face, name='authenticate-face'),
    path('', views.default_view, name='hello'),
]