from rest_framework import permissions


class IsAdminUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == 'POST':
            return request.user.is_authenticated
        return True
        if request.method in permissions.SAFE_METHODS:
            return (request.user.is_admin
                    or request.user.is_admin)


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )


class IsSubscribeOnly(permissions.BasePermission):
    """Разрешает удаление только для действий с подписками."""
    def has_permission(self, request, view):
        return view.action == 'subscribe'
