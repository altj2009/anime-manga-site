from django.urls import path
from . import views

app_name = 'appname'

urlpatterns = [
    path('', views.home, name='home'),
    path('anime/', views.anime_list, name='anime_list'),
    path('anime/<slug:slug>/', views.anime_detail, name='anime_detail'),
    path('anime/<slug:slug>/episode/<int:number>/', views.episode_watch, name='episode_watch'),
    path('manga/', views.manga_list, name='manga_list'),
    path('manga/<slug:slug>/', views.manga_detail, name='manga_detail'),
    path('manga/<slug:slug>/chapter/<int:number>/', views.chapter_read, name='chapter_read'),
    path('search/', views.search, name='search'),
]

urlpatterns = [
    path('', views.home, name='home'),
    path('anime/', views.anime_list, name='anime_list'),
    path('anime/<slug:slug>/', views.anime_detail, name='anime_detail'),
    path('anime/<slug:slug>/episode/<int:number>/', views.episode_watch, name='episode_watch'),
    path('manga/', views.manga_list, name='manga_list'),
    path('manga/<slug:slug>/', views.manga_detail, name='manga_detail'),
    path('manga/<slug:slug>/chapter/<int:number>/', views.chapter_read, name='chapter_read'),
    path('search/', views.search, name='search'),

    # ← добавить:
    path('profile/', views.profile, name='profile'),
    path('user/<str:username>/', views.user_public, name='user_public'),
    path('shops-map/', views.shops_map, name='shops_map'),
]