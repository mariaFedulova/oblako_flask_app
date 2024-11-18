import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    yield app.test_client()

# Тесты для маршрутов
def test_root(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'Hello' in response.data 

def test_data_page(client):
    response = client.get('/data')
    assert response.status_code == 200
    assert b'This is some data!' in response.data 

def test_users_page(client):
    response = client.get('/users')
    assert response.status_code == 200

# Тест кэша
def test_cache(client):
    response1 = client.get('/data')
    response2 = client.get('/data')
    assert response1.data == response2.data 

# Тестирование исключений
def test_404(client):
    response = client.get('/non_existent_route')
    assert response.status_code == 404
