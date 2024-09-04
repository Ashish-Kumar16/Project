from django.urls import path
from .views import RegisterView, LoginView, PostCreateView, PostListView, CommentCreateView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('posts/', PostListView.as_view(), name='posts-list'),
    path('posts/<int:post_id>/comments/', CommentCreateView.as_view(), name='post-comments'),
    path('posts/create/', PostCreateView.as_view(), name='create-post'),
]
