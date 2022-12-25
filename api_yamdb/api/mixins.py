"""
Миксины и кастомные вьюсеты приложения api.
"""

from rest_framework import mixins, status, viewsets
from rest_framework.response import Response


class PartialUpdateModelMixin:
    """Миксин для частичного обновления модели."""
    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ListCreateDestroyViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """
    Кастомный вьюсет для просмотра, создания и
    удаления экземпляров класса.
    """
    pass


class NotPUTViewSet(
    mixins.ListModelMixin,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
    PartialUpdateModelMixin,
    viewsets.GenericViewSet
):
    """
    Кастомный вьюсет для просмотра, создания,
    частичного обновления и удаления экземпляров
    класса. Не поддерживает метод PUT.
    """
    pass
