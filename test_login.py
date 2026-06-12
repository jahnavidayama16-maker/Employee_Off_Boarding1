import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_offboarding_system.settings')
django.setup()

from django.test import Client
from accounts.models import CustomUser

# 1. Ensure employee is active first to show it works
emp = CustomUser.objects.get(email='employee@microlent.com')
emp.is_active = True
emp.set_password('employee123')
emp.save()

client = Client()
print("1. Testing login with ACTIVE employee...")
response = client.post('/login/', {'username': 'employee@microlent.com', 'password': 'employee123'})
# Should redirect to employee dashboard (status code 302)
print("Response status code:", response.status_code)
if response.status_code == 302:
    print("Success! Active employee logged in and was redirected to", response.url)

# Logout
client.logout()

# 2. Deactivate employee
emp.is_active = False
emp.save()

print("\n2. Testing login with DEACTIVATED employee...")
response = client.post('/login/', {'username': 'employee@microlent.com', 'password': 'employee123'})
# Should return to login page with an error, not redirect
print("Response status code:", response.status_code)
if response.status_code == 200:
    print("Blocked! Deactivated employee stayed on the login page.")
    # Check if form errors exist
    if response.context and 'form' in response.context and response.context['form'].errors:
        print("Error message provided to user:", list(response.context['form'].errors.values())[0][0])

# Reactivate the employee so the user can test manually right after
emp.is_active = True
emp.save()
print("\nEmployee reactivated so you can use the account.")
