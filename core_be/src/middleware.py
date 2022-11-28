from django.db import connections
from django.db.utils import OperationalError
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin


class HealthCheckMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.META["PATH_INFO"] == "/ping/":
            return HttpResponse("pong")

        if request.META["PATH_INFO"] == "/dbping/":  # Health check db connection
            db_conn = connections["default"]
            try:
                c = db_conn.cursor()
            except OperationalError:
                """Connection Failed"""
            else:
                return HttpResponse("pong")
