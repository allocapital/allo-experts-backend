from django.db import models
from cloudinary.models import CloudinaryField
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _
from mdeditor.fields import MDTextField


class MechanismBgColor(models.TextChoices):
        PINK = '#FFE5F8', _('Pink')
        GREEN = '#DBF0DB', _('Green')
        PURPLE = '#DAD6FF', _('Purple')
        YELLOW = '#FFEEBE', _('Yellow')
        CREAM = '#FFFDEB', _('Cream')
        PEACH = '#FFD9CE', _('Peach')
        BLUE = '#D3EDFE', _('Blue')
        OCEAN = '#C8F6F6', _('Ocean')

class Mechanism(models.Model):
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
        choices=MechanismBgColor.choices,
        default=MechanismBgColor.PINK
    )


  class Meta:
    ordering=('-created_at',)

  def __str__(self):
    return self.title
  
  def save(self, *args, **kwargs):
    to_assign=slugify(self.title)
    

    if Mechanism.objects.filter(slug=to_assign).exists():
        to_assign=to_assign+str(Mechanism.objects.all().count())

    self.slug=to_assign

    super().save(*args, **kwargs)