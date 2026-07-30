from rest_framework import viewsets
from .models import Source
from .serializers import SourceSerializer


class SourceViewSet(viewsets.ModelViewSet):
    """
    API endpoint do przeglądania i zarządzania źródłami RSS.
    """
    queryset = Source.objects.all()
    serializer_class = SourceSerializer 