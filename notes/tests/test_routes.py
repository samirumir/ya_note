from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.shortcuts import redirect
from django.test import TestCase
from django.urls import reverse
from yanote.wsgi import *

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

    def test_availability_homepage_for_anonymous(self):
        """Главная страница доступна анонимному пользователю"""
        pass


    def test_availability_for_authorized_client(self):
        """Аутентифицированному пользователю доступна страницы
        notes:list, note:done, nots:add"""
        pass


    def test_availability_for_note_edit_and_delete(self):
        """Проверка на редактирование(удаление) авторизованному
         и неавторизованнуому пользователю"""
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            # Логиним пользователя в клиенте:
            self.client.force_login(user)
            # Для каждой пары "пользователь - ожидаемый ответ"
            # перебираем имена тестируемых страниц:
            for name in ('notes:edit', 'notes:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.notes.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)


    def test_redirect_for_anonymous_client(self):
        """Редирект неавторизованных пользователей на страницу регистрации"""
        login_url = reverse('users:login')
        for name in (
            'notes:edit',
            'notes:delete',
            'notes:done',
            'notes:add',
            'notes:detail',
            'notes:list',
            'notes:success',
            ):
            with self.subTest(name=name):
                # Получаем адрес страницы редактирования или удаления комментария:
                url = reverse(name, args=(self.notes.slug,))
                # Получаем ожидаемый адрес страницы логина,
                # на который будет перенаправлен пользователь.
                # Учитываем, что в адресе будет параметр next, в котором передаётся
                # адрес страницы, с которой пользователь был переадресован.
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                # Проверяем, что редирект приведёт именно на указанную ссылку.
                self.assertRedirects(response, redirect_url)


    def test_availability_authpage_for_all_users(self):
        """Страницы регистрации пользователей,
         входа в учётную запись и выхода из неё доступны всем пользователям."""
        pass