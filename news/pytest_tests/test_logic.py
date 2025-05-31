"""Тесты для проверки логики приложения news."""

from http import HTTPStatus
from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()


class TestCommentCreation(TestCase):
    """
    Класс содержит тесты для проверки логики создания комментариев.

    Содержит тесты для проверки создания комментариев.
    """

    COMMENT_TEXT = 'Текст комментария'

    @classmethod
    def setUpTestData(cls):
        """Данные для тестов."""
        from news.models import News
        cls.news = News.objects.create(title='Заголовок', text='Текст')
        cls.url = reverse('news:detail', args=(cls.news.id,))  # type: ignore
        cls.user = User.objects.create(username='Мимо Крокодил')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {'text': cls.COMMENT_TEXT}

    def test_anonymous_cant_create_comment(self):
        """Тестирует, анонимный пользователь не может создать комментарий."""
        self.client.post(self.url, data=self.form_data)
        assert Comment.objects.count() == 0

    def test_user_can_create_comment(self):
        """
        Тестирует, авторизованный пользователь может создать комментарий.

        Проверяет, что авторизованный пользователь может успешно создать
        комментарий.
        """
        response = self.auth_client.post(self.url, data=self.form_data)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == (  # type: ignore
            # type: ignore
            f'{reverse("news:detail", args=(
                self.news.id,))}#comments'  # type: ignore
        )
        assert Comment.objects.count() == 1
        comment = Comment.objects.get()
        assert comment.text == self.form_data['text']
        assert comment.news == self.news
        assert comment.author == self.user

    def test_user_cant_use_bad_words(self):
        """Тестирует, пользователь не может использовать запрещённые слова."""
        bad_words_data = {'text': f'Текст с {BAD_WORDS[0]}'}
        response = self.auth_client.post(
            self.url, data=bad_words_data
        )
        assert 'form' in response.context
        assert response.context['form'].errors['text'] == [WARNING]
        assert Comment.objects.count() == 0


class TestCommentEditDelete(TestCase):
    """
    Класс TestCommentEditDelete содержит тесты для проверки логики.

    редактирования и удаления комментариев.
    """

    COMMENT_TEXT = 'Текст комментария'
    NEW_COMMENT_TEXT = 'Обновлённый комментарий'

    @classmethod
    def setUpTestData(cls):
        """Данные для тестов."""
        from news.models import News, Comment
        cls.news = News.objects.create(title='Заголовок', text='Текст')
        news_url = reverse('news:detail', args=(cls.news.id,))  # type: ignore
        cls.url_to_comments = news_url + '#comments'
        cls.author = User.objects.create(username='Автор комментария')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.comment = Comment.objects.create(
            news=cls.news,
            author=cls.author,
            text=cls.COMMENT_TEXT
        )
        cls.edit_url = reverse(
            'news:edit', args=(cls.comment.id,))  # type: ignore
        cls.delete_url = reverse(
            'news:delete', args=(cls.comment.id,))  # type: ignore
        cls.form_data = {'text': cls.NEW_COMMENT_TEXT}

    def test_author_can_edit_comment(self):
        """
        Тестирует, что автор комментария может успешно редактировать.

        Свой комментарий.
        """
        response = self.author_client.post(self.edit_url, data=self.form_data)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == self.url_to_comments  # type: ignore
        self.comment.refresh_from_db()
        assert self.comment.text == self.NEW_COMMENT_TEXT

    def test_author_can_delete_comment(self):
        """
        Тестирует, что автор комментария может успешно удалить.

        Свой комментарий.
        """
        response = self.author_client.delete(self.delete_url)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url == self.url_to_comments  # type: ignore
        assert Comment.objects.count() == 0

    def test_other_user_cant_edit_comment(self):
        """
        Тестирует, что другой пользователь не может редактировать.

        чужой комментарий.
        """
        new_text = 'Новый текст'
        form_data = {'text': new_text}
        response = self.reader_client.post(self.edit_url, data=form_data)
        assert response.status_code == HTTPStatus.NOT_FOUND
        self.comment.refresh_from_db()
        assert self.comment.text != new_text

    def test_other_user_cant_delete_comment(self):
        """
        Тестирует, что другой пользователь.

        не может удалить чужой комментарий.
        """
        response = self.reader_client.delete(self.delete_url)
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert Comment.objects.count() == 1
