from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db import transaction

from .models import Post
from boat.models import Boat

@login_required
def my_posts(request):
    posts = Post.objects.filter(boat__owner=request.user).order_by('id')
    return render(request, 'post/my_posts.html', context={'posts': posts})   

@login_required
def create(request):
    
    if request.method == 'GET':
        boats = Boat.objects.filter(owner=request.user)
        return render(request, 'post/create.html', context={'boats': boats})
    
    elif request.method == 'POST':
        data = request.POST
        
        try:         
            
            boat = Boat.objects.get(pk=data.get('boat'), owner=request.user)
            with transaction.atomic():
                fields = {
                    'text': data.get('text'),
                }
                post = Post.objects.create(**fields, boat=boat)

        except Exception as e:
            return JsonResponse({'message': str(e)}, status=400)

        return JsonResponse({
            'data': {'id': post.id},
            'redirect': '/posts/my_posts/'
        })

@login_required
def update(request, pk):
    if request.method == 'GET':
        try:                 
            post = Post.objects.get(pk=pk, boat__owner=request.user)
            boats = Boat.objects.filter(owner=request.user)
            return render(request, 'post/update.html', context={'post': post, 'boats': boats})
        except Post.DoesNotExist:
            return render(request, 'not_found.html')
    elif request.method == 'POST':       
        try: 
            data = request.POST
            post = Post.objects.get(pk=pk, boat__owner=request.user)
            boat = Boat.objects.get(pk=data.get('boat'), owner=request.user)
            with transaction.atomic():
                post.text = data.get('text')
                post.boat = boat
                post.save()        
            return JsonResponse({'redirect': '/posts/my_posts/'})
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=400)

@login_required
def delete(request, pk):
    if request.method == 'POST':
        try:
            post = Post.objects.get(pk=pk, boat__owner=request.user)
            post.delete()
            return JsonResponse({'redirect': '/posts/my_posts/'})
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=400)  
