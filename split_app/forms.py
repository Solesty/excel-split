from django import forms
from .models import Document


class DocumentForm(forms.ModelForm):
    sheet_name = forms.CharField(max_length=255, required=False, strip=True)

    class Meta:
        model = Document
        fields = (
            "title",
            "max_lines",
            "docfile",
            "sheet_name",
            "copy_headers",
            "count_headers",
        )

    # docfile = forms.FileField(label='Select a file')
    # title = forms.CharField(max_length=255)
