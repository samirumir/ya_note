from http import HTTPStatus
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from pytils.translit import slugify
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
    NOTE_TITLE = 'Первый пост'
    NOTE_TEXT = 'Первый пост'
    NOTE_SLUG = 'First'

    @classmethod
    def setUpTestData(cls):
        cls.url = reverse('notes:add',)
        cls.user = User.objects.create(username='Человек простой')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data_with_slug = {
            'title': cls.NOTE_TEXT,
            'text': cls.NOTE_TITLE,
            'slug':cls.NOTE_SLUG
            }
        cls.form_data_without_slug = {
            'title': cls.NOTE_TEXT,
            'text': cls.NOTE_TITLE,
            }
        cls.done_url = reverse('notes:success',)

    # @skip('bla bla bla')
    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создавать посты"""
        self.client.post(self.url, data=self.form_data_with_slug)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 0)


    # @skip('bla bla bla')
    def test_user_can_create_note(self):
        """Авторизованный пользователь может создавать посты"""
        response = self.auth_client.post(self.url, data=self.form_data_with_slug)
        self.assertRedirects(response, self.done_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.NOTE_TITLE)
        self.assertEqual(note.title, self.NOTE_TEXT)
        self.assertEqual(note.author, self.user)
        self.assertEqual(note.slug, self.NOTE_SLUG)


    # @skip('bla bla bla')
    def test_slugify_by_name(self):
        """При создании поста с пустым полем slug, значение берется из title"""
        response = self.auth_client.post(
            self.url, data=self.form_data_without_slug
            )
        self.assertRedirects(response, self.done_url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        note = Note.objects.get()
        self.assertEqual(note.text, self.NOTE_TITLE)
        self.assertEqual(note.title, self.NOTE_TEXT)
        self.assertEqual(note.author, self.user)
        self.assertEqual(note.slug, slugify(self.NOTE_TITLE)[:100])


    # @skip('bla bla bla')
    def test_slug_is_unique(self):
        """Значение slug должно быть уникальным"""
        response = self.auth_client.post(
            self.url, data=self.form_data_with_slug
            )
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        response = self.auth_client.post(
            self.url, data={
                'title': 'Второй пост',
                'text': 'Второй пост',
                'slug': 'First',
                }
            )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        # self.assertRedirects(response, self.url)
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
    
class TestNotesEditDelete(TestCase):
    TEXT_NEW = 'Обновленный первый пост'
    TEXT_OLD = 'Первоначальный пост'
    TITLE_NEW = 'Обновленный заголовок первого поста'
    TITLE_OLD = 'Первоначальный заголовок'
    SLUG = 'First'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Человек простой')
        cls.reader = User.objects.create(username='Читатель левый')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.notes = Note.objects.create(
            title=cls.TITLE_OLD,
            text=cls.TEXT_OLD,
            author=cls.author,
            slug=cls.SLUG
            )
        cls.note_url = reverse('notes:detail', args=(cls.notes.slug,))
        cls.edit_url = reverse('notes:edit', args=(cls.notes.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.notes.slug,))
        cls.done_url = reverse('notes:success')
        cls.form_data = {'title': cls.TITLE_NEW, 'text': cls.TEXT_NEW}
    
    # @skip('bla bla bla')
    def test_author_can_delete_note(self):
        """Авторизованный пользователь может удалять посты"""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.done_url)
        notes_count= Note.objects.count()
        self.assertEqual(notes_count, 0)
    
    # @skip('bla bla bla')
    def test_author_can_edit_note(self):
        """Авторизованный пользователь может редактировать посты"""
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.done_url)
        self.notes.refresh_from_db()
        self.assertEqual(self.notes.text, self.TEXT_NEW)
        self.assertEqual(self.notes.title, self.TITLE_NEW)

    # @skip('bla bla bla')
    def test_reader_cant_delete_note_other_users(self):
        """Анонимный пользователь не может удалять посты"""
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count= Note.objects.count()
        self.assertEqual(notes_count, 1)

    # @skip('bla bla bla')
    def test_reader_cant_edit_note_other_users(self):
        """Анонимный пользователь не может редактировать посты"""
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.notes.refresh_from_db()
        self.assertEqual(self.notes.text, self.TEXT_OLD)
        self.assertEqual(self.notes.title, self.TITLE_OLD)