from django.db import models
from django.contrib.auth.models import User

class EnsembleReading(models.Model):
    ENSEMBLE_CHOICES = [
        ('01', 'Temperature and Water Status (Low Power)'),
        ('11', 'Full Set (Temp, Water, 9-axis IMU, GPS)'),
        ('12', 'High Data Rate IMU'),
    ]

    ensemble_type = models.CharField(max_length=2, choices=ENSEMBLE_CHOICES)
    temperature = models.FloatField(null=True, blank=True)
    water_status = models.CharField(max_length=100, null=True, blank=True)
    geo_coordinates = models.CharField(max_length=100, null=True, blank=True)
    
    # Store IMU data as JSON for flexibility (9-axis or high-rate arrays)
    imu_data = models.JSONField(null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Ensemble {self.ensemble_type} at {self.timestamp}"


class Video(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name="user_video")
    video = models.FileField(upload_to='video/')
