from django.db import models
from django.conf import settings
from django.urls import reverse


def slugify_ru(text):
    """Простой slugify с поддержкой кириллицы."""
    translit = {
        'а':'a','б':'b','в':'v','г':'g','д':'d','е':'e','ё':'e','ж':'zh','з':'z',
        'и':'i','й':'y','к':'k','л':'l','м':'m','н':'n','о':'o','п':'p','р':'r',
        'с':'s','т':'t','у':'u','ф':'f','х':'h','ц':'ts','ч':'ch','ш':'sh','щ':'sch',
        'ъ':'','ы':'y','ь':'','э':'e','ю':'yu','я':'ya',
    }
    text = text.lower()
    result = ''.join(translit.get(ch, ch) for ch in text)
    result = ''.join(c if c.isalnum() else '-' for c in result)
    while '--' in result:
        result = result.replace('--', '-')
    return result.strip('-')


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_ru(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'


class Studio(models.Model):
    name = models.CharField(max_length=200, unique=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_ru(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Студия'
        verbose_name_plural = 'Студии'


class Anime(models.Model):
    STATUS_CHOICES = [
        ('ongoing', 'Онгоинг'),
        ('released', 'Вышел'),
        ('announced', 'Анонс'),
    ]
    TYPE_CHOICES = [
        ('tv', 'TV-сериал'),
        ('movie', 'Фильм'),
        ('ova', 'OVA'),
        ('ona', 'ONA'),
        ('special', 'Спешл'),
    ]

    title = models.CharField(max_length=300)
    title_original = models.CharField(max_length=300, blank=True)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    description = models.TextField()
    poster = models.ImageField(upload_to='anime/posters/', null=True, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ongoing')
    anime_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='tv')
    episodes_count = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    genres = models.ManyToManyField(Genre, related_name='anime', blank=True)
    studio = models.ForeignKey(Studio, on_delete=models.SET_NULL, null=True, blank=True, related_name='anime')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_ru(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('appname:anime_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Аниме'
        verbose_name_plural = 'Аниме'


class Episode(models.Model):
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, related_name='episodes')
    number = models.PositiveIntegerField()
    title = models.CharField(max_length=300, blank=True)
    video_url = models.URLField(help_text='Ссылка на iframe/video (YouTube, VK и т.д.)')
    thumbnail = models.ImageField(upload_to='anime/episodes/', null=True, blank=True)
    duration = models.PositiveIntegerField(help_text='Длительность в минутах', default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.anime.title} — Эпизод {self.number}'

    class Meta:
        ordering = ['number']
        unique_together = ['anime', 'number']
        verbose_name = 'Эпизод'
        verbose_name_plural = 'Эпизоды'


class Manga(models.Model):
    STATUS_CHOICES = [
        ('ongoing', 'Выходит'),
        ('completed', 'Завершена'),
        ('announced', 'Анонс'),
    ]

    title = models.CharField(max_length=300)
    title_original = models.CharField(max_length=300, blank=True)
    slug = models.SlugField(max_length=300, unique=True, blank=True)
    description = models.TextField()
    cover = models.ImageField(upload_to='manga/covers/', null=True, blank=True)
    author = models.CharField(max_length=200, blank=True)
    artist = models.CharField(max_length=200, blank=True)
    year = models.PositiveIntegerField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ongoing')
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    genres = models.ManyToManyField(Genre, related_name='manga', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_ru(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('appname:manga_detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Манга'
        verbose_name_plural = 'Манга'


class Chapter(models.Model):
    manga = models.ForeignKey(Manga, on_delete=models.CASCADE, related_name='chapters')
    number = models.DecimalField(max_digits=6, decimal_places=1)
    title = models.CharField(max_length=300, blank=True)
    volume = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.manga.title} — Глава {self.number}'

    class Meta:
        ordering = ['number']
        unique_together = ['manga', 'number']
        verbose_name = 'Глава'
        verbose_name_plural = 'Главы'


class Page(models.Model):
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='pages')
    number = models.PositiveIntegerField()
    image = models.ImageField(upload_to='manga/pages/')

    def __str__(self):
        return f'Стр. {self.number} ({self.chapter})'

    class Meta:
        ordering = ['number']
        unique_together = ['chapter', 'number']
        verbose_name = 'Страница'
        verbose_name_plural = 'Страницы'

class AnimeView(models.Model):
    anime = models.ForeignKey(Anime, on_delete=models.CASCADE, related_name='view_records')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='anime_views'
    )
    ip = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Просмотр аниме'
        verbose_name_plural = 'Просмотры аниме'

class Shop(models.Model):
    CATEGORY_CHOICES = [
        ('manga', 'Манга и комиксы'),
        ('merch', 'Аниме-мерч'),
        ('figures', 'Фигурки'),
        ('cafe', 'Гик-кафе'),
        ('cosplay', 'Косплей-магазин'),
        ('other', 'Другое'),
    ]

    name = models.CharField('Название', max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    category = models.CharField('Категория', max_length=20,
                                choices=CATEGORY_CHOICES, default='merch')
    description = models.TextField('Описание', blank=True)
    address = models.CharField('Адрес', max_length=300)

    # Контакты
    phone = models.CharField('Телефон', max_length=50, blank=True)
    instagram = models.URLField('Instagram', blank=True)
    telegram = models.URLField('Telegram', blank=True)
    website = models.URLField('Сайт', blank=True)
    work_hours = models.CharField('Часы работы', max_length=200, blank=True,
                                  help_text='Например: Пн-Вс 10:00–21:00')

    # Медиа
    photo = models.ImageField('Фото', upload_to='shops/', null=True, blank=True)

    # Модерация
    is_published = models.BooleanField('Опубликован', default=True)
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  on_delete=models.SET_NULL,
                                  null=True, blank=True,
                                  related_name='shops_added')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_ru(self.name)
        super().save(*args, **kwargs)

    def get_2gis_url(self):
        """Ссылка на 2ГИС с поиском по названию и адресу."""
        from urllib.parse import quote
        query = quote(f'{self.name} {self.address}')
        return f'https://2gis.kg/bishkek/search/{query}'

    def get_2gis_route_url(self):
        """Ссылка на построение маршрута в 2ГИС."""
        from urllib.parse import quote
        query = quote(self.address)
        return f'https://2gis.kg/bishkek/search/{query}'

    def __str__(self):
        return self.name