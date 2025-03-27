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
    title = models.CharField(max_length=200)
    description = MDTextField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Markdown content"

    slug = models.SlugField(max_length=255, null=True, blank=True, unique=True)  # Ensure slug is unique
    hidden=models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    background_img = CloudinaryField('Image', overwrite=True)
    background_color = models.CharField(
        max_length=10,
        choices=MechanismBgColor.choices,
        default=MechanismBgColor.PINK
    )
    categories = models.ManyToManyField('categories.Category', related_name='related_mechanisms', blank=True)
    experts = models.ManyToManyField('experts.Expert', related_name='related_mechanisms', blank=True)
    courses = models.ManyToManyField('courses.Course', related_name='related_mechanisms', blank=True)
    builds = models.ManyToManyField('builds.Build', related_name='related_mechanisms', blank=True)
    mechanisms = models.ManyToManyField('self', blank=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return f"https://allo.expert/mechanisms/{self.slug}/"

    def save(self, *args, **kwargs):
        # Generate a base slug from the title
        new_slug = slugify(self.title)

        if self.pk:  # Editing an existing instance
            # Fetch the current instance from the database
            current_instance = Mechanism.objects.get(pk=self.pk)

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
        while Mechanism.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
            self.slug = f"{original_slug}-{count}"
            count += 1

        super().save(*args, **kwargs)


class MechanismMapping(models.Model):
    """
    Maps funders and grant pools to specific mechanisms.
    This is used to categorize funding data from BigQuery.
    """
    funder = models.CharField(max_length=255, help_text="Name of the funding organization ('funder' value  - e.g., 'gitcoin', 'optimism')")
    grant_pool_name = models.CharField(max_length=255, null=True, blank=True, help_text="Name of the grant pool or program ('grant_pool_name' value)")
    mechanism = models.ForeignKey(Mechanism, on_delete=models.CASCADE, related_name='mappings')
    priority = models.IntegerField(default=0, help_text="Higher priority mappings are applied first")
    
    class Meta:
        ordering = ('-priority',)
        verbose_name_plural = "Mechanism Mappings"
        unique_together = [['funder', 'grant_pool_name']]
    
    def __str__(self):
        if self.grant_pool_name:
            return f"{self.funder} - {self.grant_pool_name} → {self.mechanism.title}"
        return f"{self.funder} → {self.mechanism.title}"


class MechanismTrend(models.Model):
    """
    Stores funding data aggregated by mechanism and month.
    This is used to generate trend charts on the frontend.
    """
    mechanism = models.ForeignKey(Mechanism, on_delete=models.CASCADE, related_name='trends')
    month = models.DateField(help_text="First day of the month for this data point")
    value = models.DecimalField(max_digits=14, decimal_places=2, help_text="Funding amount in USD")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ('month',)
        verbose_name_plural = "Mechanism Trends"
        unique_together = [['mechanism', 'month']]
    
    def __str__(self):
        return f"{self.mechanism.title} - {self.month.strftime('%Y-%m')} - ${self.value}"