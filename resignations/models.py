from django.db import models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

class Resignation(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resignations')
    reason = models.TextField()
    expected_last_day = models.DateField()
    manager_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    hr_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    admin_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    rejection_reason = models.TextField(blank=True, null=True)
    resignation_letter = models.FileField(upload_to='resignation_letters/', blank=True, null=True)
    exit_feedback = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    current_stage = models.CharField(max_length=50, default='Submitted')
    next_role = models.CharField(max_length=50, default='Manager')

    def save(self, *args, **kwargs):
        if self.manager_status == 'Pending':
            self.current_stage = 'Manager Review'
            self.next_role = 'Manager'
        elif self.manager_status == 'Rejected':
            self.current_stage = 'Rejected by Manager'
            self.next_role = 'None'
        elif self.manager_status == 'Approved' and self.hr_status == 'Pending':
            self.current_stage = 'HR Clearance'
            self.next_role = 'HR'
        elif self.hr_status == 'Rejected':
            self.current_stage = 'Rejected by HR'
            self.next_role = 'None'
        elif self.hr_status == 'Approved' and self.admin_status == 'Pending':
            self.current_stage = 'Admin Final Sign-off'
            self.next_role = 'Admin'
        elif self.admin_status == 'Rejected':
            self.current_stage = 'Rejected by Admin'
            self.next_role = 'None'
        elif self.admin_status == 'Approved':
            self.current_stage = 'Completed'
            self.next_role = 'None'
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employee.full_name} - {self.expected_last_day}"
