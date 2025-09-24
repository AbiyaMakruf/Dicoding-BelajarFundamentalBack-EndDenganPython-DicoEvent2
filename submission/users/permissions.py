from rest_framework import permissions

class UserPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == "create":
            return True

        if not request.user or not request.user.is_authenticated:
            return False

        if request.user.is_superuser:
            return True

        if request.user.groups.filter(name="admin").exists():
            return view.action in ["list", "retrieve"]

        if view.action in ["retrieve", "update", "partial_update", "destroy"]:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True

        if request.user.groups.filter(name="admin").exists():
            return view.action in ["retrieve"]

        return obj == request.user

