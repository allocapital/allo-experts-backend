from django.db import models
from cloudinary.models import CloudinaryField
from django.utils.translation import gettext_lazy as _
from django.template.defaultfilters import slugify

class ExpertCategory(models.TextChoices):
        ALLO_ExpertS = 'allo_Experts', _('Allo Experts')
        ALLO_DEV = 'allo_dev', _('Allo Dev')
      
class Expert(models.Model):
  name=models.CharField( max_length=200)
  slug=models.SlugField(max_length=255, null=True, blank=True)
  description=models.TextField()
  expert_in=models.CharField(
        max_length=40,
        choices=ExpertCategory.choices,
        default=ExpertCategory.ALLO_ExpertS
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

        if self.pk:  # Editing an existing instance
            # Fetch the current instance from the database
            current_instance = Expert.objects.get(pk=self.pk)

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
        while Expert.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f"{original_slug}-{count}"
            count += 1

        super().save(*args, **kwargs)
