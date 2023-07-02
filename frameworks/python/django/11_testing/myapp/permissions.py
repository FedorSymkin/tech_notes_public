from rest_framework import permissions


# Доступы в rest api огранизованы через permission классы, которые указываются во view.


class IsOwnerOrReadOnly(permissions.BasePermission):
    # Здесь мы делаем свой кастомный permission класс для Retrieve, Update, Delete, который
    # либо разрешает доступ всем в случае только чтения (SAFE_METHODS это 'GET', 'HEAD', 'OPTIONS')
    # либо, в случае записи (POST, PUT, PATCH) проверяет, является ли текущий пользователь автором
    # изменяемого объекта.
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return obj.author == request.user
