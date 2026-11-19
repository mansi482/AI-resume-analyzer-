from django.db import models
from django.conf import settings


class Resume(models.Model):
    FILE_TYPE_CHOICES = [('pdf', 'PDF'), ('docx', 'DOCX')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='resumes')
    filename = models.CharField(max_length=255)
    file = models.FileField(upload_to='resumes/')
    file_type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.user.email} - {self.filename}"
