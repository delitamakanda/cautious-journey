from django.urls import path

from posts.api import views as views_post

urlpatterns = [
    path('tags', views_post.TagList.as_view(), name='tag-list'),
    path('posts', views_post.PostList.as_view(), name='post-list'),
    path('posts/<str:slug>', views_post.PostDetail.as_view(), name='post-detail'),
]