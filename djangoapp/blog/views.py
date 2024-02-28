from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from blog.models import Post, Page
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib.auth.models import User
from django.http import Http404
from django.views.generic.list import ListView

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


def created_by(request, id):
    user = User.objects.filter(pk=id).first()
    if user is None:
        raise Http404()
    user_full_name = user.username
    if user.first_name:
        user_full_name = f'{user.first_name} {user.last_name}'

    posts = Post.objects.get_published().filter(created_by__pk=id)

    paginator = Paginator(posts, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        'blog/pages/index.html',
        {
            'page_obj': page_obj,
            'title': f'{user_full_name} post - '
        }
    )


def category(request, slug):
    posts = Post.objects.get_published().filter(category__slug=slug)

    paginator = Paginator(posts, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    if len(page_obj) == 0:
        raise Http404()
    title = f'{page_obj[0].category.name} - '
    return render(
        request,
        'blog/pages/index.html',
        {
            'page_obj': page_obj,
            'title': title
        }
    )


def tag(request, slug):
    posts = Post.objects.get_published().filter(tags__slug=slug)

    paginator = Paginator(posts, 9)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    if len(page_obj) == 0:
        raise Http404()
    title = f'{page_obj[0].tags.filter(slug=slug).first()} - '
    return render(
        request,
        'blog/pages/index.html',
        {
            'page_obj': page_obj,
            'title': title
        }
    )


def search(request):
    search_value = request.GET.get('search', '').strip()
    posts = (
        Post.objects.get_published()
        .filter(
            Q(title__icontains=search_value) |
            Q(exerpt__icontains=search_value) |
            Q(content__icontains=search_value) 
        )[:9]
    )

    title = f'{search_value[:30]} - '

    return render(
        request,
        'blog/pages/index.html',
        {
            'page_obj': posts,
            'search_value': search_value,
            'title': title
        }
    )


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
