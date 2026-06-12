import os, django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_offboarding_system.settings')
django.setup()

from accounts.models import CustomUser

with open("registered_users.txt", "w", encoding="utf-8") as f:
    for u in CustomUser.objects.all():
        f.write(f"Email: {u.email}, Role: {getattr(u, 'role', 'N/A')}, Active: {u.is_active}\n")
