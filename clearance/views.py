from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from reports.models import AuditLog
from .models import Clearance

@login_required
def clearance_list(request):
    if request.user.role in ['HR', 'Admin']:
        from resignations.models import Resignation
        # We fetch Resignations currently in the pipeline context, prefetching their clearance items
        resignations = Resignation.objects.filter(manager_status='Approved').prefetch_related('clearances').distinct().order_by('-created_at')
        return render(request, 'clearance/clearance_list.html', {'resignations': resignations})
    return redirect('home')

@login_required
def clear_item(request, pk):
    from django.utils import timezone
    clearance = get_object_or_404(Clearance, pk=pk)
    if request.method == 'POST' and request.user.role in ['HR', 'Admin']:
        remarks = request.POST.get('remarks', '').strip()
        is_cleared = request.POST.get('is_cleared') == 'on'
        
        # Enforcing user prompt: Remarks are required field
        if is_cleared and remarks:
            clearance.status = 'Cleared'
            clearance.remarks = remarks
            clearance.cleared_at = timezone.now()
            clearance.save()
            AuditLog.objects.create(user=request.user, action=f"Cleared {clearance.department_name} checklist for {clearance.resignation.employee.email}")
            
    return redirect('clearance_list')
