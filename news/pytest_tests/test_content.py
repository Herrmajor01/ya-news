"""Тесты для проверки контента на страницах приложения news."""

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from news.forms import CommentForm
from news.models import Comment, News

User = get_user_model()


class TestHomePage(TestCase):
    """Класс содержит тесты для проверки контента на главной странице."""

    HOME_URL = reverse('news:home')

    @classmethod
    def setUpTestData(cls):
        """
        Метод setUpTestData вызывается один раз для настройки данных.

        Которые будут использоваться во всех тестах этого класса.
        Создаем новости для тестирования количества и сортировки.
        """
        today = datetime.today()
        all_news = [
            News(
                title=f'Новость {index}',
                text='Просто текст.',
                date=today - timedelta(days=index)
            )
            for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
        ]
        News.objects.bulk_create(all_news)

    def test_news_count(self):
        """
        Тестирует, что количество новостей на главной.

        странице не превышает значение,
        указанное в settings.NEWS_COUNT_ON_HOME_PAGE.
        """
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        news_count = object_list.count()
        self.assertEqual(news_count, settings.NEWS_COUNT_ON_HOME_PAGE)

    def test_news_order(self):
        """
        Тестирует, что новости на главной странице отсортированы.

        от самой свежей к самой старой.
        """
        response = self.client.get(self.HOME_URL)
        object_list = response.context['object_list']
        all_dates = [news.date for news in object_list]
        sorted_dates = sorted(all_dates, reverse=True)
        self.assertEqual(all_dates, sorted_dates)


class TestDetailPage(TestCase):
    """
    Класс TestDetailPage содержит тесты для проверки контента.

    на странице отдельной новости.
    """

    @classmethod
    def setUpTestData(cls):
        """
        Метод setUpTestData вызывается один раз для настройки данных.

        Которые будут использоваться во всех тестах этого класса.
        Создаем новость, пользователя и комментарии для тестирования.
        """
        cls.news = News.objects.create(
            title='Тестовая новость', text='Просто текст.'
        )
        cls.detail_url = reverse(
            'news:detail', args=(cls.news.id,))  # type: ignore
        cls.author = User.objects.create(username='Комментатор')
        now = timezone.now()
        for index in range(10):
            comment = Comment.objects.create(
                news=cls.news, author=cls.author, text=f'Текст {index}',
            )
            comment.created = now + timedelta(days=index)
            comment.save()

    def test_comments_order(self):
        """
        Тестирует, что комментарии на странице отдельной новости.

        Отсортированы от старых к новым.
        """
        response = self.client.get(self.detail_url)
        self.assertIn('news', response.context)
        news = response.context['news']
        all_comments = news.comment_set.all()
        all_timestamps = [comment.created for comment in all_comments]
        sorted_timestamps = sorted(all_timestamps)
        self.assertEqual(all_timestamps, sorted_timestamps)

    def test_anonymous_client_has_no_form(self):
        """
        Тестирует, что анонимному пользователю не видна форма для отправки.

        комментария на странице отдельной новости.
        """
        response = self.client.get(self.detail_url)
        self.assertNotIn('form', response.context)

    def test_authorized_client_has_form(self):
        """
        Тестирует, что авторизованному пользователю видна форма для отправк.

        комментария на странице отдельной новости, и что эта форма является
        экземпляром CommentForm.
        """
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], CommentForm)
