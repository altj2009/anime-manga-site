from django.contrib import admin
from .models import Genre, Studio, Anime, Episode, Manga, Chapter, Page, Shop



@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Studio)
class StudioAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


class EpisodeInline(admin.TabularInline):
    model = Episode
    extra = 1


@admin.register(Anime)
class AnimeAdmin(admin.ModelAdmin):
    list_display = ('title', 'year', 'status', 'anime_type', 'rating', 'views')
    list_filter = ('status', 'anime_type', 'genres', 'year')
    search_fields = ('title', 'title_original')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('genres',)
    inlines = [EpisodeInline]


class PageInline(admin.TabularInline):
    model = Page
    extra = 1


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('manga', 'number', 'title', 'volume')
    list_filter = ('manga',)
    inlines = [PageInline]


@admin.register(Manga)
class MangaAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'year', 'status', 'rating', 'views')
    list_filter = ('status', 'genres')
    search_fields = ('title', 'author')
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ('genres',)

@admin.register(Shop)
class ShopAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'address', 'is_published', 'created_at')
    list_filter = ('category', 'is_published')
    search_fields = ('name', 'address')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_published',)
    fieldsets = (
        ('Основное', {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Адрес', {
            'fields': ('address',),
            'description': 'Введи адрес так, как он есть в 2ГИС.'
        }),
        ('Контакты', {
            'fields': ('phone', 'instagram', 'telegram', 'website', 'work_hours')
        }),
        ('Медиа и модерация', {
            'fields': ('photo', 'is_published', 'added_by')
        }),
    )