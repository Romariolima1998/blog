from django.db import models
from django.contrib.auth.models import User


from django_summernote.models import AbstractAttachment


from utils.redimencionamento import resize_image
from utils.rands import slugify_new


class PostManager(models.Manager):
    def get_published(self):
        return self.filter(is_published=True).order_by('-pk')


class PostAttachment(AbstractAttachment):
    def save(self, *args, **kwargs):
        if not self.name:
            self.name = self.file.name
        current_favicon_name = str(self.file.name)
        super_save = super().save(*args, **kwargs)
        favicon_changed = False

        if self.file:
            favicon_changed = current_favicon_name != self.file.name

        if favicon_changed:
            resize_image(self.file, 900, quality=70)

        return super_save


class Tag(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(
        unique=True, default=None,
        null=True, blank=True, max_length=255
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_new(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Category(models.Model):
    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
    name = models.CharField(max_length=255)
    slug = models.SlugField(
        unique=True, default=None,
        null=True, blank=True, max_length=255
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_new(self.name)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Page(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(
        unique=True, default=None,
        null=True, blank=True, max_length=255
    )
    is_published = models.BooleanField(
        default=False,
        help_text='Este campo precisa estar marcado para a pagina ser exibida',
        null=True
        )
    content = models.TextField(null=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify_new(self.title)
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class Post(models.Model):
    objects = PostManager()

    title = models.CharField(max_length=255)
    slug = models.SlugField(
        unique=True, default=None,
        null=True, blank=True, max_length=255
    )
    exerpt = models.CharField(max_length=150)
    is_published = models.BooleanField(
        default=False,
        help_text='Este campo precisa estar marcado para o post ser exibido',
        )
    content = models.TextField()
    cover = models.ImageField(upload_to='post/%Y/%m', blank=True, default='')
    cover_in_post_content = models.BooleanField(
        default=True,
        help_text='exibir a imagem de capa no conteudo do post?'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='post_created_by'
    )
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        blank=True, null=True,
        related_name='post_updated_by'
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True,
        blank=True, default=None,
    )
    tags = models.ManyToManyField(
        Tag, blank=True, default='',
        )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):

        current_favicon_name = str(self.cover.name)
        super_save = super().save(*args, **kwargs)
        favicon_changed = False

        if self.cover:
            favicon_changed = current_favicon_name != self.cover.name

        if favicon_changed:
            resize_image(self.cover, 900, quality=70)

        return super_save
