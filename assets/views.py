from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Asset
from django.utils import timezone
from reports.models import AuditLog
from django.db.models import Q


@login_required
def manage_assets(request):
    if request.user.role in ['HR', 'Admin']:
        assets = Asset.objects.all().select_related('assigned_to').order_by('-id')
        is_admin_hr = True
    else:
        assets = Asset.objects.filter(assigned_to=request.user).order_by('-id')
        is_admin_hr = False

    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    if search_query:
        assets = assets.filter(
            Q(name__icontains=search_query) |
            Q(assigned_to__full_name__icontains=search_query) |
            Q(assigned_to__email__icontains=search_query)
        )
    if status_filter in ['Issued', 'Returned', 'Lost']:
        assets = assets.filter(status=status_filter)

    # For assign form: get all active employees
    from accounts.models import CustomUser
    employees = CustomUser.objects.filter(is_active=True).order_by('full_name') if is_admin_hr else []

    return render(request, 'assets/asset_management.html', {
        'assets': assets,
        'is_admin_hr': is_admin_hr,
        'search_query': search_query,
        'status_filter': status_filter,
        'employees': employees,
    })


@login_required
def update_status(request, pk):
    if request.method == 'POST' and request.user.role in ['HR', 'Admin']:
        asset = get_object_or_404(Asset, pk=pk)
        new_status = request.POST.get('status')
        if new_status in ['Issued', 'Returned', 'Lost']:
            old_status = asset.status
            asset.status = new_status
            if new_status == 'Returned':
                asset.returned_date = timezone.now()
            asset.save()
            AuditLog.objects.create(
                user=request.user,
                action=f"Changed asset '{asset.name}' status from {old_status} to {new_status}."
            )
            messages.success(request, f"Asset '{asset.name}' status updated to {new_status}.")
        else:
            messages.error(request, "Invalid status value.")
    return redirect('manage_assets')


@login_required
def assign_asset(request):
    """NEW VIEW: Allows HR/Admin to assign a new asset to an employee."""
    if request.user.role not in ['HR', 'Admin']:
        messages.error(request, "You do not have permission to assign assets.")
        return redirect('manage_assets')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        employee_id = request.POST.get('assigned_to')

        if not name or not employee_id:
            messages.error(request, "All fields are required to assign an asset.")
            return redirect('manage_assets')

        from accounts.models import CustomUser
        try:
            employee = CustomUser.objects.get(pk=employee_id, is_active=True)
        except CustomUser.DoesNotExist:
            messages.error(request, "Selected employee not found.")
            return redirect('manage_assets')

        asset = Asset.objects.create(
            name=name,
            assigned_to=employee,
            status='Issued',
            manager_approval='Pending',
            assigned_date=timezone.now(),
        )
        AuditLog.objects.create(
            user=request.user,
            action=f"Assigned asset '{asset.name}' to {employee.full_name} ({employee.email})."
        )
        messages.success(request, f"Asset '{name}' successfully assigned to {employee.full_name}.")
        return redirect('manage_assets')

    return redirect('manage_assets')


@login_required
def team_assets(request):
    if request.user.role != 'Manager':
        return redirect('home')
        
    # Get all employees in the manager's department
    from accounts.models import CustomUser
    department_users = CustomUser.objects.filter(department=request.user.department).exclude(id=request.user.id)
    
    # Get assets for those employees
    assets = Asset.objects.filter(assigned_to__in=department_users).select_related('assigned_to').order_by('-id')
    
    search_query = request.GET.get('q', '').strip()
    if search_query:
        assets = assets.filter(
            Q(name__icontains=search_query) |
            Q(assigned_to__full_name__icontains=search_query)
        )
        
    return render(request, 'assets/team_assets.html', {
        'assets': assets,
        'search_query': search_query,
    })


@login_required
def manager_approve_asset(request, pk):
    if request.user.role != 'Manager':
        return redirect('home')
        
    if request.method == 'POST':
        asset = get_object_or_404(Asset, pk=pk)
        
        # Verify the asset belongs to an employee in the manager's department
        if not asset.assigned_to.department or asset.assigned_to.department != request.user.department:
            messages.error(request, "You can only approve assets for your own department.")
            return redirect('team_assets')
            
        approval_status = request.POST.get('manager_approval')
        remarks = request.POST.get('manager_remarks', '').strip()
        
        if approval_status in ['Pending', 'Cleared']:
            asset.manager_approval = approval_status
            asset.manager_remarks = remarks
            asset.save()
            AuditLog.objects.create(
                user=request.user,
                action=f"Manager marked asset '{asset.name}' as {approval_status}."
            )
            messages.success(request, f"Asset '{asset.name}' approval status updated to {approval_status}.")
        else:
            messages.error(request, "Invalid approval status.")
            
    return redirect('team_assets')
