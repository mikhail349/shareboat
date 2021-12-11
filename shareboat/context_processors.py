from boat.models import Boat

def nav_counters(request):
    boats_on_moderation_count = Boat.objects.filter(status=Boat.Status.ON_MODERATION).count()
    return {
        'nav_counters': {
            'boats_on_moderation_count': boats_on_moderation_count
        }
    } 
    