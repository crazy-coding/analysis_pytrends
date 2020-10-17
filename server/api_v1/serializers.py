from . import models
from rest_framework import serializers
from rest_framework.authtoken.models import Token


class CustomSerializer(serializers.ModelSerializer):
    def get_field_names(self, declared_fields, info):
        expanded_fields = super(CustomSerializer, self).get_field_names(declared_fields, info)

        if getattr(self.Meta, 'extra_fields', None):
            return expanded_fields + self.Meta.extra_fields
        else:
            return expanded_fields

# ===================================================
class GroupSerializer(CustomSerializer):
    class Meta:
        model = models.Group
        fields = '__all__'

class TokenSerializer(CustomSerializer):
    class Meta:
        model = Token
        fields = '__all__'

class UserSerializer(CustomSerializer):
    group = GroupSerializer(read_only=True)
    token = TokenSerializer(read_only=True)

    class Meta:
        model = models.User
        fields = '__all__'
        extra_fields = ['token']

class TrendSerializer(CustomSerializer):
    class Meta:
        model = models.Trend
        fields = '__all__'

class InterestSerializer(CustomSerializer):
    trend = TrendSerializer(read_only=True)

    class Meta:
        model = models.Interest
        fields = '__all__'