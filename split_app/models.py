from django.db import models

# Create your models here.
class Document(models.Model):

    docfile = models.FileField(upload_to="original/")
    title = models.CharField(max_length=255)
    key = models.CharField(max_length=50, default="")
    created_at = models.DateTimeField(auto_now_add=True)
    max_lines = models.IntegerField(default=4000)
    copy_headers = models.BooleanField(default=True)
    count_headers = models.BooleanField(default=False)

    # not needed for csv
    sheet_name = models.CharField(max_length=255, default="")
