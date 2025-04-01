from rest_framework import viewsets
from mainapps.artist.models import Artist,Genre
from .serializers import ArtistSerializer, ArtistGenreUpdateSerializer,GenreDetailSerializer
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework import permissions
from django.db.models import Exists, OuterRef

class ArtistViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows artists to be viewed or edited.

    Supports:
        - GET (list & retrieve)
        - POST (create)
        - PUT/PATCH (update)
        - DELETE (remove)
    """
    queryset = Artist.objects.all()
    serializer_class = ArtistSerializer

class ArtistGenre(generics.RetrieveUpdateAPIView):
    queryset = Artist.objects.all() 
    permission_classes = [permissions.IsAuthenticated,]
    lookup_field = 'pk'
    
    def get_serializer_class(self):
        if getattr(self, 'swagger_fake_view', False):
            return GenreDetailSerializer  # Prevents calling `get_object()` in schema generation
        if self.request.method == 'GET':
            return GenreDetailSerializer
        return ArtistGenreUpdateSerializer
    
    def get(self, request, *args, **kwargs):
        """Get all genre with artist status"""
        artist = self.get_object()
        
        genres = Genre.objects.annotate(
            has_permission=Exists(
                artist.genres.through.objects.filter(
                    artist_id=artist.id,  
                    genre_id=OuterRef('id')
                )
            )
        )
        serializer = self.get_serializer(genres, many=True)

        return Response({'genres': serializer.data})
    def put(self, request, *args, **kwargs):

        """Update artist genres with complete list"""
        artist = self.get_object()
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Validate all genre slugs exist
        slugs = serializer.validated_data['genres']
        valid_genres = Genre.objects.filter(slug__in=slugs)
        
        # Check for invalid genres
        received_genres = set(slugs)
        valid_slugs = set(valid_genres.values_list('slug', flat=True))
        if invalid := slugs - valid_slugs:
            return Response(
                {"detail": f"Invalid genres: {', '.join(invalid)}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Atomic genre update
        with transaction.atomic():
            artist.genres.set.set(valid_genres)
        
        return Response({'status': 'genres updated'}, status=status.HTTP_200_OK)
    

