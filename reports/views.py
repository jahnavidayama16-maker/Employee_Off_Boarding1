from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.paginator import Paginator
from resignations.models import Resignation
from clearance.models import Clearance
from assets.models import Asset
import csv
import json


@login_required
def analytics_dashboard(request):
    if request.user.role != 'Admin':
        return redirect('home')

    resignations = Resignation.objects.all().select_related('employee', 'employee__department')

    # Date Filters
    start_date = request.GET.get('start_date', '').strip()
    end_date = request.GET.get('end_date', '').strip()
    dept_filter = request.GET.get('department', '').strip()

    if start_date:
        resignations = resignations.filter(expected_last_day__gte=start_date)
    if end_date:
        resignations = resignations.filter(expected_last_day__lte=end_date)
    if dept_filter:
        resignations = resignations.filter(employee__department__name=dept_filter)

    reasons_count = {}
    months_count = {}
    dept_count = {}

    for r in resignations:
        reason_short = r.reason[:30] + '...' if len(r.reason) > 30 else r.reason
        reasons_count[reason_short] = reasons_count.get(reason_short, 0) + 1

        month_label = r.expected_last_day.strftime('%b %Y')
        months_count[month_label] = months_count.get(month_label, 0) + 1

        dept_name = r.employee.department.name if r.employee.department else 'Unassigned'
        dept_count[dept_name] = dept_count.get(dept_name, 0) + 1

    # Department list for filter dropdown
    from accounts.models import Department
    departments = Department.objects.all().order_by('name')

    context = {
        'total_res': resignations.count(),
        'total_pending_hr': resignations.filter(hr_status='Pending', manager_status='Approved').count(),
        'total_assets_pending': Asset.objects.exclude(status='Returned').count(),
        'total_completed': resignations.filter(admin_status='Approved').count(),
        'reasons_labels': json.dumps(list(reasons_count.keys())),
        'reasons_data': json.dumps(list(reasons_count.values())),
        'months_labels': json.dumps(list(months_count.keys())),
        'months_data': json.dumps(list(months_count.values())),
        'dept_labels': json.dumps(list(dept_count.keys())),
        'dept_data': json.dumps(list(dept_count.values())),
        'start_date': start_date,
        'end_date': end_date,
        'dept_filter': dept_filter,
        'departments': departments,
    }
    return render(request, 'reports/analytics.html', context)


@login_required
def export_csv(request):
    if request.user.role != 'Admin':
        return HttpResponse('Unauthorized', status=401)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="microlent_offboarding_report.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Employee Name', 'Email', 'Department',
        'Current Stage', 'Expected Last Day',
        'Manager Status', 'HR Status', 'Admin Status',
        'All Assets Returned', 'Submitted On'
    ])

    completed_resignations = Resignation.objects.filter(
        admin_status='Approved'
    ).select_related('employee', 'employee__department').order_by('-created_at')

    for r in completed_resignations:
        assets_returned = not Asset.objects.filter(
            assigned_to=r.employee
        ).exclude(status='Returned').exists()
        writer.writerow([
            r.employee.full_name,
            r.employee.email,
            r.employee.department.name if r.employee.department else 'N/A',
            r.current_stage,
            r.expected_last_day,
            r.manager_status,
            r.hr_status,
            r.admin_status,
            'Yes' if assets_returned else 'No (Pending / Lost)',
            r.created_at.strftime('%Y-%m-%d %H:%M'),
        ])

    return response


@login_required
def audit_log(request):
    if request.user.role != 'Admin':
        return redirect('home')

    from reports.models import AuditLog

    # FIX: Added search + pagination — was loading ALL logs with no limit
    search_query = request.GET.get('q', '').strip()
    logs = AuditLog.objects.all().select_related('user').order_by('-timestamp')

    if search_query:
        from django.db.models import Q
        logs = logs.filter(
            Q(action__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(user__full_name__icontains=search_query)
        )

    paginator = Paginator(logs, 25)  # 25 per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'reports/audit_log.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'total_logs': logs.count(),
    })
