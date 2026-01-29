from django.shortcuts import render,redirect
from django.contrib.auth import login
from .forms import UserRegistrationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()

            user.profile.role = form.cleaned_data['role']
            user.profile.save()

            login(request,user)
            return redirect('accounts:dashboard')

    else:
        form = UserRegistrationForm()
    return render(request,'accounts/register.html',{'form':form})



class UserLoginView(LoginView):
    template_name = 'accounts/login.html'

class UserLogoutView(LogoutView):
    next_page = 'accounts:login'

@login_required
def dashboard(request):
    role = request.user.profile.role
    return render(request,'accounts/dashboard.html',{'profile':request.user.profile})


