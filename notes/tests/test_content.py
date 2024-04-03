from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm

from unittest import skip

User = get_user_model()

"""В файле test_content.py:
1.отдельная заметка передаётся на страницу со списком заметок в списке object_list в словаре context;
2.в список заметок одного пользователя не попадают заметки другого пользователя;
3.на страницы создания и редактирования заметки передаются формы."""

class TestAddPage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Человек простой')
        cls.add_url = reverse('notes:add',)
        cls.notes = Note.objects.create(
            title='Простой страницы',
            text='Простой текст страницы',
            slug='First',
            author=cls.author,)
        cls.edit_url = reverse('notes:edit', args=(cls.notes.slug,))

    # @skip('bla bla bla')
    def test_anonymous_client_has_no_form(self):
        response = self.client.get(self.add_url)
        self.assertNotIn('form', response.context)

    # @skip('bla bla bla')
    def test_authorized_client_has_add_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.add_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)

    def test_authorized_client_has_edit_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.edit_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)


class TestHomePage(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Человек простой')
        cls.reader = User.objects.create(username='Читатель левый')
        cls.notes_author = Note.objects.create(
            title='Простой страницы',
            text='Простой текст страницы',
            slug='First',
            author=cls.author,)
        cls.notes_reader = Note.objects.create(
            title='Простой страницы',
            text='Простой текст страницы',
            slug='Second',
            author=cls.reader,)
        cls.notes_url = reverse('notes:list')

    def test_note_in_context(self):
        """Словарь передается в context, 
        на страницу пользователя не попадают записи другого пользователя"""
        self.client.force_login(self.author)
        response = self.client.get(self.notes_url)
        object_list = response.context['object_list']
        notes_count = object_list.count()
        self.assertEqual(notes_count, 1)

    