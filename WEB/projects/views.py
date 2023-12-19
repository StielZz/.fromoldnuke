from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from .models import *
from .forms import *
from django.utils import timezone
from datetime import datetime


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    error_message = None

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            error_message = 'Неправильное имя пользователя или пароль'

    return render(request, 'login.html', {'error_message': error_message})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = ExtendedUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')

    return render(request, 'register.html', {'form': "Проверьте правильность заполнения формы"})

def logout_view(request):
    logout(request) 
    return redirect('login')

def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    user = request.user
    user_projects = ProjectParticipants.objects.filter(id_user=user.id)

    search_query = request.GET.get('search_query', '')
    if search_query:
        projects = Projects.objects.filter(title__icontains=search_query) | Projects.objects.filter(skills__icontains=search_query)
    else:
        projects = list(participant.id_project for participant in user_projects)
    
    context = {
        'user': user,
        'projects': projects,
        'search_query': search_query,
    }

    return render(request, 'dashboard.html', context)

def download_projects_view(request):
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)

    projects = ProjectParticipants.objects.filter(id_user=request.user.id)
    
    projects_data = []
    for project in projects:
        projects_data.append(f"Название проекта: {project.id_project.title}")
        projects_data.append(f"Описание: {project.id_project.description}")
        projects_data.append(f"Скилы: {project.id_project.skills}")
        projects_data.append(f"Сроки: {project.id_project.start_date} - {project.id_project.end_date}")
        projects_data.append(f"Статус: {project.id_project.id_status.status_name}")
        projects_data.append("\n")

    content = "\n".join(projects_data)
    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="user_projects.txt"'

    return response

def project_detail_view(request, project_id):
    if not request.user.is_authenticated:
        return redirect('login')

    project = get_object_or_404(Projects, id_project=project_id)
    user = request.user.id
    participant = ProjectParticipants.objects.filter(id_project=project, id_user=user).first()
    user_role = participant.id_role if participant else None
    statuses = Statuses.objects.all()

    is_leader = user_role.role_name == 'Лидер'

    if request.method == 'POST':
        form = ChangeProjectInfoForm(request.POST)

        if form.is_valid():
            new_status = form.cleaned_data['new_status']
            new_description = form.cleaned_data['new_description']

            if new_status:
                project.id_status = new_status

            if new_description:
                project.description = new_description

            project.save(update_fields=['id_status', 'description'])

            if 'publish' in request.POST:
                published_status = Statuses.objects.get(status_name='Опубликован')
                project.id_status = published_status
                project.save(update_fields=['id_status'])

        if 'leave_project' in request.POST:
            if participant:
                participant.delete()

            return redirect('dashboard')
    else:
        form = ChangeProjectInfoForm(initial={'new_status': project.id_status, 'new_description': project.description})

    context = {
        'project': project,
        'user_role': user_role,
        'statuses': statuses,
        'form': form,
        'is_leader': is_leader,
    }

    return render(request, 'project_detail.html', context)

def join_project_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        project_id = request.POST.get('project')
        role_id = request.POST.get('role')

        project = get_object_or_404(Projects, id_project=project_id)
        role = get_object_or_404(Roles, id_role=role_id)
        user = get_object_or_404(AuthUser, id=request.user.id)

        ProjectParticipants.objects.create(id_project=project, id_user=user, id_role=role)

        return redirect('dashboard')

    user = request.user.id
    user_participated_project_ids = ProjectParticipants.objects.filter(id_user=user).values_list('id_project', flat=True)
    available_projects = Projects.objects.exclude(id_project__in=user_participated_project_ids)
    roles = Roles.objects.all()
    roles = Roles.objects.exclude(id_role=1)

    context = {
        'user': user,
        'available_projects': available_projects,
        'roles': roles,
    }

    return render(request, 'join_project.html', context)

def create_project_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        skills = request.POST.get('skills')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        start_date = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
        end_date = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%d'))

        proposed_status = Statuses.objects.get(status_name='Предложен')
        project = Projects.objects.create(
            title=title,
            description=description,
            skills=skills,
            start_date=start_date,
            end_date=end_date,
            id_status=proposed_status,
        )

        leader_role = Roles.objects.get(role_name='Лидер')
        
        user = get_object_or_404(AuthUser, id=request.user.id)
        ProjectParticipants.objects.create(
            id_project=project,
            id_user=user,
            id_role=leader_role,
        )

        return redirect('dashboard')

    return render(request, 'create_project.html')