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
from .models import EnsembleReading, Session

@csrf_exempt
def get_ensembles(request):
    """
    Returns a list of all ensembles
    GET /api/ensembles
    """
    if request.method == "GET":
        try:
            ensembles = EnsembleReading.objects.all()
            data = [
                {
                    "id": ensemble.id,
                    "session_id": ensemble.session.client_session_id,
                    "ensemble_type": ensemble.ensemble_type,
                    "temperature": ensemble.temperature,
                    "water_status": ensemble.water_status,
                    "gps": ensemble.geo_coordinates,
                    "imu": ensemble.imu_data
                }
                for ensemble in ensembles
            ]
            return JsonResponse(data, safe=False)
        except Exception as e:
            print(f"Error fetching ensembles: {e}")
            return HttpResponse(f"Error fetching ensembles: {e}", status=500)

    return HttpResponse("Invalid request method", status=405)

@csrf_exempt
def get_ensemble(request, ensemble_id):
    """
    Returns details of a specific ensemble.
    GET /api/ensembles/<ensemble_id>
    """
    if request.method == "GET":
        try:
            ensemble = EnsembleReading.objects.get(pk=ensemble_id)
            data = {
                "id": ensemble.id,
                "session_id": ensemble.session.client_session_id,
                "ensemble_type": ensemble.ensemble_type,
                "temperature": ensemble.temperature,
                "water_status": ensemble.water_status,
                "gps": ensemble.geo_coordinates,
                "imu": ensemble.imu_data
            }
            return JsonResponse(data)
        except EnsembleReading.DoesNotExist:
            return HttpResponse("Ensemble not found", status=404)
        except Exception as e:
            print(f"Error fetching ensemble: {e}")
            return HttpResponse(f"Error fetching ensemble: {e}", status=500)
        
    return HttpResponse("Invalid request method", status=405)

@csrf_exempt
def create_ensemble(request):
    """
    Handles data uploads from SmartFin.
    Expected data structure:
    POST /api/upload
    {
        "session_id": "session_id", this should be the primary key of the Session object in the database
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

            # Check it has the required fields
            ensemble_type = data.get("ensemble_type")
            if not ensemble_type:
                return HttpResponse("Missing ensemble_type", status=400)
            session_id = data.get("session_id")
            if not session_id:
                return HttpResponse("Missing session_id", status=400)

            # Create the reading using the available data
            reading = EnsembleReading.objects.create(
                session_id=Session.objects.get(pk=session_id),
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

@csrf_exempt
def get_sessions(request):
    """
    Returns a list of all sessions.
    GET /api/sessions
    Response:
    [
        {
            "id": 1,
            "client_session_id": "unique_session_id",
            "started_at": "2023-01-01T00:00:00Z",
            "ended_at": "2023-01-01T01:00:00Z",
            "duration": 3600,
            "avg_tmp": 60.5,
            "num_ensembles": 100
        },
        ...
    ]
    """
    if request.method == "GET":
        sessions = Session.objects.all()
        data = []
        for session in sessions:
            data.append({
                "id": session.id,
                "client_session_id": session.client_session_id,
                "started_at": session.started_at.isoformat(),
                "ended_at": session.ended_at.isoformat(),
                "duration": session.duration,
                "avg_tmp": session.avg_tmp,
                "num_ensembles": session.num_ensembles
            })
        return JsonResponse(data, safe=False)

    return HttpResponse("Invalid request method", status=405)

@csrf_exempt
def get_session(request, session_id):
    """
    Returns details of a specific session.
    GET /api/sessions/<session_id>
    Response:
    {
        "id": 1,
        "client_session_id": "unique_session_id",
        "started_at": "2023-01-01T00:00:00Z",
        "ended_at": "2023-01-01T01:00:00Z",
        "duration": 3600,
        "avg_tmp": 60.5,
        "num_ensembles": 100,
        "ensembles": [
            {
                "id": 1,
                "ensemble_type": "11",
                "temperature": 18.5,
                "water_status": "in_water",
                "geo_coordinates": "34.05,-118.24",
                "imu_data": {...},
                "timestamp": "2023-01-01T00:30:00Z"
            },
            ...
        ]
    }
    """
    if request.method == "GET":
        try:
            session = Session.objects.get(pk=session_id)
            ensembles = session.ensembles.all()
            ensemble_data = []
            for e in ensembles:
                ensemble_data.append({
                    "id": e.id,
                    "ensemble_type": e.ensemble_type,
                    "temperature": e.temperature,
                    "water_status": e.water_status,
                    "geo_coordinates": e.geo_coordinates,
                    "imu_data": e.imu_data,
                    "timestamp": e.timestamp.isoformat()
                })
            data = {
                "id": session.id,
                "client_session_id": session.client_session_id,
                "started_at": session.started_at.isoformat(),
                "ended_at": session.ended_at.isoformat(),
                "duration": session.duration,
                "avg_tmp": session.avg_tmp,
                "num_ensembles": session.num_ensembles,
                "ensembles": ensemble_data
            }
            return JsonResponse(data)

        except Session.DoesNotExist:
            return HttpResponse("Session not found", status=404)

    return HttpResponse("Invalid request method", status=405)


@csrf_exempt
def create_session(request):
    """
    Handles session creation.
    Expected data structure:
    POST /api/sessions
    {
        "client_session_id": "unique_session_id",
        "started_at": "2023-01-01T00:00:00Z",
        "ended_at": "2023-01-01T01:00:00Z"
    }
    """
    if request.method == "POST":
        try:
            # Handle both JSON and traditional POST data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST

            # Check it has the required fields
            client_session_id = data.get("client_session_id")
            if not client_session_id:
                return HttpResponse("Missing client_session_id", status=400)

            started_at = data.get("started_at")
            if not started_at:
                return HttpResponse("Missing started_at", status=400)

            ended_at = data.get("ended_at")
            if not ended_at:
                return HttpResponse("Missing ended_at", status=400)

            # Create the session using the available data
            session = Session.objects.create(
                client_session_id=client_session_id,
                started_at=started_at,
                ended_at=ended_at
            )

            print(f"Stored {session}")
            return JsonResponse({"status": "success", "id": session.id})

        except Exception as e:
            print(f"Upload error: {e}")
            return HttpResponse(f"Error processing upload: {e}", status=500)

    return HttpResponse("Invalid request method", status=405)

# Ensemble 01: Just Temperature and Water status (low power).
# Ensemble 11: The "Full" set including Temp, Water, 9-axis IMU, and GPS (used during active surfing).
# Ensemble 12: High Data Rate IMU, which provides much higher frequency motion data specifically for advanced wave-shape analysis.