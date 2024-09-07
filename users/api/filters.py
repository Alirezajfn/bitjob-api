from rest_framework.filters import BaseFilterBackend


class SelfFilterBacked(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        queryset = queryset.filter(id=request.user.id)
        return queryset
