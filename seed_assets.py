import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_offboarding_system.settings')
django.setup()

from assets.models import Asset
from accounts.models import CustomUser

emp = CustomUser.objects.filter(email='employee@microlent.com').first()

if emp:
    print(f"Adding assets for {emp}...")
    if Asset.objects.count() == 0:
        Asset.objects.create(
            name="MacBook Pro 16-inch (M3)",
            serial_number="MBP-2024-M3-001",
            assigned_to=emp,
            status="Issued"
        )
        Asset.objects.create(
            name="Dell UltraSharp 27 Monitor",
            serial_number="DELL-U27-042",
            assigned_to=emp,
            status="Issued"
        )
        Asset.objects.create(
            name="Office Access Keycard",
            serial_number="KEY-90210",
            assigned_to=emp,
            status="Issued"
        )
        print("Success! Created 3 assets for the employee.")
    else:
        print("Assets already exist in the db.")
else:
    print("Employee not found.")
