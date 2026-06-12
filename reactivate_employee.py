import os, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_offboarding_system.settings')
django.setup()

from accounts.models import CustomUser

emp = CustomUser.objects.get(email='employee@microlent.com')
emp.is_active = True
emp.save()
print("Employee reactivated!")
