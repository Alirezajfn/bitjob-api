from drf_spectacular.utils import extend_schema, OpenApiParameter
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


class CategoryListAPIView(APIView):

    @extend_schema(
        parameters=[
            OpenApiParameter(name='limit', description='Limit the number of categories returned', required=False, type=int),
        ],
        responses=CategorySerializer(many=True)
    )
    def get(self, request, *args, **kwargs):
        limit = request.query_params.get('limit', None)
        if limit:
            limit = int(limit)
            categories = Category.objects.all()[:limit]
        else:
            categories = Category.objects.all()

        serializer = CategorySerializer(categories, many=True)

        return Response(serializer.data)
