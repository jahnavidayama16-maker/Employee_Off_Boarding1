from django.db import models
from django.conf import settings

from django.utils import timezone

class Asset(models.Model):
    name = models.CharField(max_length=100)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assets')
    
    APPROVAL_CHOICES = (
        ('Pending', 'Pending'),
        ('Cleared', 'Cleared'),
    )
    manager_approval = models.CharField(max_length=20, choices=APPROVAL_CHOICES, default='Pending')
    manager_remarks = models.TextField(blank=True, null=True)

    STATUS_CHOICES = (
        ('Issued', 'Issued'),
        ('Returned', 'Returned'),
        ('Lost', 'Lost'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Issued')
    assigned_date = models.DateField(default=timezone.now)
    returned_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.assigned_to.full_name})"
