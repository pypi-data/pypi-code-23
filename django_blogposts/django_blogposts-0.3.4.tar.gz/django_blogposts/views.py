# -*- coding: utf-8 -*-
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.http import Http404
from .models.blogpost import BlogPost
from .models.categories import Categories
from .models.tags import Tags
from django.conf import settings
from django.db.models import Q
__author__ = "spi4ka"


class PostsListView(ListView):

    queryset = BlogPost.objects.filter(is_moderated=True)

    paginate_by = 10

    template_name = "django_blogposts/list.html"

    def get_queryset(self):
        queryset = self.queryset
        if getattr(settings, 'BLOGPOSTS_USE_CATEGORIES', True):
            queryset = queryset.prefetch_related('category')

            queryset = queryset.filter(
                category__is_moderated=True
            )

            if self.kwargs.get('pk'):
                queryset = queryset.filter(
                    category__pk=self.kwargs.get('pk')
                )

        if getattr(settings, 'BLOGPOSTS_USE_TAGS', True):
            queryset = queryset.prefetch_related('tags')

            if self.request.GET.get('tag'):
                queryset = queryset.filter(
                    tags__is_moderated=True
                )

                queryset = queryset.filter(
                    tags__slug=self.request.GET.get('tag')
                )
            else:
                queryset = queryset.filter(
                    Q(tags__is_moderated=True) | Q(tags=None)
                )

        if self.request.GET.get('q'):
            queryset = queryset.filter(
                header__icontains=self.request.GET.get('q'),
            )

        return queryset.distinct().defer(
            'content', 'meta_title', 'meta_kw', 'meta_desc', 'de'
        )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        if self.kwargs.get('pk'):
            if getattr(settings, 'BLOGPOSTS_USE_CATEGORIES', True):
                try:
                    context['category'] = Categories.objects.get(
                        pk=self.kwargs.get('pk')
                    )
                except Categories.DoesNotExist:
                    pass

            if getattr(settings, 'BLOGPOSTS_USE_TAGS', True):
                context['tags'] = Tags.objects.filter(is_moderated=True)

        context['active_category'] = self.kwargs.get('pk')
        context['active_tag'] = self.request.GET.get('tag')
        return context


class PostsDetailView(DetailView):

    queryset = BlogPost.objects.filter(
        is_moderated=True
    ).select_related('category')

    template_name = "django_blogposts/detail.html"

    def get_object(self, *args, **kwargs):
        page = super().get_object(*args, **kwargs)
        try:
            if getattr(settings, 'BLOGPOSTS_USE_CATEGORIES', True):
                if not page.category.is_moderated:
                    raise Http404
        except:
            raise Http404
        return page
