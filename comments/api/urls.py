from django.urls import path

from comments.api import views as views_comment

urlpatterns = [
    path('comments/', views_comment.CommentCreateApiView.as_view(), name='comment-create'),
    path('comments-list/', views_comment.CommentListApiView.as_view(), name='comment-list'),
]