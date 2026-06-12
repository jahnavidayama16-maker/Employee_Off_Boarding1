from resignations.models import Resignation
from assets.models import Asset

def notifications(request):
    if not request.user.is_authenticated:
        return {'notifications': [], 'notification_count': 0}
    
    notifications = []
    
    # 1. Assets Pending Return
    pending_assets = Asset.objects.filter(assigned_to=request.user).exclude(status='Returned')
    for asset in pending_assets:
        notifications.append({
            'icon': 'bi-laptop',
            'color': 'warning',
            'title': 'Asset Pending Return',
            'text': f'Please return {asset.name}.',
            'time': 'Action Required'
        })
        
    # 2. Resignation updates 
    resignation = Resignation.objects.filter(employee=request.user).order_by('-created_at').first()
    if resignation:
        if resignation.admin_status == 'Approved':
            notifications.append({
                'icon': 'bi-check-circle-fill',
                'color': 'success',
                'title': 'Off-boarding Complete',
                'text': 'Your resignation has been finalized by System Admin.',
                'time': 'Completed'
            })
        elif resignation.hr_status == 'Approved':
            notifications.append({
                'icon': 'bi-person-badge',
                'color': 'primary',
                'title': 'HR Clearance Approved',
                'text': 'Your resignation was approved by HR.',
                'time': 'Recent'
            })
        elif resignation.manager_status == 'Approved':
            notifications.append({
                'icon': 'bi-person-workspace',
                'color': 'info',
                'title': 'Manager Approved',
                'text': 'Your manager has approved your resignation request.',
                'time': 'Recent'
            })
            
    # Approver notifications (Managers / HR / Admins)
    if request.user.role == 'Manager':
        count = Resignation.objects.filter(employee__department=request.user.department, manager_status='Pending').count()
        if count > 0:
            notifications.append({
                'icon': 'bi-inbox-fill',
                'color': 'danger',
                'title': 'Pending Approvals',
                'text': f'You have {count} team resignations awaiting your review.',
                'time': 'Action Required'
            })
    elif request.user.role == 'HR':
        count = Resignation.objects.filter(manager_status='Approved', hr_status='Pending').count()
        if count > 0:
            notifications.append({
                'icon': 'bi-exclamation-circle-fill',
                'color': 'danger',
                'title': 'Pending HR Reviews',
                'text': f'{count} resignations are cleared by managers and await HR approval.',
                'time': 'Action Required'
            })
    elif request.user.role == 'Admin':
        count = Resignation.objects.filter(hr_status='Approved', admin_status='Pending').count()
        if count > 0:
            notifications.append({
                'icon': 'bi-shield-exclamation',
                'color': 'danger',
                'title': 'Final Sign-offs Required',
                'text': f'{count} resignations are awaiting final admin system closure.',
                'time': 'Action Required'
            })

    return {
        'notifications': notifications,
        'notification_count': len(notifications)
    }
