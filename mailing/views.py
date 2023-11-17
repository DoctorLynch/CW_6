from random import sample
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, CreateView, DetailView, DeleteView, UpdateView
from blog.models import BlogPost
from .models import Mailing, Client, Message, Log
from .forms import MailingForm, MessageForm, ClientForm


class HomeView(TemplateView):
    template_name = 'mailing/home.html'
    extra_context = {
        'title': 'Главная страница',
    }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['count_mailing'] = len(Mailing.objects.all())
        active_mailings_count = Mailing.objects.filter(status__in=['created', 'started']).count()
        context['active_mailings_count'] = active_mailings_count
        unique_clients_count = Client.objects.filter(is_active=True).distinct().count()
        context['unique_clients_count'] = unique_clients_count
        all_posts = list(BlogPost.objects.all())
        context['random_blog_posts'] = sample(all_posts, min(3, len(all_posts)))
        context['object_list'] = Mailing.objects.all()
        user = self.request.user
        user_group_names = [group.name for group in user.groups.all()]
        context['user_group_names'] = user_group_names
        return context


class MailingListView(ListView):
    model = Mailing
    template_name = 'mailing/mailing_list.html'
    context_object_name = 'mailings'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_group_names = [group.name for group in user.groups.all()]
        context['user_group_names'] = user_group_names
        return context


class MailingCreateView(LoginRequiredMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailing/create_mailing.html'

    def form_valid(self, form):
        new_mailing = form.save()
        new_mailing.owner = self.request.user
        new_mailing.save()
        self.mailing_pk = new_mailing.pk
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_success_url(self):
        return reverse_lazy('mailing:create_message', kwargs={'mailing_pk': self.mailing_pk})


class MailingUpdateView(LoginRequiredMixin, UpdateView):
    model = Mailing
    fields = ('start_time', 'frequency', 'recipients', 'status')
    success_url = reverse_lazy('mailing:mailing')

    def form_valid(self, form):
        if form.is_valid():
            new_mailing = form.save()
            new_mailing.owner = self.request.user
            new_mailing.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['initial'] = {'user': self.request.user}
        return kwargs

    def get_object(self, queryset=None):
        mailing = super().get_object(queryset)
        mailing = get_object_or_404(Mailing, id=mailing.pk)
        user_groups = [group.name for group in self.request.user.groups.all()]
        if mailing.owner != self.request.user and 'Managers' not in user_groups:
            raise Http404
        return mailing


class MailingDetailView(DetailView):
    model = Mailing
    template_name = 'mailing/mailing_detail.html'
    context_object_name = 'mailing'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = Message.objects.filter(mailing=self.object)
        return context


class MailingDeleteView(LoginRequiredMixin, DeleteView):
    model = Mailing
    success_url = reverse_lazy('mailing:mailing')
    extra_context = {
        'title': 'Удаление записи:'
    }

    def get_object(self, queryset=None):
        mailing = super().get_object(queryset)
        mailing = get_object_or_404(Mailing, id=mailing.pk)
        user_groups = [group.name for group in self.request.user.groups.all()]
        if mailing.owner != self.request.user and 'Managers' not in user_groups:
            raise Http404
        return mailing


class ClientListView(ListView):
    model = Client
    template_name = 'mailing/client_list.html'
    context_object_name = 'clients'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_group_names = [group.name for group in user.groups.all()]
        context['user_group_names'] = user_group_names
        return context


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    success_url = reverse_lazy('mailing:mailing')
    raise_exception = True

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(object_list=None, **kwargs)
        data['title'] = "Создание нового клиента."
        return data

    def form_valid(self, form):
        self.object = form.save()
        self.object.owner = self.request.user
        self.object.save()
        return super().form_valid(form)


class MessageCreateView(LoginRequiredMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailing/create_message.html'
    success_url = reverse_lazy('mailing:mailing')

    def form_valid(self, form):
        mailing = get_object_or_404(Mailing, pk=self.kwargs['mailing_pk'])
        message = form.save(commit=False)
        message.mailing = mailing
        message.save()
        return super().form_valid(form)


class DeliveryReportView(ListView):
    model = Log
    template_name = 'mailing/delivery_report.html'
    context_object_name = 'delivery_logs'

    def get_queryset(self):
        return Log.objects.filter(status='success')