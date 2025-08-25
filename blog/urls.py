# blog/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.blog_list, name='blog_list'),
    path('post/create/', views.create_blog_post, name='create_blog_post'),
    path('post/<int:pk>/', views.blog_detail, name='blog_detail'),
    path('post/<int:pk>/like/', views.like_post, name='like_post'),
]