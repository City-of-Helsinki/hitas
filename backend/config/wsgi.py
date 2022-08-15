"""
WSGI config for config project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
from io import StringIO

from django.conf import settings
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()


#
# Hot warmup
#
if settings.UWSGI_WARMUP:
    print("Running uwsgi warmup...")

    def noop(status, hh, exc_info=None):
        pass

    application(
        {
            "CONTENT_LENGTH": "",
            "CONTENT_TYPE": "",
            "DOCUMENT_ROOT": "/etc/nginx/html",
            "HTTP_HOST": "example.com",
            "PATH_INFO": "/healthz",
            "QUERY_STRING": "",
            "REMOTE_ADDR": "127.0.0.1",
            "REMOTE_PORT": "12345",
            "REQUEST_METHOD": "GET",
            "REQUEST_URI": "/healthz",
            "SERVER_NAME": "example.com",
            "SERVER_PORT": "80",
            "SERVER_PROTOCOL": "HTTP/1.1",
            "uwsgi.node": "f939bd542267",
            "uwsgi.version": "2.0.22",
            "wsgi.multiprocess": True,
            "wsgi.multithread": False,
            "wsgi.run_once": False,
            "wsgi.url_scheme": "http",
            "wsgi.version": (1, 0),
            "wsgi.input": StringIO(),
            "wsgi.errors": StringIO(),
        },
        noop,
    )
