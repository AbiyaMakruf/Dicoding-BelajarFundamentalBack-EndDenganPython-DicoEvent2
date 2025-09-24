from rest_framework import permissions

class IsAdminOrSuperUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and (
            request.user.is_superuser or request.user.groups.filter(name="admin").exists()
        )

class IsOrganizerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.organizer == request.user

class IsOrganizerOfEvent(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_superuser or request.user.groups.filter(name="admin").exists():
            return True
        return obj.event.organizer == request.user

class IsOwnerOrAdminOrOrganizer(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.groups.filter(name="admin").exists():
            return True
        if request.user.groups.filter(name="organizer").exists():
            return obj.ticket.event.organizer == request.user
        return obj.user == request.user

class IsOwnerOrAdminOrOrganizerPayment(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.groups.filter(name="admin").exists():
            return True
        if request.user.groups.filter(name="organizer").exists():
            return obj.registration.ticket.event.organizer == request.user
        return obj.registration.user == request.user
