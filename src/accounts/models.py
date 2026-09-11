import os

from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

MAX_PROFILE_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB


def profile_image_upload_to(instance, filename):
    return os.path.join("Users", instance.username, filename)


def validate_profile_image_size(file):
    if file.size > MAX_PROFILE_IMAGE_SIZE:
        raise ValidationError("Image file too large — max size is 5 MB.")


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    description = models.TextField("Description", max_length=600, default='', blank=True)
    image = models.ImageField(
        default='default/user.jpg',
        upload_to=profile_image_upload_to,
        validators=[validate_profile_image_size],
    )

    def __str__(self):
        return self.username

