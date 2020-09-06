from django.urls import path

from . import views

urlpatterns = [
    path("<username>/follow/", views.profile_follow, name="profile_follow"),
    path("follow/", views.follow_index, name="follow_index"),
    # Главная страница
    path('', views.index, name='index'),
    # Создание нового поста
    path('new/', views.new_post, name='new_post'),
    # Профайл пользователя
    path('<str:username>/', views.profile, name='profile'),
    # Просмотр записи
    path('<str:username>/<int:post_id>/', views.post_view, name='post'),
    path('<str:username>/<int:post_id>/edit/', views.post_edit, name='post_edit'),
    # Просмотр групп
    path('group/<str:slug>', views.group_posts, name='group'),
    # коментарии
    path("<username>/<int:post_id>/comment/", views.add_comment, name="add_comment"),
    path("<username>/unfollow/", views.profile_unfollow, name="profile_unfollow"),


]
