import json
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.models import Token

from .models import EnsembleReading

ENSEMBLE_TYPE_LABELS = {
    '01': 'Temperature and Water Status (Low Power)',
    '11': 'Full Set (Temp, Water, 9-axis IMU, GPS)',
    '12': 'High Data Rate IMU',
}


def _get_user_from_token(request):
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if not auth_header.startswith('Token '):
        return None
    token_key = auth_header[6:]
    try:
        return Token.objects.get(key=token_key).user
    except Token.DoesNotExist:
        return None


@csrf_exempt
def register(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    username = data.get('username', '').strip()
    password = data.get('password', '')
    if not username or not password:
        return JsonResponse({'error': 'username and password are required'}, status=400)

    try:
        user = User.objects.create_user(username=username, password=password)
    except IntegrityError:
        return JsonResponse({'error': 'Username already taken'}, status=409)

    token, _ = Token.objects.get_or_create(user=user)
    return JsonResponse({'token': token.key, 'user_id': user.id, 'username': user.username}, status=201)


@csrf_exempt
def login_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user = authenticate(username=data.get('username', ''), password=data.get('password', ''))
    if user is None:
        return JsonResponse({'error': 'Invalid credentials'}, status=401)

    token, _ = Token.objects.get_or_create(user=user)
    return JsonResponse({'token': token.key, 'user_id': user.id, 'username': user.username})


@csrf_exempt
def upload(request):
    """
    POST /api/upload
    Header: Authorization: Token <token>
    Body (JSON):
      ensemble_type  required  "01" | "11" | "12"
      temperature    optional  float (°C)
      water_status   optional  "in_water" | "dry"
      gps            optional  "lat,lon"
      imu            optional  object or array
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    user = _get_user_from_token(request)
    if user is None:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    try:
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            data = request.POST

        ensemble_type = data.get('ensemble_type')
        if not ensemble_type:
            return JsonResponse({'error': 'Missing ensemble_type'}, status=400)

        reading = EnsembleReading.objects.create(
            user=user,
            ensemble_type=ensemble_type,
            temperature=data.get('temperature'),
            water_status=data.get('water_status') or data.get('status'),
            geo_coordinates=data.get('gps') or data.get('geo_coordinates'),
            imu_data=data.get('imu') or data.get('imu_data'),
        )

        return JsonResponse({'status': 'success', 'id': reading.id}, status=201)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def user_data(request):
    """
    GET /api/data/
    Header: Authorization: Token <token>
    Query params (all optional):
      type    "01" | "11" | "12"  filter by ensemble type
      from    YYYY-MM-DD          filter readings on or after this date
      to      YYYY-MM-DD          filter readings on or before this date
      limit   int (default 100, max 1000)
      offset  int (default 0)
    """
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    user = _get_user_from_token(request)
    if user is None:
        return JsonResponse({'error': 'Authentication required'}, status=401)

    qs = EnsembleReading.objects.filter(user=user).order_by('-timestamp')

    ensemble_type = request.GET.get('type')
    if ensemble_type:
        qs = qs.filter(ensemble_type=ensemble_type)

    date_from = request.GET.get('from')
    date_to = request.GET.get('to')
    if date_from:
        qs = qs.filter(timestamp__date__gte=date_from)
    if date_to:
        qs = qs.filter(timestamp__date__lte=date_to)

    try:
        limit = min(int(request.GET.get('limit', 100)), 1000)
        offset = int(request.GET.get('offset', 0))
    except ValueError:
        return JsonResponse({'error': 'Invalid pagination parameters'}, status=400)

    total = qs.count()
    page = qs[offset:offset + limit]

    return JsonResponse({
        'user': user.username,
        'total_readings': total,
        'limit': limit,
        'offset': offset,
        'readings': [
            {
                'id': r.id,
                'ensemble_type': r.ensemble_type,
                'ensemble_type_label': ENSEMBLE_TYPE_LABELS.get(r.ensemble_type, r.ensemble_type),
                'temperature': r.temperature,
                'water_status': r.water_status,
                'geo_coordinates': r.geo_coordinates,
                'imu_data': r.imu_data,
                'timestamp': r.timestamp.isoformat(),
            }
            for r in page
        ],
    })


# Ensemble 01: Just Temperature and Water status (low power).
# Ensemble 11: The "Full" set including Temp, Water, 9-axis IMU, and GPS (used during active surfing).
# Ensemble 12: High Data Rate IMU, which provides much higher frequency motion data specifically for advanced wave-shape analysis.
