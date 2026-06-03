from .models import Notification

def notifications(request):
    if request.user.is_authenticated:
        notifs = Notification.objects.filter(
            recipient=request.user
        ).order_by('-created_at')[:5]
        
        unread_count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        
        return {
            'notifications': notifs,
            'unread_notif_count': unread_count,
        }
    return {
        'notifications': [],
        'unread_notif_count': 0,
    }