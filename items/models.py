from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


def expiry_date():
    return timezone.now() + timedelta(days=30)


class Item(models.Model):

    ITEM_TYPE_CHOICES = [
        ('lost', 'Lost'),
        ('found', 'Found'),
    ]

    CATEGORY_CHOICES = [
        ('electronics', 'Electronics'),
        ('documents', 'Documents'),
        ('keys', 'Keys'),
        ('accessories', 'Accessories'),
        ('clothing', 'Clothing'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('claimed', 'Claimed'),
        ('resolved', 'Resolved'),
        ('expired', 'Expired'),
    ]

    posted_by         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='items')
    item_type         = models.CharField(max_length=10, choices=ITEM_TYPE_CHOICES)
    title             = models.CharField(max_length=200)
    category          = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description       = models.TextField()
    location          = models.CharField(max_length=200)
    date_of_incident  = models.DateField()
    image             = models.ImageField(upload_to='items/', blank=True, null=True)
    status            = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    created_at        = models.DateTimeField(auto_now_add=True)
    expires_at        = models.DateTimeField(default=expiry_date)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.item_type.upper()}] {self.title}"

    def is_expired(self):
        return timezone.now() > self.expires_at


class Claim(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    item              = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='claims')
    claimant          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='claims')
    proof_description = models.TextField()
    contact_details   = models.CharField(max_length=200)
    status            = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    admin_remarks     = models.TextField(blank=True)
    submitted_at      = models.DateTimeField(auto_now_add=True)
    resolved_at       = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-submitted_at']
        unique_together = ('item', 'claimant')

    def __str__(self):
        return f"Claim by {self.claimant.email} on {self.item.title}"

class FoundResponse(models.Model):
    item            = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='found_responses')
    responder       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='found_responses')
    message         = models.TextField()
    contact_details = models.CharField(max_length=200)
    submitted_at    = models.DateTimeField(auto_now_add=True)
    is_read         = models.BooleanField(default=False)

    class Meta:
        ordering = ['-submitted_at']
        unique_together = ('item', 'responder')

    def __str__(self):
        return f"{self.responder.email} found {self.item.title}"  
class Notification(models.Model):

    NOTIF_TYPE_CHOICES = [
        ('claim_submitted', 'Claim Submitted'),
        ('claim_approved',  'Claim Approved'),
        ('claim_rejected',  'Claim Rejected'),
        ('found_response',  'Someone Found Your Item'),
        ('item_resolved',   'Item Resolved'),
    ]

    recipient  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notif_type = models.CharField(max_length=30, choices=NOTIF_TYPE_CHOICES)
    item       = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    message    = models.CharField(max_length=300)
    is_read    = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notif_type}] → {self.recipient.email}"      