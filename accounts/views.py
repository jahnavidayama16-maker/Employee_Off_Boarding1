from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from resignations.models import Resignation
from assets.models import Asset
from clearance.models import Clearance


def landing_page(request):
    if request.user.is_authenticated:
        return dashboard_redirect(request)
    return render(request, 'accounts/landing.html')


@login_required
def dashboard_redirect(request):
    role = request.user.role
    if role == 'Employee':
        return redirect('employee_dashboard')
    elif role == 'Manager':
        return redirect('manager_dashboard')
    elif role == 'HR':
        return redirect('hr_dashboard')
    elif role == 'Admin':
        return redirect('admin_dashboard')
    return redirect('login')


@login_required
def employee_dashboard(request):
    res_count = Resignation.objects.filter(employee=request.user).count()
    # FIX: Only count non-returned assets
    asset_count = Asset.objects.filter(assigned_to=request.user).exclude(status='Returned').count()
    latest_resignation = Resignation.objects.filter(employee=request.user).order_by('-created_at').first()
    # Get all assets for the employee
    my_assets = Asset.objects.filter(assigned_to=request.user).order_by('-id')
    return render(request, 'accounts/dashboards/employee_dashboard.html', {
        'res_count': res_count,
        'asset_count': asset_count,
        'latest_resignation': latest_resignation,
        'my_assets': my_assets,
    })


@login_required
def manager_dashboard(request):
    from accounts.models import CustomUser, Project

    # FIX: Exclude manager themselves from team_size count
    team_size = request.user.department.employees.exclude(pk=request.user.pk).count() if request.user.department else 0
    pending_approvals = Resignation.objects.filter(
        employee__department=request.user.department,
        manager_status='Pending'
    ).count()
    # FIX: Add team members list for manager to see
    team_members = []
    if request.user.department:
        team_members = CustomUser.objects.filter(
            department=request.user.department,
            role='Employee',
            is_active=True
        ).exclude(pk=request.user.pk)

    # Recent approvals by this manager
    recent_actions = Resignation.objects.filter(
        employee__department=request.user.department
    ).exclude(manager_status='Pending').order_by('-created_at')[:5]

    # Project tracking for the department
    dept_projects = Project.objects.filter(department=request.user.department) if request.user.department else Project.objects.none()
    ongoing_projects = dept_projects.filter(status='Ongoing').count()
    pending_projects = dept_projects.filter(status='Pending').count()
    completed_projects = dept_projects.filter(status='Completed').count()
    total_projects = dept_projects.count()

    # Recent project list
    team_projects = dept_projects.select_related('assigned_to')[:10]

    # Assets pending manager approval
    assets_pending_approval = Asset.objects.filter(
        assigned_to__department=request.user.department,
        manager_approval='Pending'
    ).count() if request.user.department else 0

    return render(request, 'accounts/dashboards/manager_dashboard.html', {
        'team_size': team_size,
        'pending_approvals': pending_approvals,
        'team_members': team_members,
        'recent_actions': recent_actions,
        'ongoing_projects': ongoing_projects,
        'pending_projects': pending_projects,
        'completed_projects': completed_projects,
        'total_projects': total_projects,
        'team_projects': team_projects,
        'assets_pending_approval': assets_pending_approval,
    })


@login_required
def hr_dashboard(request):
    import json
    from accounts.forms import EmployeeCreationForm
    from accounts.models import CustomUser

    pending_hr = Resignation.objects.filter(hr_status='Pending', manager_status='Approved').count()
    completed_exits = Resignation.objects.filter(admin_status='Approved').count()
    assets_pending = Asset.objects.exclude(status='Returned').count()
    pending_clearances = Clearance.objects.filter(status='Pending').count()

    status_counts = {
        'Pending Manager': Resignation.objects.filter(manager_status='Pending').count(),
        'Pending HR': pending_hr,
        'Pending Admin': Resignation.objects.filter(hr_status='Approved', admin_status='Pending').count(),
        'Completed': completed_exits,
    }

    # Recent resignations for HR view
    recent_resignations = Resignation.objects.filter(
        manager_status='Approved'
    ).select_related('employee', 'employee__department').order_by('-created_at')[:8]

    # Employee Management
    employees = CustomUser.objects.filter(role='Employee').select_related('department').order_by('-id')
    employee_form = EmployeeCreationForm()

    return render(request, 'accounts/dashboards/hr_dashboard.html', {
        'pending_hr': pending_hr,
        'pending_clearances': pending_clearances,
        'completed_exits': completed_exits,
        'assets_pending': assets_pending,
        'chart_labels': json.dumps(list(status_counts.keys())),
        'chart_data': json.dumps(list(status_counts.values())),
        'recent_resignations': recent_resignations,
        'employees': employees,
        'employee_form': employee_form,
    })


@login_required
def admin_dashboard(request):
    from accounts.models import CustomUser, Department
    from accounts.forms import EmployeeCreationForm
    import json

    total_employees = CustomUser.objects.filter(role='Employee', is_active=True).count()
    total_departments = Department.objects.count()
    completed_exits = Resignation.objects.filter(admin_status='Approved').count()
    assets_pending = Asset.objects.exclude(status='Returned').count()
    pending_admin = Resignation.objects.filter(hr_status='Approved', admin_status='Pending').count()

    status_counts = {
        'In Progress': Resignation.objects.exclude(admin_status='Approved').exclude(
            manager_status='Rejected').exclude(hr_status='Rejected').exclude(admin_status='Rejected').count(),
        'Successfully Exited': completed_exits,
    }

    # Department breakdown
    departments = Department.objects.all()
    dept_data = []
    for dept in departments:
        dept_data.append({
            'name': dept.name,
            'count': dept.employees.filter(is_active=True).count()
        })

    # Employee Management
    employees = CustomUser.objects.filter(role='Employee').select_related('department').order_by('-id')
    employee_form = EmployeeCreationForm()

    return render(request, 'accounts/dashboards/admin_dashboard.html', {
        'total_employees': total_employees,
        'total_departments': total_departments,
        'completed_exits': completed_exits,
        'assets_pending': assets_pending,
        'pending_approvals': pending_admin,
        'chart_labels': json.dumps(list(status_counts.keys())),
        'chart_data': json.dumps(list(status_counts.values())),
        'dept_labels': json.dumps([d['name'] for d in dept_data]),
        'dept_data': json.dumps([d['count'] for d in dept_data]),
        'employees': employees,
        'employee_form': employee_form,
    })


@login_required
def employee_create(request):
    from django.contrib import messages
    from accounts.forms import EmployeeCreationForm
    if request.user.role not in ['HR', 'Admin']:
        return redirect('dashboard_redirect')
    
    if request.method == 'POST':
        form = EmployeeCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Auto-assign default assets
            from assets.models import Asset
            Asset.objects.create(
                name="MacBook Pro 14-inch (Staff)",
                assigned_to=user,
                status="Issued"
            )
            Asset.objects.create(
                name="Employee ID & Access Card",
                assigned_to=user,
                status="Issued"
            )
            
            messages.success(request, f'Employee {user.full_name} created with base assets assigned successfully.')
        else:
            messages.error(request, 'Error creating employee account. Please check the form.')
    return redirect(request.META.get('HTTP_REFERER', 'dashboard_redirect'))


@login_required
def employee_edit(request, pk):
    from django.contrib import messages
    from django.shortcuts import get_object_or_404
    from accounts.models import CustomUser
    from accounts.forms import EmployeeEditForm
    if request.user.role != 'Admin':
        messages.error(request, 'Only Administrators can edit employee profiles.')
        return redirect('dashboard_redirect')
    
    employee = get_object_or_404(CustomUser, pk=pk, role='Employee')
    if request.method == 'POST':
        form = EmployeeEditForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, f'Employee {employee.full_name} updated successfully.')
        else:
            messages.error(request, 'Error updating employee.')
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))


@login_required
def employee_toggle_status(request, pk):
    from django.contrib import messages
    from django.shortcuts import get_object_or_404
    from accounts.models import CustomUser
    if request.user.role != 'Admin':
        messages.error(request, 'Only Administrators can deactivate/reactivate employees.')
        return redirect('dashboard_redirect')
    
    if request.method == 'POST':
        employee = get_object_or_404(CustomUser, pk=pk, role='Employee')
        employee.is_active = not employee.is_active
        employee.save()
        status = "reactivated" if employee.is_active else "deactivated"
        messages.success(request, f'Employee account {status} successfully.')
    return redirect(request.META.get('HTTP_REFERER', 'admin_dashboard'))


@login_required
def team_projects(request):
    from accounts.models import Project, CustomUser
    from django.contrib import messages
    from django.db.models import Q
    if request.user.role != 'Manager':
        return redirect('dashboard_redirect')

    if request.method == 'POST':
        name = request.POST.get('name')
        assigned_to_id = request.POST.get('assigned_to')
        status = request.POST.get('status', 'Ongoing')
        
        if name and assigned_to_id:
            try:
                assignee = CustomUser.objects.get(pk=assigned_to_id, department=request.user.department)
                Project.objects.create(
                    name=name,
                    assigned_to=assignee,
                    department=request.user.department,
                    status=status
                )
                messages.success(request, f'Project "{name}" assigned successfully to {assignee.full_name}.')
            except CustomUser.DoesNotExist:
                messages.error(request, 'Invalid employee selected.')
        else:
            messages.error(request, 'Please provide project name and assignee.')
        return redirect('team_projects')

    projects = Project.objects.filter(
        department=request.user.department
    ).select_related('assigned_to') if request.user.department else Project.objects.none()

    status_filter = request.GET.get('status', '').strip()
    if status_filter in ['Ongoing', 'Pending', 'Completed']:
        projects = projects.filter(status=status_filter)

    search_query = request.GET.get('search', '').strip()
    if search_query:
        projects = projects.filter(
            Q(assigned_to__full_name__icontains=search_query) | 
            Q(assigned_to__email__icontains=search_query)
        )

    ongoing_count = Project.objects.filter(department=request.user.department, status='Ongoing').count() if request.user.department else 0
    pending_count = Project.objects.filter(department=request.user.department, status='Pending').count() if request.user.department else 0
    completed_count = Project.objects.filter(department=request.user.department, status='Completed').count() if request.user.department else 0

    team_members = CustomUser.objects.filter(
        department=request.user.department,
        role='Employee',
        is_active=True
    ).exclude(pk=request.user.pk) if request.user.department else []

    return render(request, 'accounts/team_projects.html', {
        'projects': projects,
        'status_filter': status_filter,
        'search_query': search_query,
        'ongoing_count': ongoing_count,
        'pending_count': pending_count,
        'completed_count': completed_count,
        'team_members': team_members,
    })


@login_required
def project_toggle_status(request, pk):
    from django.contrib import messages
    from django.shortcuts import get_object_or_404
    from accounts.models import Project

    if request.user.role != 'Manager':
        messages.error(request, 'Only Managers can update project status.')
        return redirect('dashboard_redirect')
    
    project = get_object_or_404(Project, pk=pk, department=request.user.department)
    
    if request.method == 'POST':
        if project.status == 'Ongoing':
            project.status = 'Completed'
        else:
            project.status = 'Ongoing'
        project.save()
        messages.success(request, f'Project "{project.name}" marked as {project.status}.')
        
    return redirect('team_projects')
