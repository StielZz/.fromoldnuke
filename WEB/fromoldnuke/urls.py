from django.contrib import admin
from django.urls import path
from projects import views

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('dashboard/download_projects/', views.download_projects_view, name='download_projects'),
    path('dashboard/join_project/', views.join_project_view, name='join_project'),
    path('dashboard/create_project/', views.create_project_view, name='create_project'),
    path('dashboard/project/<int:project_id>/', views.project_detail_view, name='project_detail'),
]