from datetime import datetime

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models


def validate_year(value):
    current_year = datetime.now().year
    if not 0 <= value <= current_year:
        raise ValidationError('Check the year fild.'
                              'It should be less or equal to current year')


class User(AbstractUser):
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'
    ROLES = (
        (ADMIN, 'Admin'),
        (MODERATOR, 'Moderator'),
        (USER, 'User'),
    )

    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='First name',
    )
    email = models.EmailField(
        blank=False,
        unique=True,
        max_length=254,
        verbose_name='Email address',
    )
    role = models.CharField(
        choices=ROLES,
        max_length=16,
        default='user',
        verbose_name='Access level',
    )
    bio = models.TextField(
        verbose_name='Biography',
        blank=True,
    )

    @property
    def is_admin(self):
        return self.is_superuser or self.role == self.ADMIN

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'


class Category(models.Model):
    name = models.CharField('name', max_length=256, db_index=True)
    slug = models.SlugField('slug', unique=True, max_length=50)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField('genre name', max_length=256, db_index=True)
    slug = models.SlugField('slug', unique=True, max_length=50)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField('name', max_length=200, db_index=True)
    year = models.IntegerField('year',
                               validators=[validate_year],
                               db_index=True)
    description = models.TextField('description', blank=True)
    genre = models.ManyToManyField(Genre, verbose_name='genre')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='titles',
        verbose_name='category',
    )

    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.name


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='title')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='author')
    text = models.TextField('review text')
    score = models.IntegerField('your score',
                                blank=False)
    pub_date = models.DateTimeField('publication date', auto_now_add=True)

    # <На одно произведение> <один user> может оставить <только один отзыв>
    class Meta:
        ordering = ['id']
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'], name='unique_review')]


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='review',
    )
    text = models.TextField('comments')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments_author',
        verbose_name='author',
    )
    pub_date = models.DateTimeField('publication date', auto_now_add=True)

    class Meta:
        ordering = ['id']
