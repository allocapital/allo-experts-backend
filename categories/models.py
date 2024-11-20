from django.db import models

class Category(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    experts = models.ManyToManyField('experts.Expert', related_name='related_categories', blank=True)
    courses = models.ManyToManyField('courses.Course', related_name='related_categories', blank=True)
    builds = models.ManyToManyField('builds.Build', related_name='related_categories', blank=True)
    mechanisms = models.ManyToManyField('mechanisms.Mechanism', related_name='related_categories', blank=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return f"https://allo.expert/categories/{self.pk}/"
