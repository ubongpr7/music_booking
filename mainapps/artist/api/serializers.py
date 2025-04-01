from rest_framework import serializers
from mainapps.artist.models import Artist, Genre

class ArtistSerializer(serializers.ModelSerializer):
    """
    Serializer for the Artist model.

    Excludes:
        - genres: Many-to-many field linking artists to genres.
    """

    class Meta:
        model = Artist
        fields = ['id', 'name', 'bio', 'website', 'contact_email', 'contact_phone']
        read_only_fields = ['id']
        


class ArtistGenreUpdateSerializer(serializers.ModelSerializer):
    genres = serializers.ListField(
        child=serializers.CharField(),
        write_only=True,
        help_text="List of permission codenames to assign"
    )

    class Meta:
        model = Artist
        fields = ['genres']

class GenreDetailSerializer(serializers.Serializer):
    has_permission = serializers.BooleanField(read_only=True)
    class Meta:
        model = Genre
        fields = ['name', 'slug', 'has_permission']
        read_only_fields = ['has_permission', 'slug']


