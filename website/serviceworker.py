from django.http import FileResponse
import os
from django.conf import settings

def service_worker(request):
    path = os.path.join(settings.BASE_DIR, "website", "static", "js", "serviceworker.js")
    return FileResponse(open(path, "rb"), content_type="application/javascript")