import os
import django
import random
from django.utils import timezone
from datetime import timedelta

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartfin_server.settings')
django.setup()

from smartfin_server.models import EnsembleReading

def seed_data():
    print("Seeding mock SmartFin data...")
    # Base location (e.g., San Diego area as it's common for SmartFin)
    base_lat, base_lon = 32.8, -117.2
    
    ensembles = ['01', '11', '12']
    
    for i in range(50):
        # Data within the last 7 days
        days_ago = random.randint(0, 6)
        hours_ago = random.randint(0, 23)
        timestamp = timezone.now() - timedelta(days=days_ago, hours=hours_ago)
        
        # Slight variation in location
        lat = base_lat + (random.random() - 0.5) * 0.2
        lon = base_lon + (random.random() - 0.5) * 0.2
        
        # Temperature varying with location (hotter south/inland for this mock)
        temp = 15.0 + (33.0 - lat) * 10.0 + random.random() * 2.0
        
        ensemble = random.choice(ensembles)
        
        EnsembleReading.objects.create(
            ensemble_type=ensemble,
            temperature=round(temp, 2),
            water_status="in_water" if random.random() > 0.2 else "dry",
            geo_coordinates=f"{lat},{lon}",
            imu_data={"accel": [random.random() for _ in range(3)]} if ensemble != '01' else None,
            timestamp=timestamp
        )

    print("Success: 50 mock readings created.")

if __name__ == "__main__":
    seed_data()
