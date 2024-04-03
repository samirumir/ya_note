from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.contrib import auth
from django.shortcuts import redirect
from django.test import Client, TestCase
from django.urls import reverse
from yanote.wsgi import *

from unittest import skip

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Создатель')
        cls.reader = User.objects.create(username='Человек простой')

        cls.notes = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author)

    # @skip("bla bla")
    def test_availability_firsts_for_anonymous(self):
        """Главная страница, авторизация и регистрация и выход доступны
          всем пользователям"""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.client, HTTPStatus.OK)
            )
        for user, status in users_statuses:
            if user == self.author:
                self.client.force_login(user)
            for name in (
                'notes:home',
                'users:login',
                'users:logout',
                ):
                with self.subTest(user=user, name=name):
                    url = reverse(name)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    # @skip("bla bla")
    def test_availability_for_authorized_client(self):
        """Аутентифицированному пользователю доступна страницы
        notes:list, note:success, notes:add"""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in (
                'notes:list',
                'notes:success',
                'notes:add',
                ):
                with self.subTest(user=user, name=name):
                    url = reverse(name)
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    # @skip("bla bla")
    def test_availability_for_note_edit_and_delete(self):
        """Проверка на редактирование(удаление) авторизованному
         и неавторизованнуому пользователю"""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in (
                'notes:edit',
                'notes:delete',
                'notes:detail',
                ):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.notes.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    # @skip("bla bla")
    def test_redirect_for_anonymous_client(self):
        """Редирект неавторизованных пользователей на страницу регистрации"""
        login_url = reverse('users:login')
        for name in (
            'notes:edit',
            'notes:delete',
            'notes:detail',
            ):
            with self.subTest(name=name):
                url = reverse(name, args=(self.notes.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
        for name in (
            'notes:add',
            'notes:success',
            'notes:list',
            ):
            with self.subTest(name=name):
                url = reverse(name)
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)
