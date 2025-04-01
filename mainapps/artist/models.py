from django.db import models
from django.utils.text import slugify

class Genre(models.Model):
    """
    Model representing a musical genre.

    Attributes:
        name (CharField): The name of the genre, which must be unique.
        slug (SlugField): A URL-friendly identifier automatically generated from the name.
    """
    
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=70, unique=True, blank=True,editable=False)

    def save(self, *args, **kwargs):
        """
        Auto-generate a unique slug from the genre name before saving.
        """
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure uniqueness
            while Genre.objects.filter(slug=self.slug).exists():
                self.slug = f"{slugify(self.name)}-{Genre.objects.count()}"
        super().save(*args, **kwargs)

    def __str__(self):
        """
        Return the string representation of the Genre.

        Returns:
            str: The name of the genre.
        """
        return self.name
class Artist(models.Model):
    """
    Model representing an artist or band.

    Attributes:
        name (CharField): The name of the artist or band.
        genres (ManyToManyField): A many-to-many relationship with Genre,
            representing the musical genres associated with the artist.
        bio (TextField): An optional biography of the artist.
        website (URLField): An optional URL for the artist's website.
        contact_email (EmailField): The contact email address for the artist.
        contact_phone (CharField): An optional contact phone number for the artist.
    """
    name = models.CharField(max_length=100)
    genres = models.ManyToManyField(Genre, related_name='artists', blank=True,)
    bio = models.TextField(blank=True)
    website = models.URLField(blank=True)
    contact_email = models.EmailField()
    contact_phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        """
        Return the string representation of the Artist.

        Returns:
            str: The name of the artist.
        """
        return self.name
