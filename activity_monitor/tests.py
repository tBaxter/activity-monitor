import unittest

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase


class TestActivityViews(TestCase):
    # authtestdata.json is pulled from django.contrib.auth for some basic users
    fixtures = ['auth_users.json']

    def setUp(self):
        self.user = get_user_model().objects.all()[0]

    def test_action_archive(self):
        """
        Test archive
        """
        resp = self.client.get(reverse('action_archive'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('object_list' in resp.context)

    def test_action_archive_for_user(self):
        """
        Test archive for user
        """
        resp = self.client.get(reverse('action_archive_for_user', args=[self.user.username]))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('object_list' in resp.context)

    def test_actions_for_today(self):
        """
        Test archive for today
        """
        resp = self.client.get(reverse('actions_for_today'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('object_list' in resp.context)

    def test_actions_for_day(self):
        """
        Test archive for day
        """
        resp = self.client.get(reverse('actions_for_day', args=[2014, 12, 25]))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('object_list' in resp.context)

    def test_actions_for_month(self):
        """
        Test archive for month
        """
        resp = self.client.get(reverse('actions_for_month', args=[2014, 12]))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('object_list' in resp.context)

    def test_actions_for_year(self):
        """
        Test archive for year
        """
        resp = self.client.get(reverse('actions_for_year', args=[2014]))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('object_list' in resp.context)
