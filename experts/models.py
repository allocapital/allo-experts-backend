from django.db import models
from cloudinary.models import CloudinaryField
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import slugify

class ExpertCategory(models.TextChoices):
        ALLO_MECHANISMS = 'allo_mechanisms', _('Allo Mechanisms')
        ALLO_DEV = 'allo_dev', _('Allo Dev')
      
class Expert(models.Model):
  name=models.CharField( max_length=200)
  slug=models.SlugField(max_length=255, null=True, blank=True)
  description=models.TextField()
  expert_in=models.CharField(
        max_length=40,
        choices=ExpertCategory.choices,
        default=ExpertCategory.ALLO_MECHANISMS
    )
  contact_info_telegram=models.CharField(max_length=50)
  contact_info_twitter=models.CharField(max_length=50)
  contact_info_email=models.EmailField(max_length=254)
  created_at=models.DateTimeField(auto_now_add=True)
  updated_at=models.DateTimeField(auto_now=True)
  avatar=CloudinaryField('Image', overwrite="True", format="png")

  class Meta:
    ordering=('-created_at',)

  def __str__(self):
    return self.name

  def save(self, *args, **kwargs):
    # Generate a base slug from the title
    new_slug = slugify(self.name)

    # If this instance already exists (we're editing)
    if self.pk:
        # Fetch the current instance from the database
        current_instance = Expert.objects.get(pk=self.pk)
        
        # If the title has changed, we need to check the slug
        if current_instance.name != self.name:
            # If the new slug already exists for another instance, append a number
            if Expert.objects.exclude(pk=self.pk).filter(slug=new_slug).exists():
                count = 1
                new_unique_slug = f"{new_slug}-{count}"
                # Find a unique slug by incrementing the count
                while Expert.objects.filter(slug=new_unique_slug).exists():
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
        while Expert.objects.filter(slug=new_slug).exists():
            count = 1
            new_unique_slug = f"{new_slug}-{count}"
            while Expert.objects.filter(slug=new_unique_slug).exists():
                count += 1
                new_unique_slug = f"{new_slug}-{count}"
            new_slug = new_unique_slug
        self.slug = new_slug

    super().save(*args, **kwargs)
  