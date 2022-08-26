from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.db.models import Q, Prefetch
from django.urls import reverse

from .models import MessageBoat, MessageBooking, MessageSupport
from .serializers import MessageSerializerList
from user.models import User

from boat.models import Boat
from booking.models import Booking

import json

@permission_required('user.support_chat', raise_exception=True)
def support(request):
    messages = []

    for user in User.objects.filter(is_active=True).prefetch_related('messages_as_sender__messagesupport'):
        last_message = user.messages_as_sender.filter(messagesupport__isnull=False).union(user.messages_as_recipient.filter(messagesupport__isnull=False)).last()
        if last_message:
            last_message.get_href = reverse('chat:support_chat', kwargs={'user_pk': user.pk})
            last_message.get_title = user.email
            messages.append(last_message) 

    return render(request, 'chat/support.html', context={'messages': messages}) 

@permission_required('user.support_chat', raise_exception=True)
def support_chat(request, user_pk):
    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        user = None
    
    messages = MessageSupport.objects.filter(Q(sender__pk=user.pk) | Q(recipient__pk=user.pk)).order_by('sent_at')
    messages_serializer_data = MessageSerializerList(messages, many=True, context={'request': request, 'is_support': True}).data
    messages.filter(recipient__isnull=True, read=False).update(read=True)
    
    context = {
        'messages': json.dumps(messages_serializer_data),
        'user': user,
    }

    return render(request, 'chat/support_chat.html', context=context)

@permission_required('user.support_chat', raise_exception=True)
def get_new_support_messages(request, user_pk):
    if request.method == 'GET':
        messages = MessageSupport.objects.filter(sender__pk=user_pk, recipient__isnull=True, read=False).order_by('sent_at')
        data = MessageSerializerList(messages, many=True, context={'request': request, 'is_support': True}).data
        messages.update(read=True)
        return JsonResponse({'data': data})

@permission_required('user.support_chat', raise_exception=True)
def send_support_message(request, user_pk):
    if request.method == 'POST':
        data = request.POST
        try:
            user = User.objects.get(pk=user_pk)
            new_message = MessageSupport.objects.create(text=data.get('text'), sender=None, recipient=user)

            messages = MessageSupport.objects.filter(Q(read=False)).filter(Q(sender=user, recipient__isnull=True) | Q(pk=new_message.pk)).order_by('sent_at')
            
            data = MessageSerializerList(messages, many=True, context={'request': request, 'is_support': True}).data
            messages.filter(recipient__isnull=True, read=False).update(read=True)

            return JsonResponse({'data': data})
        except User.DoesNotExist:
            return JsonResponse({'data': []})

@login_required
def list(request):
    user = request.user
    messages = []

    # booking renter
    msgs = MessageBooking.objects.filter(Q(sender=user) | Q(recipient=user)).order_by('-pk')
    bookings = Booking.objects.filter(Q(renter=user)).prefetch_related(
        Prefetch('messages', queryset=msgs, to_attr='last_messages')
    )
    for booking in bookings:
        if booking.last_messages:
            last_message = booking.last_messages[0]
            last_message.badge = f'<div class="badge bg-light text-primary border fw-normal">Бронирование № {booking.pk}</div>'
            messages.append(last_message)        

    # booking boat owner
    msgs = MessageBooking.objects.filter(Q(sender=user) | Q(recipient=user)).order_by('-pk')
    requests = Booking.objects.filter(Q(boat__owner=user)).prefetch_related(
        Prefetch('messages', queryset=msgs, to_attr='last_messages')
    )
    for req in requests:
        if req.last_messages:
            last_message = req.last_messages[0]
            last_message.badge = f'<div class="badge bg-light text-primary border fw-normal">Заявка на бронирование № {req.pk}</div>'
            messages.append(last_message)  

    # boat owner
    msgs = MessageBoat.objects.filter(Q(sender=user) | Q(recipient=user)).order_by('-pk')
    boats = Boat.objects.filter(Q(owner=user)).prefetch_related(
        Prefetch('messages', queryset=msgs, to_attr='last_messages')
    )
    for boat in boats:
        if boat.last_messages:
            last_message = boat.last_messages[0]
            last_message.badge = '<div class="badge bg-light text-primary border fw-normal">Лодка</div>' 
            messages.append(last_message)  

    messages = sorted(messages, key=lambda message: message.pk, reverse=True)

    last_message_support = MessageSupport.objects.filter(sender=user).union(MessageSupport.objects.filter(recipient=user)).last()
    if last_message_support:
        last_message_support.badge = '<div class="badge bg-warning text-primary border border-warning fw-normal">Поддержка</div>'
        messages.insert(0, last_message_support)
    
    if not last_message_support:
        last_message_support = MessageSupport(text='Сообщений пока нет', read=True)    
        last_message_support.badge = '<div class="badge bg-warning text-primary border-warning fw-normal">Поддержка</div>'   
        messages.insert(0, last_message_support)

    context={
        'messages': messages,
        'unread_exists': user.messages_as_recipient.filter(read=False).exists()
    }

    return render(request, 'chat/list.html', context=context)

@login_required
def get_new_messages_booking(request, pk):
    if request.method == 'GET':
        try:
            booking = Booking.objects.get(Q(pk=pk), Q(renter=request.user) | Q(boat__owner=request.user))

            messages = MessageBooking.objects.filter(booking=booking, recipient=request.user, read=False).order_by('sent_at')
            data = MessageSerializerList(messages, many=True, context={'request': request}).data
            messages.update(read=True)

            return JsonResponse({'data': data})
            
        except Booking.DoesNotExist:
            return JsonResponse({'message': 'Бронирование не найдено'}, status=400)

@login_required
def get_new_messages(request):
    if request.method == 'GET':
        messages = MessageSupport.objects.filter(recipient=request.user, read=False).order_by('sent_at')
        data = MessageSerializerList(messages, many=True, context={'request': request}).data
        messages.update(read=True)
        return JsonResponse({'data': data})

@login_required
def get_new_messages_boat(request, pk):

    def _not_found():
        return JsonResponse({'message': 'Бронирование не найдено'}, status=400)

    if request.method == 'GET':
        try:
            boat = Boat.objects.get(pk=pk)
            is_moderator = request.user.has_perm('boat.moderate_boats')

            messages = MessageBoat.objects.filter(boat=boat, read=False)
            if boat.owner == request.user:
                messages = messages.filter(recipient=request.user)
            elif is_moderator:
                messages = messages.filter(recipient__isnull=True)
            else:
                return _not_found()      
            messages = messages.order_by('sent_at')

            data = MessageSerializerList(messages, many=True, context={'request': request}).data
            messages.update(read=True)
            return JsonResponse({'data': data})
            
        except Boat.DoesNotExist:
            return _not_found()

@login_required
def send_message_booking(request, pk):
    if request.method == 'POST':
        data = request.POST
        try:
            booking = Booking.objects.get(Q(pk=pk), Q(renter=request.user) | Q(boat__owner=request.user))
            recipient = booking.boat.owner if booking.renter == request.user else booking.renter
            
            new_message = MessageBooking.objects.create(text=data.get('text'), sender=request.user, recipient=recipient, booking=booking)

            messages = MessageBooking.objects.filter(Q(booking=booking), Q(read=False), Q(recipient=request.user) | Q(pk=new_message.pk)).order_by('sent_at')
            data = MessageSerializerList(messages, many=True, context={'request': request}).data
            messages.filter(recipient=request.user, read=False).update(read=True)

            return JsonResponse({'data': data})
        except Booking.DoesNotExist:
            return JsonResponse({'message': 'Не удалось отправить сообщение. Бронирование не найдено'}, status=400)
     

@login_required
def send_message_boat(request, pk):
    if request.method == 'POST':
        data = request.POST
        try:
            boat = Boat.objects.get(pk=pk)
            is_moderator = request.user.has_perm('boat.moderate_boats')

            if boat.owner == request.user:
                recipient = None
                sender = boat.owner
            elif is_moderator:
                recipient = boat.owner
                sender = None  
            else:
                return JsonResponse({'message': 'Не удалось отправить сообщение. Лодка не найдена'}, status=400)

            new_message = MessageBoat.objects.create(text=data.get('text'), sender=sender, recipient=recipient, boat=boat)
            
            messages = MessageBoat.objects.filter(Q(boat=boat), Q(read=False), Q(recipient=request.user) | Q(pk=new_message.pk)).order_by('sent_at')
            data = MessageSerializerList(messages, many=True, context={'request': request}).data
            messages.filter(recipient=request.user, read=False).update(read=True)

            return JsonResponse({'data': data})
        
        except Booking.DoesNotExist:
            return JsonResponse({'message': 'Не удалось отправить сообщение. Лодка не найдена'}, status=400)

@login_required
def send_message(request):
    if request.method == 'POST':
        data = request.POST
        new_message = MessageSupport.objects.create(text=data.get('text'), sender=request.user, recipient=None)

        messages = MessageSupport.objects.filter(
            Q(read=False), 
            Q(recipient=request.user) | Q(pk=new_message.pk)
        ).order_by('sent_at')
        
        data = MessageSerializerList(messages, many=True, context={'request': request}).data
        messages.filter(recipient=request.user, read=False).update(read=True)

        return JsonResponse({'data': data})
        

@login_required
def message(request):
    messages = MessageSupport.objects.filter(Q(sender=request.user) | Q(recipient=request.user)).order_by('sent_at')
    messages_serializer_data = MessageSerializerList(messages, many=True, context={'request': request}).data

    messages.filter(recipient=request.user, read=False).update(read=True)
    
    context = {
        'messages': json.dumps(messages_serializer_data)
    }
    return render(request, 'chat/message.html', context=context)

@login_required
def booking(request, pk):
    try:
        booking = Booking.objects.get(Q(pk=pk), Q(renter=request.user) | Q(boat__owner=request.user))
        messages = MessageBooking.objects.filter(Q(booking=booking), Q(sender=request.user) | Q(recipient=request.user)).order_by('sent_at')
        messages_serializer_data = MessageSerializerList(messages, many=True, context={'request': request}).data

        messages.filter(recipient=request.user, read=False).update(read=True)
        
        context = {
            'booking': booking,
            'messages': json.dumps(messages_serializer_data)
        }
        return render(request, 'chat/booking.html', context=context)
    except Booking.DoesNotExist:
        return render(request, 'not_found.html', status=404) 

@login_required
def boat(request, pk):
    try:
        is_moderator = request.user.has_perm('boat.moderate_boats')

        boat = Boat.objects.get(Q(pk=pk))
        if not is_moderator and boat.owner != request.user:
            return render(request, 'not_found.html', status=404) 

        messages = MessageBoat.objects.filter(boat=boat)
        if is_moderator:
            messages = messages.filter(Q(sender__isnull=True) | Q(recipient__isnull=True))
        else:
            messages = messages.filter(Q(sender=request.user) | Q(recipient=request.user))
        messages = messages.order_by('sent_at')

        messages_ser_data = MessageSerializerList(messages, many=True, context={'request': request}).data

        if is_moderator:
            messages.filter(Q(sender__isnull=True) | Q(recipient__isnull=True), read=False).update(read=True)
        else:
            messages.filter(recipient=request.user, read=False).update(read=True)
        
        context = {
            'boat': boat,
            'messages': json.dumps(messages_ser_data)
        }

        return render(request, 'chat/boat.html', context=context)
    except Boat.DoesNotExist:
        return render(request, 'not_found.html', status=404)

@login_required
def read_all(request):
    request.user.messages_as_recipient.filter(read=False).update(read=True)
    return redirect(reverse('chat:list'))