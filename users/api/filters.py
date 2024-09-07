from rest_framework.filters import BaseFilterBackend


class SelfFilterBacked(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        """
        Filter the queryset to only show the user's own data.
        """
        queryset = queryset.filter(username=request.user.username)
        return queryset
