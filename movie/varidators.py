import os
from django.core.exceptions import ValidationError

def validate_is_video(value):
    ext = os.path.splitext(value.name)[1]

    if not ext.lower() in ['.mp4']:
        raise ValidationError('Only ".mp4" files are availables.')