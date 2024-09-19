from django.db import models
from cloudinary.models import CloudinaryField

class Expert(models.Model):
  name=models.CharField( max_length=200)
  description=models.TextField()
  email=models.EmailField(max_length=254)
  created_at=models.DateTimeField(auto_now_add=True)
  updated_at=models.DateTimeField(auto_now=True)
  logo=CloudinaryField('Image', overwrite="True", format="jpg")


  class Meta:
    ordering=('-created_at',)

  def __str__(self):
    return self.email
  
  