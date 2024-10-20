from django.db import models
from cloudinary.models import CloudinaryField
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _
from mdeditor.fields import MDTextField


class CourseBgColor(models.TextChoices):
        PINK = '#FFE5F8', _('Pink')
        GREEN = '#DBF0DB', _('Green')
        PURPLE = '#DAD6FF', _('Purple')
        YELLOW = '#FFEEBE', _('Yellow')
        CREAM = '#FFFDEB', _('Cream')
        PEACH = '#FFD9CE', _('Peach')
        BLUE = '#D3EDFE', _('Blue')
        OCEAN = '#C8F6F6', _('Ocean')

class Course(models.Model):
  title=models.CharField( max_length=200)
  description=MDTextField(null=True, blank=True)
  class Meta:
        verbose_name_plural = "Markdown content"
  slug=models.SlugField(max_length=255, null=True, blank=True)
  created_at=models.DateTimeField(auto_now_add=True)
  updated_at=models.DateTimeField(auto_now=True)
  background_img=CloudinaryField('Image', overwrite="True")
  background_color=models.CharField(
        max_length=10,
        choices=CourseBgColor.choices,
        default=CourseBgColor.PINK
    )
  starts_at=models.DateTimeField(null=True, blank=True)
  register_url=models.URLField(null=True, blank=True)


  class Meta:
    ordering=('-created_at',)

  def __str__(self):
    return self.title

  def save(self, *args, **kwargs):
    # Generate a base slug from the title
    new_slug = slugify(self.title)

    # If this instance already exists (we're editing)
    if self.pk:
        # Fetch the current instance from the database
        current_instance = Course.objects.get(pk=self.pk)
        
        # If the title has changed, we need to check the slug
        if current_instance.title != self.title:
            # If the new slug already exists for another instance, append a number
            if Course.objects.exclude(pk=self.pk).filter(slug=new_slug).exists():
                count = 1
                new_unique_slug = f"{new_slug}-{count}"
                # Find a unique slug by incrementing the count
                while Course.objects.filter(slug=new_unique_slug).exists():
                    count += 1
                    new_unique_slug = f"{new_slug}-{count}"
                self.slug = new_unique_slug  # Set to unique slug
            else:
                # If the slug is unique, assign it directly
                self.slug = new_slug
        else:
            # If the title hasn't changed, keep the existing slug
            self.slug = current_instance.slug
    else:
        # For new instances, ensure the slug is unique
        while Course.objects.filter(slug=new_slug).exists():
            count = 1
            new_unique_slug = f"{new_slug}-{count}"
            while Course.objects.filter(slug=new_unique_slug).exists():
                count += 1
                new_unique_slug = f"{new_slug}-{count}"
            new_slug = new_unique_slug
        self.slug = new_slug

    super().save(*args, **kwargs)