from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render, redirect
from blog.models import Post, Page
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import Http404, HttpRequest, HttpResponse
from django.views.generic import ListView, DetailView

# Create your views here.


class PostListView(ListView):
    model = Post
    ordering = '-pk',
    template_name = 'blog/pages/index.html'
    # context_object_name = 'page_obj'
    paginate_by = 9
    queryset = Post.objects.get_published()

    # def get_queryset(self) -> QuerySet:
    #     query_set = super().get_queryset()
    #     query_set = query_set.filter(is_published=True)
    #     return query_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["title"] = 'Home - '
        return context


class CreatedByListView(PostListView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._temp_context = {}

    def get_queryset(self) -> QuerySet[Any]:
        qs = super().get_queryset()
        qs = qs.filter(created_by__pk=self._temp_context['author_pk'])
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        user = self._temp_context['user']

        user_full_name = user.username
        if user.first_name:
            user_full_name = f'{user.first_name} {user.last_name}'
        title = f'{user_full_name} post - '
        ctx.update({
            'title': title
        })
        return ctx

    def get(
            self, request: HttpRequest,
            *args: Any, **kwargs: Any
            ) -> HttpResponse:

        id = self.kwargs.get('id')
        user = User.objects.filter(pk=id).first()
        if user is None:
            raise Http404()

        self._temp_context.update({
            'author_pk': id,
            'user': user
        })
   
        return super().get(request, *args, **kwargs)


class CategoryListView(PostListView):
    # se False levanta um erro 404 se a pesquisa for vasia
    allow_empty = False

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(
            category__slug=self.kwargs.get('slug')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        title = f'{self.object_list[0].category.name} - '
        ctx.update({
            'title': title
        })
        return ctx
    

class TagListView(PostListView):
    # se False levanta um erro 404 se a pesquisa for vasia
    allow_empty = False

    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(
            tags__slug=self.kwargs.get('slug')
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        slug = self.kwargs.get("slug")
        title = f'{self.object_list[0].tags.filter(slug=slug).first()} - '
        ctx.update({
            'title': title
        })
        return ctx


class SearchListView(PostListView):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._search_value = ''

    def setup(self, request: HttpRequest, *args: Any, **kwargs: Any) -> None:
        self._search_value = request.GET.get('search','').strip()
        return super().setup(request, *args, **kwargs)

    def get_queryset(self):
        return super().get_queryset().filter(
            Q(title__icontains=self._search_value) |
            Q(exerpt__icontains=self._search_value) |
            Q(content__icontains=self._search_value)
        )[:9]

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx.update({
            'title': f'{self._search_value[:30]} - ',
            'search_value': self._search_value  
        })
        return ctx
    
    def get(self, request: HttpRequest, *args: Any, **kwargs: Any) -> HttpResponse:
        if self._search_value == '':
            redirect('blog:index')
        return super().get(request, *args, **kwargs)


class PageDetailView(DetailView):
    model = Page
    slug_field = 'slug'
    template_name = 'blog/pages/page.html'
    context_object_name = 'page'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        page = self.get_object()
        title = f'{page.title} - '
        ctx.update({
            'title': title
        })
        return ctx
    
    def get_queryset(self) -> QuerySet[Any]:
        return super().get_queryset().filter(is_published=True)


def page(request, slug):
    page_obj = Page.objects.get_published().filter(slug=slug).first()

    if page_obj is None:
        raise Http404()

    title = f'{page_obj.title} - '
    return render(
        request,
        'blog/pages/page_obj.html',
        {
            'page': page_obj,
            'title': title
        }
    )


def post(request, slug):
    post_obj = Post.objects.get_published().filter(slug=slug).first()

    if post_obj is None:
        raise Http404()

    title = f'{post_obj.title} - '

    return render(
        request,
        'blog/pages/post.html',
        {
            'post': post_obj,
            'title': title
        }
    )
