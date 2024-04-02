from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from unittest import skip

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()

"""Проверки в этом файле
1.Залогиненный пользователь может создать заметку, а анонимный — не может.

2.Невозможно создать две заметки с одинаковым slug.

3.Если при создании заметки не заполнен slug, то он формируется автоматически, 
с помощью функции pytils.translit.slugify.

4.Пользователь может редактировать и удалять свои заметки,
но не может редактировать или удалять чужие."""


class TestNotesCreation(TestCase):
    # Текст для нового поста
    NOTE_TITLE = 'Заголовок'
    NOTE_TEXT = 'Текст'
    NOTE_SLUG = 'Наименование'

    @classmethod
    def setUpTestData(cls):
        cls.news = Note.objects.create(
            title='Первоначальная', text='Первый', slug = 'First'
            )
        cls.url = reverse('notes:add',)
        cls.user = User.objects.create(username='Человек простой')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        # Данные для POST-запроса при создании нового поста.
        cls.form_data = {
            'title': cls.NOTE_TEXT, 'text': cls.NOTE_TITLE, 'slug':cls.NOTE_SLUG
            }

    # @skip('bla bla bla')
    def test_anonymous_user_cant_create_note(self):
        # Совершаем запрос от анонимного клиента, в POST-запросе отправляем
        # предварительно подготовленные данные формы с текстом комментария.
        self.client.post(self.url, data=self.form_data)
        # Считаем количество комментариев.
        notes_count = Note.objects.count()
        # Ожидаем, что комментариев в базе нет - сравниваем с нулём.
        self.assertEqual(notes_count, 0)

    @skip('bla bla bla')
    def test_user_can_create_note(self):
        # Совершаем запрос через авторизованный клиент.
        response = self.auth_client.post(self.url, data=self.form_data)
        # Проверяем, что редирект привёл к разделу с комментами.
        self.assertRedirects(response, 'notes:home')
        # Считаем количество комментариев.
        notes_count = Note.objects.count()
        # Убеждаемся, что есть один комментарий.
        self.assertEqual(notes_count, 1)
        # Получаем объект комментария из базы.
        note = Note.objects.get()
        # Проверяем, что все атрибуты комментария совпадают с ожидаемыми.
        self.assertEqual(note.text, self.NOTE_TEXT)
        self.assertEqual(note.title, self.NOTE_TITLE)
        self.assertEqual(note.author, self.user)
        self.assertEqual(note.slug, self.NOTE_SLUG)

    @skip('bla bla bla')
    def test_user_cant_use_bad_words(self):
        # Формируем данные для отправки формы; текст включает
        # первое слово из списка стоп-слов.
        bad_words_data = {'text': f'Какой-то текст, {Warning}, еще текст'}
        # Отправляем запрос через авторизованный клиент.
        response = self.auth_client.post(self.url, data=bad_words_data)
        # Проверяем, есть ли в ответе ошибка формы.
        self.assertFormError(
            response,
            form='form',
            field='text',
            errors=WARNING
        )
        # Дополнительно убедимся, что комментарий не был создан.
        comments_count = Comment.objects.count()
        self.assertEqual(comments_count, 0)
