from rest_framework import filters

from .models import Genre


class BookFilterBackend(filters.BaseFilterBackend):
    """
    Filter for BookViewSet
    """
    def filter_queryset(self, request, queryset, view):
        genre_slug = request.query_params.get('genre')
        title = request.query_params.get('title')
        author = request.query_params.get('author')
        country = request.query_params.get('country')
        if genre_slug:
            genre_id = Genre.objects.get(slug=genre_slug).id
            return queryset.filter(genre=genre_id)
        if title:
            return queryset.filter(title__contains=title)
        if author:
            return queryset.filter(author=author)
        if country:
            return queryset.filter(country=country)
        return queryset
    
