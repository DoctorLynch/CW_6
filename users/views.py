import random
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView
from users.forms import UserRegisterForm, UserProfileForm
from users.models import User


class RegisterView(CreateView):
    model = User
    form_class = UserRegisterForm
    template_name = 'users/register.html'

    def get_success_url(self):
        return reverse('users:verify_email', kwargs={'email': self.object.email})

    def form_valid(self, form):
        self.object = form.save()
        if form.is_valid():
            verification_code = ''.join([str(random.randint(0, 9)) for _ in range(12)])
            self.object.verify_code = verification_code
            self.object.is_active = False
            self.object.save()
            send_mail(
                subject='Поздравляем с регистрацией',
                message=f'Вы зарегистрировались на нашей платформе, ваш код авторизации {verification_code}',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[self.object.email],
            )
        return super().form_valid(form)


class ProfileView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileForm
    success_url = reverse_lazy('users:profile')

    def get_object(self, queryset=None):
        return self.request.user


@login_required
def generate_new_password(request):
    new_password = ''.join([str(random.randint(0, 9)) for _ in range(12)])
    send_mail(
        subject='Вы сменили пароль',
        message=f'Ващ новый пароль: {new_password}',
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[request.user.email]
    )
    request.user.set_password(new_password)
    request.user.save()
    return redirect(reverse('shop:list'))


def verify_email(request, email):
    if request.method == 'POST':
        code = request.POST.get('user-code')
        user = User.objects.get(email=email)
        if user.verify_code == code:
            user.is_active = True
            user.save()
            return redirect(reverse('shop:list'))
    return render(request, 'users/verification.html')
