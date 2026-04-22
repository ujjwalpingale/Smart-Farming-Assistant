from django.contrib import admin
from .models import CropInput, FertilizerInput, DiseaseInput

admin.site.register(CropInput)
admin.site.register(FertilizerInput)
admin.site.register(DiseaseInput)
