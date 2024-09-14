from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework.views import APIView

from projects.models import Project, Category
from .filters import ProjectFilter
from .serializers import ProjectSerializer, CategorySerializer
from rest_framework.permissions import IsAuthenticated


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    filter_backends = [DjangoFilterBackend]
    filterset_class = ProjectFilter

    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)


class ProjectCategoryListView(APIView):
    serializer_class = CategorySerializer
    # return 8 categories
    queryset = Category.objects.all()[:8]

    def get(self, request):
        serializer = CategorySerializer(self.queryset, many=True)
        return Response(serializer.data, status=200)
