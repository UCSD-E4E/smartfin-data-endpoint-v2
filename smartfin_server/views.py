import os
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, StreamingHttpResponse, JsonResponse
from django.shortcuts import render
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync
from django.contrib.auth.decorators import login_required



import json
from .models import EnsembleReading

@csrf_exempt
def upload(request):
    """
    Handles data uploads from SmartFin.
    Expected data structure:
    POST /api/upload
    {
        "ensemble_type": "01" | "11" | "12",
        "temperature": 18.5,
        "water_status": "in_water",
        "gps": "34.05,-118.24", (for ensemble 11)
        "imu": {...} | [...] (for ensemble 11 or 12)
    }
    """
    if request.method == "POST":
        try:
            # Handle both JSON and traditional POST data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST

            ensemble_type = data.get("ensemble_type")
            if not ensemble_type:
                return HttpResponse("Missing ensemble_type", status=400)

            # Create the reading using the available data
            reading = EnsembleReading.objects.create(
                ensemble_type=ensemble_type,
                temperature=data.get("temperature"),
                water_status=data.get("water_status") or data.get("status"),
                geo_coordinates=data.get("gps") or data.get("geo_coordinates"),
                imu_data=data.get("imu") or data.get("imu_data")
            )

            print(f"Stored {reading}")
            return JsonResponse({"status": "success", "id": reading.id})

        except Exception as e:
            print(f"Upload error: {e}")
            return HttpResponse(f"Error processing upload: {e}", status=500)

    return HttpResponse("Invalid request method", status=405)


# Ensemble 01: Just Temperature and Water status (low power).
# Ensemble 11: The "Full" set including Temp, Water, 9-axis IMU, and GPS (used during active surfing).
# Ensemble 12: High Data Rate IMU, which provides much higher frequency motion data specifically for advanced wave-shape analysis.