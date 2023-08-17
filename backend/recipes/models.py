from django.db import models
from django.core.validators import RegexValidator


class Tag(models.Model):

    name = models.CharField(
        blank=False,
        max_length=200,
        unique=True,

    )
    color = models.CharField(
        blank=False,
        max_length=7,
        unique=True,
    )
    slug = models.SlugField(
        blank=False,
        max_length=200,
        unique=True,
        validators=[RegexValidator('^[-a-zA-Z0-9_]+$')],
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
