import pytest
from django.urls import reverse
from model_bakery import baker
from rest_framework.test import APIClient

from students.models import Course, Student

pytestmark = pytest.mark.django_db


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def course_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)

    return factory


@pytest.fixture
def student_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)

    return factory


def test_create_course(client):
    response = client.post(
        reverse("courses-list"), data={"name": "создаём тестовый курс"}
    )
    assert response.status_code == 201
    assert response.data["name"] == "создаём тестовый курс"


def test_update_course(client, course_factory):
    course = course_factory()
    response = client.patch(
        reverse("courses-detail", kwargs={"pk": course.id}),
        data={"name": "обновляем тестовый курс"},
    )
    assert response.status_code == 200
    assert response.data["name"] == "обновляем тестовый курс"


def test_delete_course(client, course_factory):
    course = course_factory()
    response = client.delete(reverse("courses-detail", kwargs={"pk": course.id}))
    assert response.status_code == 204


def test_retrieve_course(client, course_factory):
    course = course_factory()
    response = client.get(reverse("courses-detail", kwargs={"pk": course.id}))
    assert response.status_code == 200
    assert response.data["id"] == course.id


def test_course_list(client, course_factory):
    courses = course_factory(_quantity=10)
    response = client.get(reverse("courses-list"))
    assert response.status_code == 200
    assert len(response.data) == 10
    assert {item["id"] for item in response.data} == {c.id for c in courses}


def test_filter_courses_by_id(client, course_factory):
    courses = course_factory(_quantity=3)
    target = courses[1]
    response = client.get(reverse("courses-list"), data={"id": target.id})
    assert response.status_code == 200
    assert len(response.data) == 1 and response.data[0]["id"] == target.id


def test_filter_courses_by_name(client, course_factory):
    list_name = ["python", "sql", "django"]
    courses = course_factory(_quantity=10)
    for course, name in zip(courses[:3], list_name):
        course.name = name
        course.save()
    target_name = list_name[0]
    response = client.get(reverse("courses-list"), data={"name": target_name})
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]["name"] == target_name


@pytest.mark.parametrize(
    "students_count, expected_status",
    [
        (2, 201),
        (3, 400),
    ],
)
def test_max_students_per_course(
    client, student_factory, settings, students_count, expected_status
):
    settings.MAX_STUDENTS_PER_COURSE = 2
    students = student_factory(_quantity=students_count)
    student_ids = [student.id for student in students]
    response = client.post(
        reverse("courses-list"),
        data={"name": "курс с ограничением по студентам", "students": student_ids},
    )
    assert response.status_code == expected_status
