import pytest
from app import app


@pytest.fixture
def client():
    """Создаёт тестовый клиент Flask"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_hello_world(client):
    """Тест: главная страница возвращает 200"""
    response = client.get('/')
    assert response.status_code == 200


def test_hello_world_content(client):
    """Тест: главная страница содержит правильный текст"""
    response = client.get('/')
    assert b'Hello, World!!!' in response.data
    assert b'Docker-контейнера' in response.data


def test_hello_world_html(client):
    """Тест: ответ содержит HTML-тег h1"""
    response = client.get('/')
    assert b'<h1>' in response.data
    assert b'</h1>' in response.data


def test_hello_world_is_string(client):
    """Тест: ответ — строка (не JSON, не ошибка)"""
    response = client.get('/')
    assert response.content_type == 'text/html; charset=utf-8'


def test_nonexistent_route(client):
    """Тест: несуществующий маршрут возвращает 404"""
    response = client.get('/nonexistent')
    assert response.status_code == 404
