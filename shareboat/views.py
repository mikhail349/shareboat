from django.shortcuts import render
from boat.models import Boat

def index(request):
    boats_states = set(Boat.published.filter(coordinates__pk__isnull=False).values_list('coordinates__state', flat=True))
    bases_states = set(Boat.published.filter(base__pk__isnull=False).values_list('base__state', flat=True))
    states = sorted(boats_states | bases_states)
    context = {
        'states': states,
        'steps': ('Найди лодку', 'Забронируй', 'Получи подтверждение от владельца', 'Отправляйся в путешествие!')
    }
    return render(request, 'index.html', context=context)

def not_found(request):
    return render(request, 'not_found.html', status=404)
