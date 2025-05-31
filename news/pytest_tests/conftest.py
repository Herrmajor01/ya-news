"""Фикстуры для тестов Django-приложения news."""

import pytest
from django.test import Client
from django.utils import timezone
from datetime import datetime, timedelta
from django.conf import settings


@pytest.fixture
def client(db):
    """Фикстура для тестового клиента Django."""
    return Client()


@pytest.fixture
def user(db):
    """Фикстура для создания тестового пользователя."""
    from django.contrib.auth import get_user_model
    user_model = get_user_model()
    return user_model.objects.create(username='Пользователь')


@pytest.fixture
def author(db):
    """Фикстура для создания тестового автора."""
    from django.contrib.auth import get_user_model
    user_model = get_user_model()
    return user_model.objects.create(username='Автор')


@pytest.fixture
def reader(db):
    """Фикстура для создания тестового читателя."""
    from django.contrib.auth import get_user_model
    user_model = get_user_model()
    return user_model.objects.create(username='Читатель')


@pytest.fixture
def auth_client(user):
    """Фикстура для авторизованного тестового клиента."""
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def author_client(author):
    """Фикстура для авторизованного клиента автора."""
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def reader_client(reader):
    """Фикстура для авторизованного клиента читателя."""
    client = Client()
    client.force_login(reader)
    return client


@pytest.fixture
def news(db):
    """Фикстура для создания тестовой новости."""
    from news.models import News
    return News.objects.create(title='Тестовая новость', text='Текст')


@pytest.fixture
def comment(author, news):
    """Фикстура для создания тестового комментария."""
    from news.models import Comment
    return Comment.objects.create(
        news=news, author=author, text='Текст комментария'
    )


@pytest.fixture
def news_list(db):
    """Фикстура для создания списка тестовых новостей."""
    from news.models import News
    today = datetime.now()
    all_news = [
        News(title=f'Новость {index}', text='Текст',
             date=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def comments(author, news):
    """Фикстура для создания списка тестовых комментариев."""
    from news.models import Comment
    now = timezone.now()
    comments = [
        Comment(news=news, author=author,
                text=f'Текст {index}', created=now + timedelta(days=index))
        for index in range(10)
    ]
    return Comment.objects.bulk_create(comments)
