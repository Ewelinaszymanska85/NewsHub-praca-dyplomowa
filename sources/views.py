from rest_framework import viewsets
from drf_spectacular.utils import extend_schema
from .models import Source
from .serializers import SourceSerializer


@extend_schema(tags=["Źródła RSS"])
class SourceViewSet(viewsets.ModelViewSet):
    """
    API endpoint do przeglądania i zarządzania źródłami RSS.
    """
    queryset = Source.objects.all()
    serializer_class = SourceSerializer 