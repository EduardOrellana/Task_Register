from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    path('login/', views.loginView, name='loginView'),
    path('logout/', views.logoutView, name='logoutView'),
    path('tasks/', views.tasksView, name='tasksView'),
    path('tasks/create/', views.createTasks, name='createTasks'),
    path('tasks/<int:task_id>/', views.taskDetails, name='taskDetails'),
    path('tasks/<int:task_id>/edit/', views.editTask,
         name='editTask'),
    # New line added for edit task view
    path('tasks/<int:task_id>/delete/', views.deleteTask, name='deleteTask'),
    # New line added for edit profile view
    path('profile/edit/', views.editProfile, name='editProfile'),
]
