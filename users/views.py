from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.views.generic import CreateView, TemplateView, UpdateView, View

from users.forms import CustomUserCreationForm, EmailAuthenticationForm, ProfileUpdateForm
from users.models import CustomUser
from users.services import send_verification_email


class SignUpView(CreateView):
    template_name = 'users/signup.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('users:login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.is_email_verified = False
        user.save()
        send_verification_email(self.request, user)
        messages.success(
            self.request,
            'Аккаунт создан. Проверьте email и подтвердите регистрацию.',
        )
        return super().form_valid(form)


class EmailVerificationView(View):
    def get(self, request, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
            user = None

        if user and default_token_generator.check_token(user, token):
            user.is_active = True
            user.is_email_verified = True
            user.save(update_fields=['is_active', 'is_email_verified'])
            messages.success(request, 'Email подтвержден. Можете войти в систему.')
            return redirect('users:login')

        messages.error(request, 'Не удалось подтвердить email. Ссылка недействительна.')
        return redirect('users:login')


class UserLoginView(LoginView):
    template_name = 'users/login.html'
    authentication_form = EmailAuthenticationForm


class UserLogoutView(LogoutView):
    next_page = reverse_lazy('home')


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    template_name = 'users/profile_edit.html'
    form_class = ProfileUpdateForm
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Профиль обновлен.')
        return super().form_valid(form)
