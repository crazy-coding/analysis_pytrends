from rest_framework import viewsets, permissions, pagination
from rest_framework.schemas import AutoSchema
from rest_framework.response import Response
from rest_framework.compat import coreapi
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.authtoken.models import Token
from django.db import IntegrityError
from . import serializers, models
from .services.dataingest import DataIngest
from django.http import HttpResponse
import datetime


class CustomViewSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        extra_fields = []
        if path.endswith('/register/'):
            extra_fields = [
                coreapi.Field("name", required=True),
                coreapi.Field("email", required=True),
                coreapi.Field("password", required=True),
            ]
        if path.endswith('/chart/'):
            extra_fields = [
                coreapi.Field("from_date"),
                coreapi.Field("to_date"),
                coreapi.Field("pull_type"),
                coreapi.Field("trend_name"),
                coreapi.Field("trend_type"),
                coreapi.Field("site"),
            ]

        manual_fields = super().get_manual_fields(path, method)
        return manual_fields + extra_fields

class HasPermPage(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm_page(view.basename) if request.user.is_authenticated else False

# ===================================================
class RegisterViewSet(viewsets.ViewSet):
    schema = CustomViewSchema()
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        """ Register. """
        success = True
        error = ''
        try:
            new_user = models.User.objects.create_user(
                email = request.data.get('email'),
                password = request.data.get('password'),
            )
            new_user.name = request.data.get('name')
            try:
                # new_user.group = models.Group.objects.get(name='free')
                print(new_user)
                new_user.save()
            except ObjectDoesNotExist:
                new_user.delete()
                error = 'Please contact our support team.'

            serializer = AuthTokenSerializer(data={'username': request.data.get('email'), 'password': request.data.get('password')}, context={'request': request})
            serializer.is_valid(raise_exception=True)
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            token = token.key
            message = {
                'type': 'success',
                'message': 'Registered successfully.'
            }
        except IntegrityError:
            token = ''
            success = False
            message = {
                'type': 'danger',
                'message': 'Exist email address provided.'
            }
            error = 'Exist email address provided.'

        return Response({ 
            'success': success, 
            'token': token,
            'error': error,
            'message': message,
        })

class UserViewSet(viewsets.ModelViewSet):
    """ User. """
    queryset = models.User.objects.all().order_by('-date_joined')
    serializer_class = serializers.UserSerializer
    permission_classes = [HasPermPage]
    http_method_names = ['get', 'post', 'put', 'delete']

class GroupViewSet(viewsets.ModelViewSet):
    """ Group. """
    queryset = models.Group.objects.all()
    serializer_class = serializers.GroupSerializer
    permission_classes = [HasPermPage]
    http_method_names = ['get', 'post', 'put', 'delete']

class TrendViewSet(viewsets.ModelViewSet):
    """ Trend. """
    queryset = models.Trend.objects.all()
    serializer_class = serializers.TrendSerializer
    http_method_names = ['get', 'post', 'put', 'delete']

class InterestViewSet(viewsets.ModelViewSet):
    """ Interest. """
    queryset = models.Interest.objects.all()
    serializer_class = serializers.InterestSerializer
    http_method_names = ['get']

class ChartViewSet(viewsets.ViewSet):
    schema = CustomViewSchema()
    permission_classes = (permissions.AllowAny,)

    def list(self, request):
        """ Chart data. """
        first_interest = models.Interest.objects.first()
        from_date = request.GET.get('from_date', datetime.datetime.today().strftime('%Y-%m-01'))
        to_date = request.GET.get('to_date', datetime.datetime.today().strftime('%Y-%m-%d'))
        pull_type = request.GET.get('pull_type', 'hour')
        trend_name = request.GET.get('trend_name', first_interest.trend.name)
        trend_type = request.GET.get('trend_type', first_interest.trend.type)
        site = request.GET.get('site', first_interest.trend.site)

        # print([from_date,to_date,pull_type,trend_name,trend_type,site])
        queryset = models.Interest.objects.filter(pull_datetime__gt=from_date, pull_datetime__lt=to_date, pull_type=pull_type, trend__name=trend_name, trend__type=trend_type, trend__site=site).order_by('pull_datetime')
        serializer = serializers.InterestSerializer(queryset, many=True)
        return Response(serializer.data)

def data_ingest(request):
    dataIngest = DataIngest()
    dataIngest.ingest()
    return HttpResponse("Finished")