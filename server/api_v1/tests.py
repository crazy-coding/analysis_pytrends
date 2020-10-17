from django.test import TestCase
from rest_framework.authtoken.serializers import AuthTokenSerializer
from . import models


class UserGroupTestCase(TestCase):
    def setUp(self):
        admin_group = models.Group.objects.create(name="admin", permission_page="user,group")
        client_group = models.Group.objects.create(name="client", permission_page="")

        admin_user = models.User.objects.create_user(email="admin1@test.com", password="admin")
        admin_user.name = "Administrator1"
        admin_user.group = admin_group
        admin_user.save()
        client_user = models.User.objects.create_user(email="client1@test.com", password="client")
        client_user.name = "Client1"
        client_user.group = client_group
        client_user.save()

    def test_group_created(self):
        """[Testing] Group Model Create"""
        self.assertEqual(models.Group.objects.get(name="admin").name, "admin")
        self.assertEqual(models.Group.objects.get(name="client").name, "client")

    def test_user_created(self):
        """[Testing] User Model Create"""
        self.assertEqual(models.User.objects.get(name="Administrator1").name, "Administrator1")
        self.assertEqual(models.User.objects.get(name="Client1").name, "Client1")

    def test_user_group_relations(self):
        """[Testing] Relation with User and Group models"""
        admin_group = models.Group.objects.get(name="admin")
        admin_user = models.User.objects.get(name="Administrator1")
        client_group = models.Group.objects.get(name="client")
        client_user = models.User.objects.get(name="Client1")
        self.assertEqual(admin_user.group, admin_group)
        self.assertEqual(client_user.group, client_group)

    def test_auth_token(self):
        """[Testing] Authenticate with username and password"""
        admin_user = models.User.objects.get(name="Administrator1")

        serializer = AuthTokenSerializer(data={'username': "admin1@test.com", 'password': "admin"})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        self.assertEqual(admin_user, user)
        