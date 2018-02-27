from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import translation
from rest_framework.test import APIRequestFactory, APIClient

from demo.models import Article
from demo.static import Root
from django_ontology.models import ontology_models


class RestTestCase(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.client = APIClient()

        staff_user = User(username="staff", email="staff@asdf.se", is_staff=True)
        staff_user.set_password("password")
        staff_user.save()

        user = User(username="regular", email="regular@asdf.se", is_staff=False)
        user.set_password("password")
        user.save()

        Root.load()

    def test_model_urls_avaliable(self):
        for model in ontology_models():
            self.assertTrue(reverse("django_ontology-rest-%s-list" % model.slug))

    def test_list_create(self):
        # translation.activate("sv")
        self.client.login(username="staff", password="password")
        response = self.client.post(
            reverse("django_ontology-rest-article-list"),
            data={"key": "new_concept"}
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Article.translate.filter(key="new_concept").exists())

    def test_list_create_child(self):
        self.client.login(username="staff", password="password")
        response = self.client.post(
            reverse("django_ontology-rest-article-list"),
            data={"key": "new_concept", "parent": "Root"}
        )
        self.assertEqual(response.status_code, 201)
        c = Article.translate.get(key="new_concept")
        self.assertEqual(c.parent_id, "Root")

    def test_list_create_expression(self):
        self.client.login(username="staff", password="password")
        response = self.client.post(
            reverse("django_ontology-rest-article-list"),
            data={"key": "new_concept", "short": "New concept"}
        )
        self.assertEqual(response.status_code, 201)
        c = Article.translate.get(key="new_concept")
        self.assertEqual(str(c.short), "New concept")

    def test_list_create_expression_language(self):
        self.client.login(username="staff", password="password")
        response = self.client.post(
            reverse("django_ontology-rest-article-list") + "?language=sv",
            data={"key": "new_concept", "short": "New concept"}
        )
        self.assertEqual(response.status_code, 201)
        c = Article.translate.get(key="new_concept", language="sv")

        self.assertEqual(str(c.short), "New concept")

    def test_update_concept(self):
        Article.objects.create(key="new_article")
        self.client.login(username="staff", password="password")
        response = self.client.put(
            reverse("django_ontology-rest-article-detail", kwargs=dict(pk="new_article")) + "?language=sv",
            data={"key": "new_article", "short": "Updated short"}
        )
        self.assertEqual(response.status_code, 200)
        a = Article.translate.get(key="new_article", language="sv")
        self.assertEqual(str(a.short), "Updated short")


