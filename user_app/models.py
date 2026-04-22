from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class CropInput(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nitrogen = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(200)])
    phosphorus = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(200)])
    potassium = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(200)])
    temperature = models.FloatField(validators=[MinValueValidator(-50), MaxValueValidator(60)])
    humidity = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    ph = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(14)])
    rainfall = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(500)])
    result = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Crop Prediction - {self.result}"

class FertilizerInput(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nitrogen = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(200)])
    phosphorus = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(200)])
    potassium = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(200)])
    recommended_fertilizer = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Fertilizer - {self.recommended_fertilizer}"


class DiseaseInput(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    crop_name = models.CharField(max_length=50)
    symptoms = models.TextField()
    disease_name = models.CharField(max_length=100)
    prevention = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Disease - {self.disease_name}"
