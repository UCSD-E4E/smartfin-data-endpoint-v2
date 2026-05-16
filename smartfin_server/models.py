from django.db import models
from django.contrib.auth.models import User

class EnsembleReading(models.Model):
    ENSEMBLE_CHOICES = [
        ('01', 'Temperature and Water Status (Low Power)'),
        ('11', 'Full Set (Temp, Water, 9-axis IMU, GPS)'),
        ('12', 'High Data Rate IMU'),
    ]

    session = models.ForeignKey('Session', on_delete=models.CASCADE, related_name="ensembles")
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

class Session(models.Model):
    client_session_id = models.CharField(max_length=100, unique=True)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    
    @property
    def duration(self):
        if self.ended_at and self.started_at:
            return (self.ended_at - self.started_at).total_seconds()
        return None

    @property
    def avg_tmp(self):
        ensembles = self.ensembles.all()
        temps = [e.temperature for e in ensembles if e.temperature is not None]
        return sum(temps) / len(temps) if temps else None

    @property
    def num_ensembles(self):
        return self.ensembles.count()

    def __str__(self):
        return f"Session {self.client_session_id}: ({self.started_at} - {self.ended_at})"
