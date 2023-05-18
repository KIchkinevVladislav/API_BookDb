from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Restriction of rights. Actions are available only to the admin or django admin.
    """

    message = 'Не хватает прав, нужны права Администратора'

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.is_superuser or request.user.role == 'admin'

        
class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Restriction of rights. Actions are available only to the admin or django admin or only reading.
    """

    message = 'Не хватает прав, нужны права Администратора'

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated:
            return request.user.is_superuser or request.user.role == 'admin'

        
class IsAuthorOrAdminOrModerator(permissions.BasePermission):
    """
    Restriction of rights. 
    Actions are available only to the admin or moderator or author.
    """
    message = 'Не хватает прав'

    def has_object_permission(self, request, view, obj):
        if request.method == 'POST':
            return not request.user.is_anonymous()

        if request.method in ('PATCH', 'DELETE'):
            return(
                request.user == obj.author
                or request.user.role == 'admin'
                or request.user.role == 'moderator'
            )

        if request.method in permissions.SAFE_METHODS:
            return True
        return False

    
