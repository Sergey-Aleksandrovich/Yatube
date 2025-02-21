from django.urls import path

from . import views

urlpatterns = [
    path("<username>/follow/", views.profile_follow, name="profile_follow"),
    path("follow/", views.follow_index, name="follow_index"),
    path('', views.index, name='index'),
    path('new/', views.new_post, name='new_post'),
    path('<str:username>/', views.profile, name='profile'),
    path('<str:username>/<int:post_id>/', views.post_view, name='post'),
    path('<str:username>/<int:post_id>/edit/', views.post_edit,
         name='post_edit'),
    path('group/<str:slug>', views.group_posts, name='group'),
    path("<username>/<int:post_id>/comment/", views.add_comment,
         name="add_comment"),
    path("<username>/unfollow/", views.profile_unfollow,
         name="profile_unfollow"),

]
