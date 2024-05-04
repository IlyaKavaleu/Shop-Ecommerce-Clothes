from rest_framework import serializers
from .models import MyUser, StateUserInTelegramBot


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = MyUser.objects.create_user(**validated_data)
        return user


class StateUserModelInTelegramBotSerializer(serializers.ModelSerializer):
    class Meta:
        model = StateUserInTelegramBot
        fields = ['STATE_USER', 'user']
