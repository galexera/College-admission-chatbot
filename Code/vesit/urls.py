from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.vesitShow,name="VesitPage"),
    path('MessageSends',views.MessageSends,name='Message_Sends'),
    path('VesitChatbot',views.VesitChatbot,name='VesitChatbot')
]