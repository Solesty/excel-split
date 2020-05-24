from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path("api/document/sample", views.SampleExcel.as_view()),
    path("api/document/", views.DocumentCreate.as_view()),
    path("api/document/download/<int:document_id>", views.downloadZip),
]
