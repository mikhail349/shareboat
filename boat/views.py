from django.shortcuts import redirect, render
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from PIL import UnidentifiedImageError

from file.exceptions import FileSizeException
from shareboat.exceptions import ApiException

from .exceptions import BoatFileCountException
from .models import Boat, BoatFile
from .serializers import BoatSerializer, BoatFileSerializer


def response_not_found():
    return JsonResponse({'message': 'Лодка не найдена'}, status=status.HTTP_400_BAD_REQUEST)

def response_invalid_file_type():
    return JsonResponse({'message': 'Можно приложить только фотографии'}, status=status.HTTP_400_BAD_REQUEST)

def response_files_limit_count(msg):
    return JsonResponse({'message': msg}, status=status.HTTP_400_BAD_REQUEST)

def response_file_limit_size(msg):
    return JsonResponse({'message': msg}, status=status.HTTP_400_BAD_REQUEST)

FILES_LIMIT_COUNT = 10

@login_required
def get(request):
    boats = Boat.objects.filter(owner=request.user).order_by('id')
    return render(request, 'boat/list.html', context={'boats': boats})    

@login_required
def create(request):
    if request.method == 'GET':
        return render(request, 'boat/create.html')

    elif request.method == 'POST':
        data = request.POST
        files = request.FILES.getlist('file')
        
        try:
            if len(files) > FILES_LIMIT_COUNT:
                raise BoatFileCountException()
            
            with transaction.atomic():
                fields = {
                    'name':     data.get('name'),
                    'length':   data.get('length'),
                    'width':    data.get('width'),
                    'draft':    data.get('draft'),
                }
                boat = Boat.objects.create(**fields, owner=request.user)

                for file in files:
                    BoatFile.objects.create(boat=boat, file=file)
        except UnidentifiedImageError:
            return response_invalid_file_type()
        except BoatFileCountException as e:
            return response_files_limit_count(str(e))
        except FileSizeException as e:
            return response_file_limit_size(str(e))
        except Exception as e:
            return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return JsonResponse({
            'data': {'id': boat.id},
            'redirect': '/boats/'
        })


@login_required
def update(request, pk):
    try:
        boat = Boat.objects.get(pk=pk, owner=request.user)
        
        if request.method == 'GET':
            return render(request, 'boat/update.html', context={'boat': BoatSerializer(boat).data})
        elif request.method == 'POST':
            data = request.POST
            files = request.FILES.getlist('file')
            
            try:
                if len(files) > FILES_LIMIT_COUNT:
                    raise BoatFileCountException()

                with transaction.atomic():
                    boat.name   = data.get('name')
                    boat.length = data.get('length')
                    boat.width  = data.get('width')
                    boat.draft  = data.get('draft')
                    boat.save()

                    BoatFile.objects.filter(boat=boat).exclude(file__in=files).delete()

                    for file in files:
                        BoatFile.objects.get_or_create(boat=boat, file=file)

            except UnidentifiedImageError:
                return response_invalid_file_type()
            except BoatFileCountException as e:
                return response_files_limit_count(str(e))
            except FileSizeException as e:
                return response_file_limit_size(str(e))
            except Exception as e:
                return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

            return JsonResponse({'redirect': '/boats/'})
    
    except Boat.DoesNotExist:
        if request.method == 'GET':
            return render(request, 'not_found.html')
        elif request.method == 'POST':
            return response_not_found()


@login_required
@api_view(['POST'])
def delete(request, pk):
    try:
        boat = Boat.objects.get(pk=pk, owner=request.user)
        boat.delete()
    except Boat.DoesNotExist:
        return response_not_found()
    except Exception as e:
        return JsonResponse({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)    

    #if boat.posts.exists():
    #    return JsonResponse({'message': 'По данному активу уже созданы объявления'}, status=status.HTTP_400_BAD_REQUEST)    
    
    return JsonResponse({})

@login_required
def get_files(request, pk):
    files = BoatFile.objects.filter(boat__pk=pk, boat__owner=request.user)
    serializer = BoatFileSerializer(files, many=True, context={'request': request})
    return JsonResponse({'data': serializer.data})