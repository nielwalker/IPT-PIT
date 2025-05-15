from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from .models import Chairman, Coordinator, Intern, InternReport, SectionUpdate, Assessment ,Section, Portfolio
from .summary import summarize_intern_new_learning  # You need to create this function
from .po_rubrics import PO_RUBRICS
import json,re
from collections import Counter, defaultdict
from nltk.stem import PorterStemmer

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
    assessments = []
    coordinators = []
    section_coordinators = {}
    section_updates = []
    if 'chairman_id' in request.session:
        chairman = Chairman.objects.get(id=request.session['chairman_id'])
        assessments = Assessment.objects.all().order_by('-week')
        coordinators = Coordinator.objects.all().order_by('last_name')
        # ... your logic for section_coordinators and section_updates ...
    context = {
        'chairman': chairman,
        'assessments': assessments,
        'coordinators': coordinators,
        'section_coordinators': section_coordinators,
        'section_updates': section_updates,
    }
    return render(request, 'analyzer_app/chairman_dashboard.html', context)

def coordinator_dashboard_view(request):
    coordinator = None
    interns = []
    intern_reports = {}
    if 'coordinator_id' in request.session:
        coordinator = Coordinator.objects.get(id=request.session['coordinator_id'])
        interns = Intern.objects.filter(coordinator=coordinator).order_by('section', 'last_name')
        coordinator = Coordinator.objects.get(id=request.session['coordinator_id'])
        interns = Intern.objects.filter(coordinator=coordinator).order_by('section', 'last_name')
        for intern in interns:
            reports = InternReport.objects.filter(intern=intern).order_by('week')
            intern_reports[intern.id] = reports
    return render(request, 'analyzer_app/coordinator_dashboard.html', {
        'coordinator': coordinator,
        'interns': interns,
        'intern_reports': intern_reports,
    })

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
    if 'coordinator_id' in request.session:
        coordinator = Coordinator.objects.get(id=request.session['coordinator_id'])
        interns = Intern.objects.filter(coordinator=coordinator).order_by('section', 'last_name')
        return render(request, 'analyzer_app/coordinator_student_reports.html', {
            'interns': interns,
            'coordinator': coordinator,
        })
    return redirect('coordinator_login')

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
        # Gather all reports for each intern, sorted by week/date
        intern_reports = {}
        for intern in interns:
            reports = InternReport.objects.filter(intern=intern).order_by('week')  # or 'date'
            intern_reports[intern.id] = reports
        return render(request, 'analyzer_app/coordinator_submissions.html', {
            'coordinator': coordinator,
            'interns': interns,
            'intern_reports': intern_reports,
        })
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
    reports = InternReport.objects.filter(intern=intern).order_by('week')
    # Gather all new learnings
    all_learnings = " ".join([r.new_learnings for r in reports if r.new_learnings])
    # Prepare word frequency for the graph
    words = re.findall(r'\w+', all_learnings.lower())
    freq = Counter(words)
    top = freq.most_common(5)
    skills_data = {
        "labels": [w for w, _ in top],
        "data": [c for _, c in top]
    }
    return render(request, 'analyzer_app/coordinator_student_detail.html', {
        'intern': intern,
        'reports': reports,
        'summary': all_learnings if all_learnings.strip() else "No new learnings submitted.",
        'skills_data': json.dumps(skills_data),  # <-- Pass as JSON string
    })

def coordinator_submit_update_view(request):
    if 'coordinator_id' in request.session:
        coordinator = Coordinator.objects.get(id=request.session['coordinator_id'])
        # Get unique sections from the coordinator's interns
        sections = (
            coordinator.interns.values_list('section', flat=True)
            .distinct()
            .order_by('section')
        )
        if request.method == 'POST':
            section = request.POST.get('section')
            update_text = request.POST.get('update_text')
            # You must decide which intern and week this update is for
            # Example: assign to all interns in the section for a specific week
            interns = Intern.objects.filter(coordinator=coordinator, section=section)
            week = "Section Update"  # Or get from form if needed
            for intern in interns:
                Assessment.objects.create(
                    coordinator=coordinator,
                    intern=intern,
                    week=week,
                    assessment=update_text
                )
            messages.success(request, "Section update submitted as assessment(s)!")
            return redirect('coordinator_dashboard')
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

def coordinator_view_interns(request):
    if 'coordinator_id' in request.session:
        coordinator = Coordinator.objects.get(id=request.session['coordinator_id'])
        interns = Intern.objects.filter(coordinator=coordinator).order_by('section', 'last_name')
        return render(request, 'analyzer_app/coordinator_view_interns.html', {
            'coordinator': coordinator,
            'interns': interns,
        })
    return redirect('coordinator_login')

def coordinator_intern_summary_view(request):
    if 'coordinator_id' in request.session:
        coordinator = Coordinator.objects.get(id=request.session['coordinator_id'])
        interns = Intern.objects.filter(coordinator=coordinator).order_by('section', 'last_name')
        # Prepare summaries for each intern
        intern_summaries = {}
        for intern in interns:
            summary = summarize_intern_new_learning(intern.id)  # You will create this function
            intern_summaries[intern.id] = summary
        # Example: skills_data = {intern.id: {"labels": [...], "data": [...]} }
        skills_data = {}
        for intern in interns:
            # Example: get top 5 words from new learnings
            reports = InternReport.objects.filter(intern=intern)
            all_text = " ".join([r.new_learnings for r in reports if r.new_learnings])
            # Use your summary.py logic to get word frequencies
            from collections import Counter
            import re
            words = re.findall(r'\w+', all_text.lower())
            freq = Counter(words)
            top = freq.most_common(5)
            skills_data[intern.id] = {
                "labels": [w for w, _ in top],
                "data": [c for _, c in top]
            }
        # Pass skills_data to the template
        return render(request, 'analyzer_app/coordinator_interns_summary.html', {
            'coordinator': coordinator,
            'interns': interns,
            'intern_summaries': intern_summaries,
            'skills_data': skills_data,
        })
    return redirect('coordinator_login')

def coordinator_intern_summary(request, intern_id):
    intern = get_object_or_404(Intern, id=intern_id)
    reports = InternReport.objects.filter(intern=intern).order_by('week')
    all_learnings = " ".join([r.new_learnings for r in reports if r.new_learnings])
    return render(request, 'analyzer_app/coordinator_intern_summary.html', {
        'intern': intern,
        'all_learnings': all_learnings,
        'reports': reports,
    })

from .po_rubrics import PO_RUBRICS


def map_summary_to_po(summary):
    # Define keywords for each PO (customize as needed)
    PO_KEYWORDS = {
        "a": ["science", "mathematics", "critical", "creative thinking"],
        "b": ["best practices", "standards"],
        "c": ["analyze", "complex", "quantitative", "requirements"],
        "d": ["user needs", "evaluation", "administration"],
        "e": ["design", "implement", "evaluate", "components", "programs"],
        "f": ["integrate", "public health", "safety", "societal"],
        "g": ["adapt", "techniques", "tools", "limitations"],
        "h": ["collaboratively", "leader", "teams", "multidisciplinary"],
        "i": ["project plan"],
        "j": ["communicate", "oral", "written", "persuasively"],
        "k": ["impact", "organizations", "society"],
        "l": ["ethical", "legal", "security", "responsibilities"],
        "m": ["independent learning", "specialized field"],
        "n": ["generation", "knowledge", "research", "development"],
        "o": ["Filipino", "heritage", "culture"],
    }
    summary_lower = summary.lower()
    po_counts = {po: 0 for po in PO_RUBRICS}
    for po, keywords in PO_RUBRICS.items():
        for kw in keywords:
            # Count keyword occurrences
            po_counts[po] += len(re.findall(r'\b' + re.escape(kw.lower()) + r'\b', summary_lower))
    return po_counts


def coordinator_interns_summary_view(request):
    # Fetch interns associated with the coordinator
    if 'coordinator_id' in request.session:
        coordinator = Coordinator.objects.get(id=request.session['coordinator_id'])
        interns = Intern.objects.filter(coordinator=coordinator).order_by('section', 'last_name')
    else:
        return redirect('coordinator_login')

    intern_po_data = {}
    for intern in interns:
        reports = InternReport.objects.filter(intern=intern)
        all_learnings = " ".join([r.new_learnings for r in reports if r.new_learnings])
        po_counts = map_summary_to_po(all_learnings)
        intern_po_data[intern.id] = {
            "labels": list(PO_RUBRICS.keys()),
            "data": [po_counts[po] for po in PO_RUBRICS.keys()]
        }
    # Pass intern_po_data as skills_data
    return render(request, 'analyzer_app/coordinator_interns_summary.html', {
        # ... other context ...
        'skills_data': intern_po_data,  # This is a dict of dicts
    })

def summarize_intern_new_learning(intern_id):
    reports = InternReport.objects.filter(intern_id=intern_id)
    all_text = " ".join([report.new_learnings for report in reports if hasattr(report, 'new_learnings') and report.new_learnings])
    if not all_text.strip():
        return "No new learnings submitted."
    return all_text



def map_summary_to_po(summary):
    PO_RUBRICS = {
        "a": ["scienc", "scientif", "mathemat", "math", "algebra", "calculus", "critic", "analyt", "logic", "reason", "creativ", "innovat", "ideat"],
        
        "b": ["best", "practic", "convent", "standard", "protocol", "guidelin", "norm"],
        
        "c": ["analyz", "examin", "assess", "evalu", "inspect", "complex", "complic", "difficulti", "challeng", "quantit", "numer", "mathemat", "requir", "criteri", "specif"],
        
        "d": ["user", "need", "evalu", "assess", "review", "analysi", "administr", "manag", "supervis"],
        
        "e": ["design", "develop", "architect", "structur", "implement", "build", "creat", "evalu", "test", "review", "component", "modul", "element", "program", "system", "softwar"],
        
        "f": ["integr", "combin", "merg", "public", "health", "commun", "secur", "safeti", "well", "societ", "social"],
        
        "g": ["adapt", "adjust", "modifi", "custom", "techniqu", "method", "approach", "tool", "util", "applic", "limit", "constraint", "boundari"],
        
        "h": ["collabor", "togeth", "cooper", "coordin", "leader", "lead", "supervis", "manag", "team", "group", "squad", "multidisciplinari", "cross", "function"],
        
        "i": ["project", "plan", "schedul", "timeline", "roadmap", "mileston"],
        
        "j": ["communic", "convey", "express", "report", "share", "oral", "spoken", "verbal", "written", "textual", "document", "persuas", "convinc", "effect"],
        
        "k": ["impact", "effect", "influenc", "organ", "compani", "institut", "societi", "commun", "public"],
        
        "l": ["ethic", "moral", "principl", "legal", "law", "compliant", "secur", "protect", "safeti", "respons", "oblig", "duti"],
        
        "m": ["independ", "learn", "self", "studi", "autonom", "self", "pace", "special", "field", "domain", "knowledg", "expertis"],
        
        "n": ["generat", "creat", "produc", "knowledg", "inform", "insight", "research", "investig", "explor", "develop", "progress", "advanc"],
        
        "o": ["filipino", "philippin", "pinoy", "heritag", "tradit", "legaci", "cultur", "custom", "ident", "valu"]
    }
    summary_lower = summary.lower()
    po_counts = {po: 0 for po in PO_RUBRICS}
    for po, keywords in PO_RUBRICS.items():
        for kw in keywords:
            po_counts[po] += len(re.findall(r'\b' + re.escape(kw.lower()) + r'\b', summary_lower))
    return po_counts

def coordinator_student_detail(request, intern_id):
    from django.contrib.auth.models import User  # Add this import at the top of the file if not already present
    intern = get_object_or_404(User, id=intern_id)
    from .models import WeeklyJournal  # Ensure WeeklyJournal is imported
    journals = WeeklyJournal.objects.filter(student=intern)

    combined_text = " ".join(journal.new_learnings for journal in journals if journal.new_learnings)
    stemmer = PorterStemmer()
    words = [stemmer.stem(word.lower()) for word in combined_text.split()]

    PO_RUBRICS = {
        "a": ["scienc", "scientif", "mathemat", "math", "algebra", "calculus", "critic", "analyt", "logic", "reason", "creativ", "innovat", "ideat"],
        "b": ["best", "practic", "convent", "standard", "protocol", "guidelin", "norm"],
        "c": ["analyz", "examin", "assess", "evalu", "inspect", "complex", "complic", "difficulti", "challeng", "quantit", "numer", "mathemat", "requir", "criteri", "specif"],
        "d": ["user", "need", "evalu", "assess", "review", "analysi", "administr", "manag", "supervis"],
        "e": ["design", "develop", "architect", "structur", "implement", "build", "creat", "evalu", "test", "review", "component", "modul", "element", "program", "system", "softwar"],
        "f": ["integr", "combin", "merg", "public", "health", "commun", "secur", "safeti", "well", "societ", "social"],
        "g": ["adapt", "adjust", "modifi", "custom", "techniqu", "method", "approach", "tool", "util", "applic", "limit", "constraint", "boundari"],
        "h": ["collabor", "togeth", "cooper", "coordin", "leader", "lead", "supervis", "manag", "team", "group", "squad", "multidisciplinari", "cross", "function"],
        "i": ["project", "plan", "schedul", "timeline", "roadmap", "mileston"],
        "j": ["communic", "convey", "express", "report", "share", "oral", "spoken", "verbal", "written", "textual", "document", "persuas", "convinc", "effect"],
        "k": ["impact", "effect", "influenc", "organ", "compani", "institut", "societi", "commun", "public"],
        "l": ["ethic", "moral", "principl", "legal", "law", "compliant", "secur", "protect", "safeti", "respons", "oblig", "duti"],
        "m": ["independ", "learn", "self", "studi", "autonom", "self", "pace", "special", "field", "domain", "knowledg", "expertis"],
        "n": ["generat", "creat", "produc", "knowledg", "inform", "insight", "research", "investig", "explor", "develop", "progress", "advanc"],
        "o": ["filipino", "philippin", "pinoy", "heritag", "tradit", "legaci", "cultur", "custom", "ident", "valu"]
    }
    stem_to_pos = defaultdict(list)
    for po, stems in PO_RUBRICS.items():
        for stem in stems:
            stem_to_pos[stem].append(po)

    po_matches = defaultdict(int)
    total_matches = 0

    for word in words:
        matched_pos = stem_to_pos.get(word)
        if matched_pos:
            for po in matched_pos:
                po_matches[po] += 1
            total_matches += 1

    if total_matches == 0:
        po_percentages = {}
    else:
        po_percentages = {po: round((count / total_matches) * 100, 2) for po, count in po_matches.items()}

    graphs_data = {
        "labels": list(po_percentages.keys()),
        "data": list(po_percentages.values())
    }

    context = {
        "intern": intern,
        "journals": journals,
        "graphs_data": json.dumps(graphs_data)
    }
    return render(request, "coordinator/student_detail.html", context)

def student_detail_view(request, intern_id):
    intern = Intern.objects.get(id=intern_id)
    reports = InternReport.objects.filter(intern=intern)

    # Example: collect all new learnings text from reports
    all_new_learnings = " ".join(report.new_learnings for report in reports if report.new_learnings)
    
    # PO_RUBRICS imported from your po_rubrics.py
    from .po_rubrics import PO_RUBRICS

    # Simple keyword matching to count occurrences for each PO
    po_counts = {key: 0 for key in PO_RUBRICS.keys()}

    for key, desc in PO_RUBRICS.items():
        # For demo: count if PO key or description keywords appear in all_new_learnings (case insensitive)
        # You should improve this with better matching/stemming/lemmatization for accuracy
        if key.lower() in all_new_learnings.lower():
            po_counts[key] += 1

    # Prepare the graph data in the format your template expects
    graphs_data = {
        "labels": list(po_counts.keys()),
        "data": list(po_counts.values()),
    }

    # Summarize all new learnings text to display
    summary = all_new_learnings if all_new_learnings else None

    context = {
        "intern": intern,
        "reports": reports,
        "summary": summary,
        "graphs_data": json.dumps(graphs_data),  # <-- JSON string for the template
        "po_rubrics": PO_RUBRICS,
    }
    return render(request, "analyzer_app/coordinator_student_detail.html", context)

stemmer = PorterStemmer()

def map_summary_to_po(summary):
    summary_lower = summary.lower()
    words = re.findall(r'\b[a-z]+\b', summary_lower)
    stemmed_words = [stemmer.stem(word) for word in words]

    po_counts = {po: 0 for po in PO_RUBRICS}

    for po, stemmed_keywords in PO_RUBRICS.items():
        for keyword in stemmed_keywords:
            po_counts[po] += stemmed_words.count(keyword)

    return po_counts

def student_detail_view(request, intern_id):
    intern = Intern.objects.get(id=intern_id)
    reports = InternReport.objects.filter(intern=intern)
    all_new_learnings = " ".join(report.new_learnings for report in reports if report.new_learnings)
    from .po_rubrics import PO_RUBRICS
    po_counts = map_summary_to_po(all_new_learnings)
    total = sum(po_counts.values())
    if total > 0:
        po_percentages = {po: round((count / total) * 100, 2) for po, count in po_counts.items()}
    else:
        po_percentages = {po: 0 for po in po_counts}
    graphs_data = {
        "labels": list(po_counts.keys()),
        "data": [po_percentages[po] for po in po_counts.keys()],
    }
    summary = all_new_learnings if all_new_learnings else "No new learnings submitted."
    
    total = sum(po_counts.values())
    if total > 0:
        po_percentages = {po: round((count / total) * 100, 2) for po, count in po_counts.items()}
    else:
        po_percentages = {po: 0 for po in po_counts}

    context = {
        "intern": intern,
        "reports": reports,
        "summary": summary,
        "graphs_data": json.dumps(graphs_data),
        "po_rubrics": PO_RUBRICS,
        "po_percentages": po_percentages,
    }
    return render(request, "analyzer_app/coordinator_student_detail.html", context)

import json
import re
from django.shortcuts import render, get_object_or_404
from nltk.stem import PorterStemmer
from .models import Intern, InternReport  # Adjust model imports as needed

# Define your PO rubrics with stemmed keywords
PO_RUBRICS = {
    "a": ["scienc", "scientif", "mathemat", "math", "algebra", "calculus", "critic", "analyt", "logic", "reason", "creativ", "innovat", "ideat"],
    "b": ["best", "practic", "convent", "standard", "protocol", "guidelin", "norm"],
    "c": ["analyz", "examin", "assess", "evalu", "inspect", "complex", "complic", "difficulti", "challeng", "quantit", "numer", "mathemat", "requir", "criteri", "specif"],
    "d": ["user", "need", "evalu", "assess", "review", "analysi", "administr", "manag", "supervis"],
    "e": ["design", "develop", "architect", "structur", "implement", "build", "creat", "evalu", "test", "review", "component", "modul", "element", "program", "system", "softwar"],
    "f": ["integr", "combin", "merg", "public", "health", "commun", "secur", "safeti", "well", "societ", "social"],
    "g": ["adapt", "adjust", "modifi", "custom", "techniqu", "method", "approach", "tool", "util", "applic", "limit", "constraint", "boundari"],
    "h": ["collabor", "togeth", "cooper", "coordin", "leader", "lead", "supervis", "manag", "team", "group", "squad", "multidisciplinari", "cross", "function"],
    "i": ["project", "plan", "schedul", "timeline", "roadmap", "mileston"],
    "j": ["communic", "convey", "express", "report", "share", "oral", "spoken", "verbal", "written", "textual", "document", "persuas", "convinc", "effect"],
    "k": ["impact", "effect", "influenc", "organ", "compani", "institut", "societi", "commun", "public"],
    "l": ["ethic", "moral", "principl", "legal", "law", "compliant", "secur", "protect", "safeti", "respons", "oblig", "duti"],
    "m": ["independ", "learn", "self", "studi", "autonom", "self", "pace", "special", "field", "domain", "knowledg", "expertis"],
    "n": ["generat", "creat", "produc", "knowledg", "inform", "insight", "research", "investig", "explor", "develop", "progress", "advanc"],
    "o": ["filipino", "philippin", "pinoy", "heritag", "tradit", "legaci", "cultur", "custom", "ident", "valu"]
}

stemmer = PorterStemmer()

def map_summary_to_po(summary):
    summary_lower = summary.lower()
    words = re.findall(r'\b[a-z]+\b', summary_lower)
    stemmed_words = [stemmer.stem(word) for word in words]
    po_counts = {po: 0 for po in PO_RUBRICS}
    for po, keywords in PO_RUBRICS.items():
        for keyword in keywords:
            po_counts[po] += stemmed_words.count(keyword)
    return po_counts

def coordinator_student_detail(request, intern_id):
    intern = get_object_or_404(Intern, id=intern_id)
    reports = InternReport.objects.filter(intern=intern).order_by('week')
    # Summarize all new learnings
    all_new_learnings = " ".join([r.new_learnings for r in reports if r.new_learnings])
    summary = all_new_learnings if all_new_learnings else "No new learnings submitted."
    # Map summary to PO counts
    po_counts = map_summary_to_po(all_new_learnings)
    total = sum(po_counts.values())
    if total > 0:
        po_percentages = {po: round((count / total) * 100, 2) for po, count in po_counts.items()}
    else:
        po_percentages = {po: 0 for po in po_counts}
    # Prepare graph data
    graphs_data = {
        "labels": list(po_counts.keys()),
        "data": [po_percentages[po] for po in po_counts.keys()],
    }
    context = {
        "intern": intern,
        "reports": reports,
        "summary": summary,
        "graphs_data": json.dumps(graphs_data),
        "po_percentages": po_percentages,
    }
    return render(request, "analyzer_app/coordinator_student_detail.html", context)

from collections import defaultdict
import re
from django.utils.html import strip_tags

# Example PO keyword mapping (you can customize this)
PO_KEYWORDS = {
    'PO:A': ['design', 'system', 'model', 'develop'],
    'PO:B': ['analyze', 'data', 'problem', 'investigation'],
    'PO:C': ['communication', 'report', 'presentation', 'document'],
    'PO:D': ['ethics', 'responsibility', 'society'],
}

def extract_po_distribution(text):
    text = text.lower()
    word_counts = defaultdict(int)
    total_matches = 0

    for po, keywords in PO_KEYWORDS.items():
        for kw in keywords:
            matches = len(re.findall(r'\b{}\b'.format(re.escape(kw)), text))
            word_counts[po] += matches
            total_matches += matches

    # Convert counts to percentages
    po_percentages = {}
    for po, count in word_counts.items():
        if total_matches > 0:
            po_percentages[po] = round((count / total_matches) * 100, 2)
        else:
            po_percentages[po] = 0.0
    return po_percentages

def coordinator_student_detail_view(request, intern_id):
    intern = Intern.objects.get(id=intern_id)
    reports = InternReport.objects.filter(intern=intern).order_by('week', 'date')

    # Summarize all reports
    all_texts = ' '.join([strip_tags(report.activities + ' ' + report.new_learnings) for report in reports])
    summarized_text = all_texts[:500] + '...' if len(all_texts) > 500 else all_texts  # Simple summary

    po_distribution = extract_po_distribution(summarized_text)

    context = {
        'intern': intern,
        'reports': reports,
        'summary': summarized_text,
        'po_distribution': po_distribution,
    }
    return render(request, 'analyzer_app/coordinator_student_detail.html', context)