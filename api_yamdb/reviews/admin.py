from django.contrib import admin

from .models import (
    Category,
    Comment,
    Genre,
    GenreTitle,
    Review,
    Title,
    User
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'text',
        'pub_date',
        'author',
        'review',
    )
    search_fields = ('review', 'author',)
    list_filter = ('review', 'author',)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug',)
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(GenreTitle)
class GenreTitle(admin.ModelAdmin):
    list_display = ('id', 'genre', 'title',)
    search_fields = ('title',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'text',
        'pub_date',
        'author',
        'score',
        'title',
    )
    search_fields = ('title',)
    list_filter = ('title', 'author')


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'year', 'category', 'description',)
    search_fields = ('name', 'description',)
    list_filter = ('name', 'description',)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'first_name', 'last_name', 'bio', 'role')
    search_fields = ('first_name', 'last_name')
    list_filter = ('role',)
    list_editable = ('role',)
    empty_value_display = '-пусто-'
