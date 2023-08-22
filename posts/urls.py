from django.urls import path, re_path
from posts import views
from posts.views import IndexView, PostListView, PostCreateView, PostDetailView, PostUpdateView, PostDeleteView, \
    UserPostListView, search, CategoryView \
    # , post_view

app_name = 'posts'
urlpatterns = [
    path('', IndexView.as_view(), name='home'),
    # path('blog/', post_list, name='post-list'),
    path('blog/', PostListView.as_view(), name='post-list'),
    re_path(r'^user/(?P<username>\w{0,50})/$', UserPostListView.as_view(), name='user-posts'),
    # path('user/<str:username>/', UserPostListView.as_view(), name="user-posts"),
    path('search/', search, name='search'),
    # path('email-signup/', email_list_signup, name='email-list-signup'),
    # path('create/', post_create, name='post-create'),
    path('create/', PostCreateView.as_view(), name='post-create'),
    # path('post/<id>/', post_detail, name='post-detail'),
    path('post/<pk>/', PostDetailView.as_view(), name='post-detail'),
    # path('post/<id>/update/', post_update, name='post-update'),
    path('post/<pk>/update/', PostUpdateView.as_view(), name='post-update'),
    # path('post/<id>/delete/', post_delete, name='post-delete'),
    path('post/<pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    path('about/', views.about, name="blog-about"),

    path("author/<int:author_id>/", views.PostListAuthor.as_view(), name="author"),
    path('categories/<str:cats>/', CategoryView, name='categories'),

    # path('post', post_view, name='post_view'),
]
