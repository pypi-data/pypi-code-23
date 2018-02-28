# -*- coding:utf-8 -*-
from . import models, mixins
from rest_framework import serializers
__author__ = 'denishuang'


class SchoolSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.School
        fields = ('name', 'type', 'create_time', 'url')


class TeacherSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Teacher
        fields = ('name', 'url')


class GradeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Grade
        fields = ('name',)


class SessionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Session
        fields = ('name',)


class ClazzSerializer(mixins.SchoolSerializerMixin, serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Clazz
        fields = ('id', 'name', 'entrance_session', 'number', 'primary_teacher', 'grade', 'teacher_names')


class StudentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Student
        fields = ('name', 'number', 'clazz', 'grade', 'url')
