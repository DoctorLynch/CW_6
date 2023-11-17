from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, ListView, DetailView, UpdateView, DeleteView
from pytils.translit import slugify

from blog.models import BlogPost


class BlogPostCreateView(LoginRequiredMixin, CreateView):
    model = BlogPost
    fields = ('title', 'content', 'preview_image')
    success_url = reverse_lazy('blog:list')
    extra_context = {
        'title': 'Добавить новую запись:'
    }

    def form_valid(self, form):
        if form.is_valid():
            new_blog = form.save()
            new_blog.owner = self.request.user
            new_blog.slug = slugify(new_blog.title)
            new_blog.save()
        return super().form_valid(form)


class BlogPostListView(ListView):
    model = BlogPost
    extra_context = {
        'title': 'Последнии записи в блоге:'
    }

    def get_queryset(self, *args, **kwargs):
        queryset = BlogPost.objects.filter(is_published=True)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        user_group_names = [group.name for group in user.groups.all()]
        context['user_group_names'] = user_group_names
        return context


class BlogPostDetailView(DetailView):
    model = BlogPost

    def get_object(self, queryset=None):
        self.object = super().get_object(queryset)
        self.object.views_count += 1
        self.object.save()
        return self.object


class BlogPostUpdateView(LoginRequiredMixin, UpdateView):
    model = BlogPost
    fields = ('title', 'content', 'preview_image')
    extra_context = {
        'title': 'Редактировать запись:'
    }

    def form_valid(self, form):
        if form.is_valid():
            new_blog = form.save()
            new_blog.slug = slugify(new_blog.title)
            new_blog.save()
        return super().form_valid(form)

    def get_object(self, queryset=None):
        title = super().get_object(queryset)
        blog = get_object_or_404(BlogPost, title=title)
        user_groups = [group.name for group in self.request.user.groups.all()]
        if blog.owner != self.request.user and 'Managers' not in user_groups:
            raise Http404
        return blog

    def get_success_url(self):
        return reverse('blog:detail', args=[self.kwargs.get('slug')])


class BlogPostDeleteView(LoginRequiredMixin, DeleteView):
    model = BlogPost
    success_url = reverse_lazy('blog:list')
    extra_context = {
        'title': 'Удаление записи:'
    }

    def get_object(self, queryset=None):
        title = super().get_object(queryset)
        blog = get_object_or_404(BlogPost, title=title)
        user_groups = [group.name for group in self.request.user.groups.all()]
        if blog.owner != self.request.user and 'Managers' not in user_groups:
            raise Http404
        return blog
