from django.contrib import admin
from .models import Item, Claim, FoundResponse ,Notification


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display  = ('title', 'item_type', 'category', 'status', 'posted_by', 'created_at')
    list_filter   = ('item_type', 'category', 'status')
    search_fields = ('title', 'description', 'location')


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display  = ('item', 'claimant', 'status', 'submitted_at')
    list_filter   = ('status',)
    search_fields = ('item__title', 'claimant__email')
    readonly_fields = ('submitted_at',)

@admin.register(FoundResponse)
class FoundResponseAdmin(admin.ModelAdmin):
    list_display  = ('item', 'responder', 'submitted_at', 'is_read')
    list_filter   = ('is_read',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display  = ('recipient', 'notif_type', 'message', 'is_read', 'created_at')
    list_filter   = ('notif_type', 'is_read')
    search_fields = ('message',)