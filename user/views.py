import os

from django.views import generic
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic.edit import UpdateView

from user.forms import SignUpForm, UserSettings
from user.models import User


class SignUpView(generic.CreateView):
    form_class = SignUpForm
    template_name = "user/signup.html"

    def get_success_url(self):
        redirect_to = self.request.POST['next']
        return redirect_to

    def get_context_data(self, **kwargs):
        context = super(SignUpView, self).get_context_data(**kwargs)
        context.update({'next': self.request.GET.get('next', '')})
        return context

    def post(self, request, *args, **kwargs):
        response = super(SignUpView, self).post(request, *args, **kwargs)
        form = self.get_form()

        if form.is_valid():
            new_user = form.save()
            new_user.avatar = form.cleaned_data['avatar']
            new_user.save()

            login(request, new_user, 'django.contrib.auth.backends.ModelBackend')
        return response


class SettingsView(LoginRequiredMixin, UpdateView):
    form_class = UserSettings
    model = User
    template_name = 'user/user_settings.html'

    def get_success_url(self):
        redirect_to = self.request.POST['next']
        return redirect_to

    def get_context_data(self, **kwargs):
        context = super(SettingsView, self).get_context_data(**kwargs)
        context.update({'next': self.request.GET.get('next', '')})
        if self.request.user.avatar:
            context.update({'file_name': os.path.basename(self.request.user.avatar.name)})
        else:
            context.update({'file_name': ''})

        return context

    def post(self, request, *args, **kwargs):
        response = super(SettingsView, self).post(request, *args, **kwargs)
        form = self.get_form()
        if form.is_valid():
            request.user.email = form.data['email']
            if form.data['avatar']:
                request.user.avatar = form.data['avatar']
            request.user.save()
        return response
