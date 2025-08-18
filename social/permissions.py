from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """Allows edits only by the object's owner (expects `author` attribute)."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        author = getattr(obj, "author", None)
        return author == request.user
