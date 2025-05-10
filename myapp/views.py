from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from .models import Chairman, Coordinator, Intern, InternReport, SectionUpdate, Assessment, Section,Portfolio

def intern_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            intern = Intern.objects.get(username=username, password=password)
            request.session['intern_id'] = intern.id  # Save intern ID in session
            return redirect('intern_dashboard')
        except Intern.DoesNotExist:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'analyzer_app/intern_login.html')

def coordinator_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            coordinator = Coordinator.objects.get(username=username, password=password)
            request.session['coordinator_id'] = coordinator.id  # Save coordinator ID in session
            return redirect('coordinator_dashboard')
        except Coordinator.DoesNotExist:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'analyzer_app/coordinator_login.html')

def chairman_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        try:
            chairman = Chairman.objects.get(username=username, password=password)
            request.session['chairman_id'] = chairman.id  # Save chairman ID in session
            return redirect('chairman_dashboard')
        except Chairman.DoesNotExist:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'analyzer_app/chairman_login.html')

def coordinator_register_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        address = request.POST.get('address')
        contact_number = request.POST.get('contact_number')
        password = request.POST.get('password')

        # Check if username or email already exists
        if Coordinator.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif Coordinator.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        else:
            Coordinator.objects.create(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                address=address,
                contact_number=contact_number,
                password=password  # For production, hash the password!
            )
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('coordinator_login')

    return render(request, 'analyzer_app/coordinator_register.html')

def chairman_register_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        address = request.POST.get('address')
        contact_number = request.POST.get('contact_number')
        password = request.POST.get('password')

        # Check if username or email already exists
        if Chairman.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        elif Chairman.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
        else:
            Chairman.objects.create(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                address=address,
                contact_number=contact_number,
                password=password  # For production, hash the password!
            )
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('chairman_login')

    return render(request, 'analyzer_app/chairman_register.html')

def chairman_dashboard_view(request):
    chairman = None
    coordinators = {}
    if 'chairman_id' in request.session:
        chairman = Chairman.objects.get(id=request.session['chairman_id'])
        coordinators = Coordinator.objects.all().order_by('last_name')
    context = {
        'chairman': chairman,
        'coordinators': coordinators,
        # Add other context as needed
    }
    return render(request, 'analyzer_app/chairman_dashboard.html', context)

def coordinator_dashboard_view(request):
    coordinator = None
    interns = Intern.objects.all().order_by('section', 'last_name')
    context = {
        'coordinator': coordinator,
        'interns': interns,
    }
    return render(request, 'analyzer_app/coordinator_dashboard.html', context)

def chairman_logout_view(request):
    logout(request)
    return redirect('chairman_login')

def coordinator_logout_view(request):
    logout(request)
    return redirect('coordinator_login')

def intern_logout_view(request):
    logout(request)
    return redirect('intern_login')

def interns_reports_view(request):
    # Add your logic here
    return render(request, 'analyzer_app/interns_reports.html')

def intern_register_view(request):
    if request.method == 'POST':
        first_name = request.POST.get('firstname')
        last_name = request.POST.get('lastname')
        username = request.POST.get('username')
        password = request.POST.get('password')
        section = request.POST.get('section')
        coordinator_id = request.POST.get('coordinator')

        # Check for duplicate username
        if Intern.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
        else:
            coordinator = Coordinator.objects.get(id=coordinator_id)
            Intern.objects.create(
                username=username,
                password=password,
                first_name=first_name,
                last_name=last_name,
                section=section,
                coordinator=coordinator
            )
            messages.success(request, 'Intern registered successfully!')
            return redirect('intern_register')

    coordinators = Coordinator.objects.all()
    return render(request, 'analyzer_app/intern_register.html', {'coordinators': coordinators})

def intern_dashboard_view(request):
    intern = None
    if 'intern_id' in request.session:
        intern = Intern.objects.get(id=request.session['intern_id'])
    if request.method == 'POST':
        week = request.POST.get('week')
        date = request.POST.get('date')
        hours = request.POST.get('hours')
        activities = request.POST.get('activities')
        score = request.POST.get('score')
        new_learnings = request.POST.get('new_learnings')
        InternReport.objects.create(
            intern=intern,
            week=week,
            date=date,
            hours=hours,
            activities=activities,
            score=score,
            new_learnings=new_learnings
        )
        messages.success(request, 'Report submitted successfully!')
        return redirect('intern_dashboard')
    context = {'intern': intern}
    return render(request, 'analyzer_app/intern_dashboard.html', context)

@csrf_exempt  # Only use this if you have CSRF issues with fetch; otherwise, handle CSRF properly!
def add_week_report_view(request):
    if request.method == 'POST':
        intern = None
        if 'intern_id' in request.session:
            intern = Intern.objects.get(id=request.session['intern_id'])
        week = request.POST.get('week')
        date = request.POST.get('date')
        hours = request.POST.get('hours')
        activities = request.POST.get('activities')
        score = request.POST.get('score')
        new_learnings = request.POST.get('learnings')  # JS uses 'learnings' as the field name

        InternReport.objects.create(
            intern=intern,
            week=week,
            date=date,
            hours=hours,
            activities=activities,
            score=score,
            new_learnings=new_learnings
        )
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

def get_week_reports_view(request):
    if 'intern_id' in request.session:
        intern = Intern.objects.get(id=request.session['intern_id'])
        reports = InternReport.objects.filter(intern=intern)
        data = {}
        for report in reports:
            week = report.week
            if week not in data:
                data[week] = []
            data[week].append({
                'date': str(report.date),
                'hours': float(report.hours),
                'activities': report.activities,
                'score': report.score,
                'new_learnings': report.new_learnings,
            })
        return JsonResponse({'weeks': list(data.keys()), 'reports': data})
    return JsonResponse({'error': 'Not authenticated'}, status=403)

def coordinator_sections_view(request):
    if 'coordinator_id' in request.session:
        coordinator_id = request.session['coordinator_id']
        interns = Intern.objects.filter(coordinator_id=coordinator_id)
        sections = {}
        for intern in interns:
            if intern.section not in sections:
                sections[intern.section] = []
            sections[intern.section].append({
                'first_name': intern.first_name,
                'last_name': intern.last_name,
                'username': intern.username,
            })
        return JsonResponse({'sections': sections})
    return JsonResponse({'error': 'Not authenticated'}, status=403)

def coordinator_submissions_view(request):
    if 'coordinator_id' in request.session:
        coordinator = Coordinator.objects.get(id=request.session['coordinator_id'])
        interns = Intern.objects.filter(coordinator=coordinator).order_by('section', 'last_name')
        # Build a dict: {intern_id: latest_report}
        latest_reports = {}
        for intern in interns:
            report = InternReport.objects.filter(intern=intern).order_by('-date').first()
            latest_reports[intern.id] = report
        context = {
            'interns': interns,
            'latest_reports': latest_reports,
        }
        return render(request, 'analyzer_app/coordinator_submissions.html', context)
    return redirect('coordinator_login')

@require_POST
def add_rating_view(request, report_id):
    rating = request.POST.get('rating')
    try:
        report = InternReport.objects.get(id=report_id)
        report.score = rating
        report.save()
    except InternReport.DoesNotExist:
        pass
    return redirect('coordinator_submissions')

def coordinator_student_reports_view(request):
    if 'coordinator_id' in request.session:
        coordinator = Coordinator.objects.get(id=request.session['coordinator_id'])
        interns = Intern.objects.filter(coordinator=coordinator).order_by('section', 'last_name')
        return render(request, 'analyzer_app/coordinator_student_reports.html', {'interns': interns})
    return redirect('coordinator_login')

def coordinator_student_detail_view(request, intern_id):
    intern = Intern.objects.get(id=intern_id)
    # Sort by week (ascending), then by date (ascending)
    reports = InternReport.objects.filter(intern=intern).order_by('week', 'date')
    return render(request, 'analyzer_app/coordinator_student_detail.html', {'intern': intern, 'reports': reports})

def coordinator_submit_update_view(request):
    if 'coordinator_id' in request.session:
        coordinator = Coordinator.objects.get(id=request.session['coordinator_id'])
        # Get unique sections from the coordinator's interns
        sections = (
            coordinator.interns.values_list('section', flat=True)
            .distinct()
            .order_by('section')
        )
        return render(request, 'analyzer_app/coordinator_submit_update.html', {
            'coordinator': coordinator,
            'sections': sections,
        })
    return redirect('coordinator_login')

def chairman_coordinator_detail_view(request, coordinator_id):
    coordinator = Coordinator.objects.get(id=coordinator_id)
    section_updates = SectionUpdate.objects.filter(coordinator=coordinator).order_by('-submitted_at')
    assessments = Assessment.objects.filter(coordinator=coordinator).order_by('-week')
    interns = Intern.objects.filter(coordinator=coordinator).order_by('last_name')  # Only interns under this coordinator
    return render(request, 'analyzer_app/chairman_coordinator_detail.html', {
        'coordinator': coordinator,
        'section_updates': section_updates,
        'assessments': assessments,
        'interns': interns,
    })

def test_session_view(request):
    request.session['test_key'] = 'test_value'
    return HttpResponse("Session test complete")

def portfolio_analysis_view(request, intern_id):
    intern = Intern.objects.get(id=intern_id)
    portfolio = Portfolio.objects.get(intern=intern)
    rating = portfolio.rating  # or however you store the analysis
    graphs_data = ...  # Prepare your skills data as JSON
    return render(request, 'analyzer_app/portfolio_analysis.html', {
        'portfolio': portfolio,
        'rating': rating,
        'graphs_data': graphs_data,
    })
