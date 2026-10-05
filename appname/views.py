from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q, F
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from .models import Anime, Manga, Genre, Episode, Chapter, AnimeView
from django.db.models import Count, Q
from .models import Anime, Manga, Genre, Episode, Chapter, AnimeView, Shop

User = get_user_model()

def home(request):
    week_ago = timezone.now() - timedelta(days=7)

    # топ-5 по просмотрам за неделю
    top_week = (
        Anime.objects
        .filter(view_records__created_at__gte=week_ago)
        .annotate(week_views=Count('view_records', filter=Q(view_records__created_at__gte=week_ago)))
        .order_by('-week_views')[:5]
    )

    # если за неделю никто ничего не смотрел — падаем на общий топ по views
    if not top_week:
        top_week = Anime.objects.order_by('-views')[:5]

    latest_anime = Anime.objects.order_by('-created_at')[:8]
    latest_manga = Manga.objects.order_by('-created_at')[:8]
    popular_anime = Anime.objects.order_by('-views')[:6]
    popular_manga = Manga.objects.order_by('-views')[:6]

    return render(request, 'appname/home.html', {
        'top_week': top_week,
        'latest_anime': latest_anime,
        'latest_manga': latest_manga,
        'popular_anime': popular_anime,
        'popular_manga': popular_manga,
    })


def anime_list(request):
    qs = Anime.objects.all()
    query = request.GET.get('q')
    genre = request.GET.get('genre')
    status = request.GET.get('status')

    if query:
        qs = qs.filter(Q(title__icontains=query) | Q(title_original__icontains=query))
    if genre:
        qs = qs.filter(genres__slug=genre)
    if status:
        qs = qs.filter(status=status)

    page_obj = Paginator(qs, 24).get_page(request.GET.get('page'))
    return render(request, 'appname/anime_list.html', {
        'page_obj': page_obj,
        'genres': Genre.objects.all(),
        'current_genre': genre,
        'current_status': status,
        'query': query,
    })


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')


def anime_detail(request, slug):
    anime = get_object_or_404(Anime, slug=slug)

    # общий счётчик
    Anime.objects.filter(pk=anime.pk).update(views=F('views') + 1)

    # запись о просмотре (для топа за неделю)
    # защита от накрутки: не чаще 1 раза в час с одного IP
    ip = get_client_ip(request)
    hour_ago = timezone.now() - timedelta(hours=1)
    already = AnimeView.objects.filter(
        anime=anime, ip=ip, created_at__gte=hour_ago
    ).exists()

    if not already:
        AnimeView.objects.create(
            anime=anime,
            user=request.user if request.user.is_authenticated else None,
            ip=ip,
        )

    return render(request, 'appname/anime_detail.html', {
        'anime': anime,
        'episodes': anime.episodes.all(),
    })


def episode_watch(request, slug, number):
    anime = get_object_or_404(Anime, slug=slug)
    episode = get_object_or_404(Episode, anime=anime, number=number)
    return render(request, 'appname/episode_watch.html', {
        'anime': anime,
        'episode': episode,
    })


def manga_list(request):
    qs = Manga.objects.all()
    query = request.GET.get('q')
    genre = request.GET.get('genre')
    status = request.GET.get('status')

    if query:
        qs = qs.filter(Q(title__icontains=query) | Q(author__icontains=query))
    if genre:
        qs = qs.filter(genres__slug=genre)
    if status:
        qs = qs.filter(status=status)

    page_obj = Paginator(qs, 24).get_page(request.GET.get('page'))
    return render(request, 'appname/manga_list.html', {
        'page_obj': page_obj,
        'genres': Genre.objects.all(),
        'current_genre': genre,
        'current_status': status,
        'query': query,
    })


def manga_detail(request, slug):
    manga = get_object_or_404(Manga, slug=slug)
    Manga.objects.filter(pk=manga.pk).update(views=F('views') + 1)
    return render(request, 'appname/manga_detail.html', {
        'manga': manga,
        'chapters': manga.chapters.all(),
    })


def chapter_read(request, slug, number):
    manga = get_object_or_404(Manga, slug=slug)
    chapter = get_object_or_404(Chapter, manga=manga, number=number)
    prev_chapter = Chapter.objects.filter(manga=manga, number__lt=chapter.number).order_by('-number').first()
    next_chapter = Chapter.objects.filter(manga=manga, number__gt=chapter.number).order_by('number').first()
    return render(request, 'appname/chapter_read.html', {
        'manga': manga,
        'chapter': chapter,
        'pages': chapter.pages.all(),
        'prev_chapter': prev_chapter,
        'next_chapter': next_chapter,
    })


def search(request):
    query = request.GET.get('q', '').strip().lower()
    anime_results = []
    manga_results = []

    if query:
        # Ищем через Python — надёжно для кириллицы в SQLite
        all_anime = Anime.objects.all()
        anime_results = [
            a for a in all_anime
            if query in a.title.lower()
            or (a.title_original and query in a.title_original.lower())
        ][:30]

        all_manga = Manga.objects.all()
        manga_results = [
            m for m in all_manga
            if query in m.title.lower()
            or (m.title_original and query in m.title_original.lower())
            or (m.author and query in m.author.lower())
        ][:30]

    return render(request, 'appname/search.html', {
        'query': query,
        'anime_results': anime_results,
        'manga_results': manga_results,
    })


@login_required
def profile(request):
    user = request.user
    week_ago = timezone.now() - timedelta(days=7)

    watched_week = (
        AnimeView.objects
        .filter(user=user, created_at__gte=week_ago)
        .values('anime')
        .distinct()
        .count()
    )

    recently_watched = (
        AnimeView.objects
        .filter(user=user)
        .select_related('anime')
        .order_by('-created_at')[:10]
    )

    return render(request, 'appname/profile.html', {
        'watched_week': watched_week,
        'recently_watched': recently_watched,
        'total_views': AnimeView.objects.filter(user=user).count(),
    })


def user_public(request, username):
    profile_user = get_object_or_404(User, username=username)
    recently_watched = (
        AnimeView.objects
        .filter(user=profile_user)
        .select_related('anime')
        .order_by('-created_at')[:10]
    )
    return render(request, 'appname/user_public.html', {
        'profile_user': profile_user,
        'recently_watched': recently_watched,
    })

def shops_map(request):
    shops = Shop.objects.filter(is_published=True)
    current_category = request.GET.get('category')
    if current_category:
        shops = shops.filter(category=current_category)
    return render(request, 'appname/shops_map.html', {
        'shops': shops,
        'categories': Shop.CATEGORY_CHOICES,
        'current_category': current_category,
    })