from django.conf import settings
from rest_framework import serializers

from students.models import Course


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ("id", "name", "students")

    def validate(self, data):
        students = data.get("students")
        if students is not None and len(students) > settings.MAX_STUDENTS_PER_COURSE:
            raise serializers.ValidationError(
                "превышено максимальное число студентов на курсе"
            )
        return data
