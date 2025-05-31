"""Тесты для проверки доступности маршрутов."""

from http import HTTPStatus
from django.urls import reverse


def test_home_page_available_for_anonymous(client, db):
    """Проверяет доступность главной страницы для анонимного пользователя."""
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_detail_page_available_for_anonymous(client, news):
    """Проверяет доступность страницы новости для анонимного пользователя."""
    url = reverse('news:detail', args=(news.pk,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_edit_and_delete_available_for_author(author_client, comment):
    """Проверяет доступность страниц редактирования/удаления для автора."""
    for name in ('news:edit', 'news:delete'):
        url = reverse(name, args=(comment.pk,))
        response = author_client.get(url)
        assert response.status_code == HTTPStatus.OK


def test_anonymous_redirected_to_login(client, comment):
    """Проверяет редирект анонимного пользователя на страницу логина."""
    login_url = reverse('users:login')
    for name in ('news:edit', 'news:delete'):
        url = reverse(name, args=(comment.pk,))
        redirect_url = f'{login_url}?next={url}'
        response = client.get(url)
        assert response.status_code == HTTPStatus.FOUND
        assert response.url.startswith(redirect_url)


def test_other_user_gets_404(reader_client, comment):
    """Проверяет ошибку 404 для других пользователей при доступе к чужим."""
    for name in ('news:edit', 'news:delete'):
        url = reverse(name, args=(comment.pk,))
        response = reader_client.get(url)
        assert response.status_code == HTTPStatus.NOT_FOUND


def test_auth_pages_available_for_anonymous(client):
    """Проверяет доступность страниц авторизации для анонимных."""
    urls = (
        ('users:login', None),
        ('users:signup', None),
    )
    for name, args in urls:
        url = reverse(name, args=args)
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK
