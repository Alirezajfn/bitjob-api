import django_filters
from projects.models import Project


class ProjectFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name='category__id')

    tags = django_filters.ModelMultipleChoiceFilter(queryset=Project.objects.all())

    min_budget = django_filters.NumberFilter(field_name='budget', lookup_expr='gte')
    max_budget = django_filters.NumberFilter(field_name='budget', lookup_expr='lte')

    deadline_after = django_filters.DateFilter(field_name='deadline', lookup_expr='gte')
    deadline_before = django_filters.DateFilter(field_name='deadline', lookup_expr='lte')

    class Meta:
        model = Project
        fields = ['category', 'tags', 'status', 'min_budget', 'max_budget', 'deadline_after', 'deadline_before']
