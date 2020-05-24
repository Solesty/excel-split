
from rest_framework.response import Response
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission, Group


from rest_framework.views import exception_handler


def formatResponse(data, status_code, is_error=False):
    if not is_error:
        return Response(data={"data": data}, status=status_code)
    else:
        return Response(data={"data": {"error": data}}, status=status_code)
