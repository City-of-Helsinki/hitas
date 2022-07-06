from django.http import JsonResponse
from health_check.views import MainView


class HealthCheckView(MainView):
    def get(self, request, *args, **kwargs):
        status_code = 500 if self.errors else 200
        return JsonResponse(
            {"status": ("ok" if status_code == 200 else "error")},
            status=status_code,
        )
