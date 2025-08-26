# blog/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from .models import BlogPost, Like, Subscriber
from django.http import JsonResponse
from django.contrib import messages
from notifications.models import Notification

def blog_list(request):
    posts = BlogPost.objects.all().order_by('-created_at')
    posts = [post  for post in posts]
    return render(request, 'blog/blog_list.html', {'posts': posts})

def blog_detail(request, pk):
    post = get_object_or_404(BlogPost, pk=pk)
    return render(request, 'blog/blog_detail.html', {'post': post})

@login_required
def create_blog_post(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        if title and content:
            BlogPost.objects.create(author=request.user, title=title, content=content)
            messages.success(request, 'Your blog post has been created successfully!')
            return redirect('blog_list')
    return render(request, 'blog/create_blog_post.html')

@login_required
def like_post(request, pk):
    if request.method == 'POST':
        post = get_object_or_404(BlogPost, pk=pk)
        try:
            Like.objects.create(user=request.user, blog_post=post)
            # This is where the author notification will be triggered
            return JsonResponse({'success': True})
        except IntegrityError:
            return JsonResponse({'success': False, 'message': 'You have already liked this post.'})
    return JsonResponse({'success': False, 'message': 'Invalid request.'})