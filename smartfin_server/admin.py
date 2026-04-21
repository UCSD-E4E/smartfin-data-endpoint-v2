from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from .models import EnsembleReading

@admin.register(EnsembleReading)
class EnsembleReadingAdmin(admin.ModelAdmin):
    list_display = ('ensemble_type', 'temperature', 'geo_coordinates', 'timestamp')
    list_filter = ('ensemble_type', 'timestamp')
    search_fields = ('geo_coordinates', 'water_status')

    # Custom dashboard link in admin
    change_list_template = "admin/ensemble_reading_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('heatmap/', self.admin_site.admin_view(self.heatmap_view), name='smartfin-heatmap'),
        ]
        return custom_urls + urls

    def heatmap_view(self, request):
        # Filtering for the current week
        last_week = timezone.now() - timedelta(days=7)
        # We need readings with geo_coordinates for the heatmap
        readings = EnsembleReading.objects.filter(
            timestamp__gte=last_week
        ).exclude(geo_coordinates__isnull=True).exclude(geo_coordinates="")

        heatmap_data = []
        for r in readings:
            try:
                # Assuming format "lat, lon"
                lat, lon = map(float, r.geo_coordinates.split(','))
                heatmap_data.append({
                    'lat': lat,
                    'lng': lon,
                    'temp': r.temperature or 0
                })
            except (ValueError, AttributeError):
                continue

        context = {
            **self.admin_site.each_context(request),
            'heatmap_data': heatmap_data,
            'title': 'SmartFin Temperature Heatmap (Current Week)'
        }
        return render(request, 'admin/heatmap.html', context)
