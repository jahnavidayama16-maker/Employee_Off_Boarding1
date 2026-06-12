from django.db import models
from resignations.models import Resignation

class Clearance(models.Model):
    DEPT_CHOICES = (
        ('IT', 'IT'),
        ('Finance', 'Finance'),
        ('Library', 'Library'),
    )
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Cleared', 'Cleared'),
    )
    resignation = models.ForeignKey(Resignation, on_delete=models.CASCADE, related_name='clearances')
    department_name = models.CharField(max_length=50, choices=DEPT_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    remarks = models.TextField(blank=True, null=True)
    cleared_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.department_name} Clearance for {self.resignation.employee}"

    class Meta:
        unique_together = ('resignation', 'department_name')

# Signals to auto-create clearances
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Resignation)
def auto_create_clearances(sender, instance, created, **kwargs):
    if instance.manager_status == 'Approved':
        # Only create if they don't exist yet
        for dept_id, dept_name in Clearance.DEPT_CHOICES:
            Clearance.objects.get_or_create(
                resignation=instance,
                department_name=dept_id
            )
