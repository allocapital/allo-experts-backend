from django.db import models
from cloudinary.models import CloudinaryField
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _
from mdeditor.fields import MDTextField

class BuildBgColor(models.TextChoices):
    PINK = '#FFE5F8', _('Pink')
    GREEN = '#DBF0DB', _('Green')
    PURPLE = '#DAD6FF', _('Purple')
    YELLOW = '#FFEEBE', _('Yellow')
    CREAM = '#FFFDEB', _('Cream')
    PEACH = '#FFD9CE', _('Peach')
    BLUE = '#D3EDFE', _('Blue')
    OCEAN = '#C8F6F6', _('Ocean')

class Build(models.Model):
    title = models.CharField(max_length=200)
    description = MDTextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Markdown content"

    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)
    hidden=models.BooleanField(default=False)
    status = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    metadata = models.JSONField(default=dict) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    background_img = CloudinaryField('Image', overwrite=True)
    background_color = models.CharField(
        max_length=10,
        choices=BuildBgColor.choices,
        default=BuildBgColor.PINK
    )
    categories = models.ManyToManyField('categories.Category', related_name='related_builds', blank=True)
    experts = models.ManyToManyField('experts.Expert', related_name='related_builds', blank=True)
    mechanisms = models.ManyToManyField('mechanisms.Mechanism', related_name='related_builds', blank=True)
    courses = models.ManyToManyField('courses.Course', related_name='related_builds', blank=True)
    builds = models.ManyToManyField('self', blank=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return f"https://allo.expert/builds/{self.slug}/"

    def save(self, *args, **kwargs):
        # Generate a base slug from the title
        new_slug = slugify(self.title)

        if self.pk:  # Editing an existing instance
            # Fetch the current instance from the database
            current_instance = Build.objects.get(pk=self.pk)

            # Check if the title was changed
            if current_instance.title != self.title:
                # Title has changed, so we generate a new slug from the updated title
                self.slug = new_slug
            elif current_instance.slug != self.slug and self.slug:
                # Slug was manually edited, so we keep the manually set slug
                self.slug = self.slug
            else:
                # No change to title, keep the existing slug
                self.slug = current_instance.slug
        else:  # Creating a new instance
            # Generate a slug from the title for new instances
            self.slug = new_slug

        # Ensure slug uniqueness by appending a counter if necessary
        original_slug = self.slug
        count = 1
        while Build.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f"{original_slug}-{count}"
            count += 1

        super().save(*args, **kwargs)
