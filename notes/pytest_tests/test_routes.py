from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects

from django.urls import reverse


@pytest.mark.parametrize(
    "name",  # Имя параметра функции.
    # Значения, которые будут передаваться в name.
    ("notes:home", "users:login", "users:logout", "users:signup"),
)
# Указываем имя изменяемого параметра в сигнатуре теста.
def test_pages_availability_for_anonymous_user(client, name):
    url = reverse(name)  # Получаем ссылку на нужный адрес.
    response = client.get(url)  # Выполняем запрос.
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize("name", ("notes:list", "notes:add", "notes:success"))
def test_pages_availability_for_auth_user(not_author_client, name):
    url = reverse(name)
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    "name",
    ("notes:detail", "notes:edit", "notes:delete"),
)
def test_pages_availability_for_author(author_client, name, note):
    url = reverse(name, args=(note.slug,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    # parametrized_client - название параметра,
    # в который будут передаваться фикстуры;
    # Параметр expected_status - ожидаемый статус ответа.
    "parametrized_client, expected_status, args",
    # В кортеже с кортежами передаём значения для параметров:
    (
        (pytest.lazy_fixture("not_author_client"), HTTPStatus.NOT_FOUND, pytest.lazy_fixture("slug_for_args")),  # type: ignore
        (pytest.lazy_fixture("author_client"), HTTPStatus.OK, pytest.lazy_fixture("slug_for_args")),  # type: ignore
    ),
)
# Этот декоратор оставляем таким же, как в предыдущем тесте.
@pytest.mark.parametrize(
    "name",
    ("notes:detail", "notes:edit", "notes:delete"),
)
# В параметры теста добавляем имена parametrized_client и expected_status.
def test_pages_availability_for_different_users(
    parametrized_client, name, args, expected_status
):
    url = reverse(name, args=args)
    # Делаем запрос от имени клиента parametrized_client:
    response = parametrized_client.get(url)
    # Ожидаем ответ страницы, указанный в expected_status:
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    "name, args",
    (
        ("notes:detail", pytest.lazy_fixture("slug_for_args")),  # type: ignore
        ("notes:edit", pytest.lazy_fixture("slug_for_args")),  # type: ignore
        ("notes:delete", pytest.lazy_fixture("slug_for_args")),  # type: ignore
        ("notes:add", None),
        ("notes:success", None),
        ("notes:list", None),
    ),
)
# Передаём в тест анонимный клиент, name проверяемых страниц и args:
def test_redirects(client, name, args):
    login_url = reverse("users:login")
    # Теперь не надо писать никаких if и можно обойтись одним выражением.
    url = reverse(name, args=args)
    expected_url = f"{login_url}?next={url}"
    response = client.get(url)
    assertRedirects(response, expected_url)
