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
    to_assign=slugify(self.name)
    

    if Expert.objects.filter(slug=to_assign).exists():
        to_assign=to_assign+str(Expert.objects.all().count())

    self.slug=to_assign

    super().save(*args, **kwargs)
  
  