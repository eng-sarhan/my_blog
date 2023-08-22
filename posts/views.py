from django.db.models import Count, Q
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views.generic import View, ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import CommentForm, PostForm
from .models import Post, Author, PostView, Category


def get_author(user):
    qs = Author.objects.filter(user=user)
    if qs.exists():
        return qs[0]
    return None


class SearchView(View):
    def get(self, request, *args, **kwargs):
        queryset = Post.objects.all()
        query = request.GET.get('q')
        if query:
            queryset = queryset.filter(
                Q(title__icontains=query)
            ).distinct()
        context = {
            'queryset': queryset
        }
        return render(request, 'posts/search_results.html', context)


def search(request):
    queryset = Post.objects.all()
    query = request.GET.get('q')
    if query:
        queryset = queryset.filter(
            Q(title__icontains=query)
        ).distinct()
    context = {
        'queryset': queryset
    }
    return render(request, 'posts/search_results.html', context)


def get_category_count():
    queryset = Post \
        .objects \
        .values('categories__title') \
        .annotate(Count('categories__title'))
    return queryset


# def post_view(request, category_id):
#     posts = Post.objects.filter(categories__id=category_id)


class IndexView(View):

    def get(self, request, *args, **kwargs):
        featured = Post.objects.filter(featured=True)
        latest = Post.objects.order_by('-timestamp')[0:3]
        context = {
            'object_list': featured,
            'latest': latest,
            # 'form': self.form
        }
        return render(request, 'posts/index.html', context)

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email")
        # new_signup = Signup()
        # new_signup.email = email
        # new_signup.save()
        messages.info(request, "Successfully subscribed")
        return redirect("home")


def index(request):
    featured = Post.objects.filter(featured=True)
    latest = Post.objects.order_by('-timestamp')[0:3]

    context = {
        'object_list': featured,
        'latest': latest,
        # 'form': form
    }
    return render(request, 'posts/index.html', context)


class PostListView(ListView):
    model = Post
    template_name = 'posts/blog.html'
    context_object_name = 'posts'
    paginate_by = 4

    def get_context_data(self, **kwargs):
        category_count = get_category_count()
        most_recent = Post.objects.order_by('-timestamp')[:3]
        context = super().get_context_data(**kwargs)
        context['most_recent'] = most_recent
        context['page_request_var'] = "page"
        context['category_count'] = category_count
        # context['form'] = self.form
        return context


def CategoryView(request, cats):
    category_posts = Post.objects.filter(categories__title=cats.replace('-', ' '))
    return render(request, 'posts/categories.html',
                  {'cats': cats.replace('-', ' ').title(), 'category_posts': category_posts})


class PostListAuthor(ListView):
    model = Post, Author
    template_name = 'posts/post_author_list.html'
    context_object_name = 'author_posts'
    paginate_by = 4

    def get_queryset(self):
        author_id = self.kwargs['author_id']
        return Post.objects.filter(author=int(author_id)).order_by("-timestamp")


def post_list(request):
    category_count = get_category_count()
    most_recent = Post.objects.order_by('-timestamp')[:3]
    post_list = Post.objects.all()
    paginator = Paginator(post_list, 4)
    page_request_var = 'page'
    page = request.GET.get(page_request_var)
    # cats = Category.objects.all()
    try:
        paginated_queryset = paginator.page(page)
    except PageNotAnInteger:
        paginated_queryset = paginator.page(1)
    except EmptyPage:
        paginated_queryset = paginator.page(paginator.num_pages)

    context = {
        'queryset': paginated_queryset,
        'most_recent': most_recent,
        'page_request_var': page_request_var,
        'category_count': category_count,
        # 'form': form
    }
    return render(request, 'posts/blog.html', context)


class UserPostListView(ListView):
    model = Post
    template_name = 'posts/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 4

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs.get('username'))
        return Post.objects.filter(author=user).order_by('-timestamp')


class PostDetailView(DetailView):
    model = Post
    template_name = 'posts/post.html'
    context_object_name = 'post'
    form = CommentForm()

    def get_object(self):
        obj = super().get_object()
        if self.request.user.is_authenticated:
            PostView.objects.get_or_create(
                user=self.request.user,
                post=obj
            )
        return obj

    def get_context_data(self, **kwargs):
        category_count = get_category_count()
        most_recent = Post.objects.order_by('-timestamp')[:3]
        context = super().get_context_data(**kwargs)
        context['most_recent'] = most_recent
        context['page_request_var'] = "page"
        context['category_count'] = category_count
        context['form'] = self.form
        return context

    def post(self, request, *args, **kwargs):
        form = CommentForm(request.POST)
        if form.is_valid():
            post = self.get_object()
            form.instance.user = request.user
            form.instance.post = post
            form.save()
            return redirect(reverse("posts:post-detail", kwargs={
                'pk': post.pk
            }))


def post_detail(request, id):
    category_count = get_category_count()
    most_recent = Post.objects.order_by('-timestamp')[:3]
    post = get_object_or_404(Post, id=id)

    if request.user.is_authenticated:
        PostView.objects.get_or_create(user=request.user, post=post)

    form = CommentForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            form.instance.user = request.user
            form.instance.post = post
            form.save()
            return redirect(reverse("posts:post-detail", kwargs={
                'id': post.pk
            }))
    context = {
        'post': post,
        'most_recent': most_recent,
        'category_count': category_count,
        'form': form
    }
    return render(request, 'posts/post.html', context)


class PostCreateView(CreateView):
    model = Post
    template_name = 'posts/post_create.html'
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create'
        return context

    def form_valid(self, form):
        form.instance.author = get_author(self.request.user)
        form.save()
        return redirect(reverse("posts:post-detail", kwargs={
            'pk': form.instance.pk
        }))


def post_create(request):
    title = 'Create'
    form = PostForm(request.POST or None, request.FILES or None)
    author = get_author(request.user)
    if request.method == "POST":
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse("posts:post-detail", kwargs={
                'id': form.instance.id
            }))
    context = {
        'title': title,
        'form': form
    }
    return render(request, "posts/post_create.html", context)


class PostUpdateView(UpdateView):
    model = Post
    template_name = 'posts/post_create.html'
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update'
        return context

    def form_valid(self, form):
        form.instance.author = get_author(self.request.user)
        form.save()
        return redirect(reverse("posts:post-detail", kwargs={
            'pk': form.instance.pk
        }))


def post_update(request, id):
    title = 'Update'
    post = get_object_or_404(Post, id=id)
    form = PostForm(
        request.POST or None,
        request.FILES or None,
        instance=post)
    author = get_author(request.user)
    if request.method == "POST":
        if form.is_valid():
            form.instance.author = author
            form.save()
            return redirect(reverse("posts:post-detail", kwargs={
                'id': form.instance.id
            }))
    context = {
        'title': title,
        'form': form
    }
    return render(request, "posts/post_create.html", context)


class PostDeleteView(DeleteView):
    model = Post
    success_url = '/blog'
    template_name = 'posts/post_confirm_delete.html'


def post_delete(request, id):
    post = get_object_or_404(Post, id=id)
    post.delete()
    return redirect(reverse("posts:post-list"))


def about(request):
    return render(request, 'posts/about.html')
