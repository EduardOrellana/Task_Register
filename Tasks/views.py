from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
# using the built-in user model user for authentication from Django
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, authenticate, logout
from .models import Task
from .forms import TaskForm, TaskEditForm, EditProfileForm


# Create your views here.
def signup(request):
    # validate what kind of request it is (POST or GET)
    # lowercase method to get the type of request

    if request.method == 'GET':
        return render(request, 'signup.html', {'form': UserCreationForm()})
    else:
        # validate the data from the form
        form = UserCreationForm(request.POST)

        if form.is_valid():
            try:
                # create the user in the database
                user = User.objects.create_user(
                    username=request.POST['username'].lower(),
                    password=request.POST['password1']
                )
                user.save()
                # log the user in and the cookie session
                login(request, user)
                return redirect(home)

            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm(),
                    'error': 'Username already taken. Please choose a new username.'
                })
            except Exception as e:
                return render(request, 'signup.html', {
                    'form': UserCreationForm(),
                    'error': f'An error occurred: {str(e)}'
                })
        else:
            return render(request, 'signup.html', {
                'form': UserCreationForm(),
                'error': 'Passwords do not match.'
            })


def home(request):
    return render(request, 'home.html')

# profile section


def profile(request):
    if not request.user.is_authenticated:
        return redirect('loginView')
    else:
        return render(request, 'profile/profile.html', {'username': request.user.username})


def editProfile(request):
    if not request.user.is_authenticated:
        return redirect('loginView')
    else:
        if request.method == 'GET':
            user = User.objects.get(pk=request.user.id)
            form = EditProfileForm(instance=user)
            return render(request, 'profile/editProfile.html', {'form': form})
        else:
            new_username = request.POST.get('username', '').lower()
            if new_username:
                try:
                    request.user.username = new_username
                    request.user.email = request.POST.get('email', '')
                    request.user.first_name = request.POST.get(
                        'first_name', '')
                    request.user.last_name = request.POST.get('last_name', '')
                    request.user.save()
                    return redirect('profile')
                except IntegrityError:
                    return render(request, 'profile/editProfile.html', {
                        'username': request.user.username,
                        'error': 'Username already taken. Please choose a new username.'
                    })
            else:
                return render(request, 'profile/editProfile.html', {
                    'username': request.user.username,
                    'error': 'Username cannot be empty.'
                })


def loginView(request):
    if request.method == 'GET':
        return render(request, 'login.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(
            request,
            username=request.POST['username'].lower(),
            password=request.POST['password']
        )
        if user is None:
            return render(request, 'login.html', {
                'form': AuthenticationForm(),
                'error': 'Username or password is incorrect.'
            })
        else:
            login(request, user)
            return redirect('profile')


def logoutView(request):
    logout(request)
    return redirect('home')


def tasksView(request):
    if not request.user.is_authenticated:
        return redirect('loginView')
    else:

        filter_type = request.GET.get('filter', 'all')

        if filter_type == 'pending':
            tasks = get_object_or_404(
                User, pk=request.user.id).task_set.filter(completed=False)
        elif filter_type == 'completed':
            tasks = get_object_or_404(
                User, pk=request.user.id).task_set.filter(completed=True)
        else:
            tasks = get_object_or_404(User, pk=request.user.id).task_set.all()
        return render(request, 'tasks/tasksView.html', {'tasks': tasks})


def createTasks(request):
    if not request.user.is_authenticated:
        return redirect('loginView')
    else:
        if request.method == 'GET':
            return render(request, 'tasks/createTask.html', {'form': TaskForm()})
        else:
            try:
                form = TaskForm(request.POST)
                new_task = form.save(commit=False)
                new_task.user = request.user
                new_task.save()
                return redirect('tasksView')
            except ValueError:
                return render(request, 'createTasks.html', {
                    'form': TaskForm(),
                    'error': 'Please provide valid data.'
                })


def taskDetails(request, task_id):
    if not request.user.is_authenticated:
        return redirect('loginView')
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            # form = TaskForm(instance=task)
            return render(request, 'tasks/taskDetail.html', {'task': task})
        except Task.DoesNotExist:
            return HttpResponse('Task not found or you do not have permission to view it.', status=404)


def editTask(request, task_id):
    if not request.user.is_authenticated:
        return redirect('loginView')
    else:
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        if request.method == 'GET':
            form = TaskEditForm(instance=task)
            return render(request, 'tasks/editTask.html', {'form': form, 'task': task})
        else:
            try:
                form = TaskEditForm(request.POST, instance=task)
                task = form.save(commit=False)

                # if the user marks the task as completed, set the datecompleted
                if task.completed and task.datecompleted is None:
                    from django.utils import timezone
                    task.datecompleted = timezone.now()

                if not task.completed:
                    task.datecompleted = None

                task.save()
                return redirect('taskDetails', task_id=task.id)
            except ValueError:
                return render(request, 'tasks/editTask.html', {
                    'form': form,
                    'task': task,
                    'error': 'Please provide valid data.'
                })


def deleteTask(request, task_id):
    if not request.user.is_authenticated:
        return redirect('loginView')
    else:
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        if request.method == 'POST':
            task.delete()
            return redirect('tasksView')
        else:
            return render(request, 'tasks/editTask.html', {'task': task})
