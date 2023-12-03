from django.shortcuts import get_object_or_404
from rest_framework import serializers, status
from rest_framework.response import Response


class AbstractCreateDeleteMixin():
    """Абстрактный класс миксин, содержащий методы для добавления и
    удаления объектов."""

    # Метод выполняет операции добавления и удаления объектов
    def perform_action(self, model, object, serializer, request, pk,
                       keyword, mess_fail_add, mess_fail_no_exists):
        user = request.user
        obj = get_object_or_404(object, id=pk)

        if request.method == 'POST':
            if model.objects.filter(
                user=user,
                **{keyword: obj}
            ).exists():
                raise serializers.ValidationError(
                    {'message': mess_fail_add}
                )
            model.objects.create(user=user, **{keyword: obj})
            ser = serializer(
                obj,
                context={'request': request}
            )
            return Response(ser.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            if not model.objects.filter(
                user=user,
                **{keyword: obj}
            ).exists():
                raise serializers.ValidationError(
                    {'message': mess_fail_no_exists}
                )
            model.objects.get(user=user, **{keyword: obj}).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
