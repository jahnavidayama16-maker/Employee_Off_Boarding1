from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Resignation
from .forms import ResignationForm
from reports.models import AuditLog


@login_required
def request_resignation(request):
    # Prevent employees from submitting multiple active resignations
    existing = Resignation.objects.filter(
        employee=request.user
    ).exclude(
        manager_status='Rejected'
    ).exclude(
        hr_status='Rejected'
    ).exclude(
        admin_status='Rejected'
    ).first()

    if existing:
        from django.contrib import messages
        messages.warning(request, "You already have an active resignation in progress. Please wait for it to be resolved before submitting a new one.")
        return redirect('employee_dashboard')

    if request.method == 'POST':
        form = ResignationForm(request.POST, request.FILES)
        if form.is_valid():
            res = form.save(commit=False)
            res.employee = request.user
            res.save()
            AuditLog.objects.create(user=request.user, action="Submitted resignation request.")
            from django.contrib import messages
            messages.success(request, "Your resignation request has been submitted successfully.")
            return redirect('employee_dashboard')
    else:
        form = ResignationForm()
    return render(request, 'resignations/request_form.html', {'form': form})


@login_required
def team_approvals(request):
    if request.user.role == 'Manager':
        resignations = Resignation.objects.filter(
            employee__department=request.user.department,
            manager_status='Pending'
        ).select_related('employee', 'employee__department')
        return render(request, 'resignations/approval_panel.html', {
            'resignations': resignations, 'role_type': 'Manager'
        })
    elif request.user.role == 'HR':
        resignations = Resignation.objects.filter(
            manager_status='Approved',
            hr_status='Pending'
        ).select_related('employee', 'employee__department')
        return render(request, 'resignations/approval_panel.html', {
            'resignations': resignations, 'role_type': 'HR'
        })
    elif request.user.role == 'Admin':
        resignations = Resignation.objects.filter(
            hr_status='Approved',
            admin_status='Pending'
        ).select_related('employee', 'employee__department')
        return render(request, 'resignations/approval_panel.html', {
            'resignations': resignations, 'role_type': 'Admin'
        })
    return redirect('home')


@login_required
def approve_resignation(request, pk, role):
    resignation = get_object_or_404(Resignation, pk=pk)

    if request.method == 'POST':
        # --- REJECTION HANDLING (all roles) ---
        if 'reject' in request.POST:
            reason = request.POST.get('rejection_reason', 'No specific reason provided.').strip()
            if not reason:
                reason = 'No specific reason provided.'

            if role == 'Manager' and request.user.role == 'Manager':
                resignation.manager_status = 'Rejected'
                resignation.rejection_reason = reason
                AuditLog.objects.create(
                    user=request.user,
                    action=f"Manager rejected resignation of {resignation.employee.email}. Reason: {reason}"
                )
            elif role == 'HR' and request.user.role == 'HR':
                # BUG FIX: HR rejection was missing entirely in original code
                resignation.hr_status = 'Rejected'
                resignation.rejection_reason = reason
                AuditLog.objects.create(
                    user=request.user,
                    action=f"HR rejected resignation of {resignation.employee.email}. Reason: {reason}"
                )
            elif role == 'Admin' and request.user.role == 'Admin':
                # BUG FIX: Admin rejection was missing entirely in original code
                resignation.admin_status = 'Rejected'
                resignation.rejection_reason = reason
                AuditLog.objects.create(
                    user=request.user,
                    action=f"Admin rejected resignation of {resignation.employee.email}. Reason: {reason}"
                )

            resignation.save()
            return redirect('team_approvals')

    # --- APPROVAL HANDLING (GET request) ---
    if role == 'Manager' and request.user.role == 'Manager':
        resignation.manager_status = 'Approved'
        AuditLog.objects.create(
            user=request.user,
            action=f"Manager approved resignation of {resignation.employee.email}."
        )
    elif role == 'HR' and request.user.role == 'HR':
        resignation.hr_status = 'Approved'
        AuditLog.objects.create(
            user=request.user,
            action=f"HR approved resignation of {resignation.employee.email}."
        )
    elif role == 'Admin' and request.user.role == 'Admin':
        resignation.admin_status = 'Approved'
        AuditLog.objects.create(
            user=request.user,
            action=f"Admin finalized resignation of {resignation.employee.email}."
        )
        # Soft-delete: deactivate the employee account
        emp = resignation.employee
        emp.is_active = False
        emp.save()
        AuditLog.objects.create(
            user=request.user,
            action=f"System auto-deactivated user account: {emp.email}."
        )
    else:
        # Unauthorized attempt - silently redirect
        return redirect('team_approvals')

    resignation.save()
    return redirect('team_approvals')


@login_required
def submit_exit_feedback(request, pk):
    if request.method == 'POST':
        resignation = get_object_or_404(Resignation, pk=pk, employee=request.user)
        feedback = request.POST.get('exit_feedback', '').strip()
        if feedback:
            resignation.exit_feedback = feedback
            resignation.save()
            AuditLog.objects.create(user=request.user, action="Submitted Exit Interview Feedback.")
            from django.contrib import messages
            messages.success(request, "Exit feedback submitted successfully. Thank you.")
        else:
            from django.contrib import messages
            messages.warning(request, "Please provide your exit feedback before submitting.")
    return redirect('employee_dashboard')
