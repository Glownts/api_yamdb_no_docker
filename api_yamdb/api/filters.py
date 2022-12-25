"""
Фильтры для вью-функций приложения api.
"""
import django_filters

from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    """Фильтр для соритровки произведений."""
    category = django_filters.Filter(field_name='category__slug')
    genre = django_filters.Filter(field_name='genre__slug')
    name = django_filters.Filter(field_name='name', lookup_expr='contains')
    year = django_filters.NumberFilter(field_name='year')

    class Meta:
        model = Title
        fields = ('category', 'genre', 'year', 'name')
