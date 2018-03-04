# -*- coding:utf-8 -*-
import django_filters
from rest_framework.metadata import SimpleMetadata
from .apps import Config

from . import models, mixins, serializers, importers
from rest_framework import viewsets, permissions, decorators, status
from rest_framework.response import Response
from django_szuprefix.api import register, mixins as api_mixins

__author__ = 'denishuang'


class SchoolViewSet(viewsets.ModelViewSet):
    queryset = models.School.objects.all()
    serializer_class = serializers.SchoolSerializer
    permission_classes = [permissions.IsAdminUser]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend]


register(Config.label, 'school', SchoolViewSet)


class TeacherViewSet(mixins.SchoolMixin, viewsets.ModelViewSet):
    queryset = models.Teacher.objects.all()
    serializer_class = serializers.TeacherSerializer
    # permission_classes = [permissions.IsAdminUser]


register(Config.label, 'teacher', TeacherViewSet)


class GradeViewSet(mixins.SchoolMixin, api_mixins.BatchCreateModelMixin, viewsets.ModelViewSet):
    queryset = models.Grade.objects.all()
    serializer_class = serializers.GradeSerializer


register(Config.label, 'grade', GradeViewSet)


class SessionViewSet(mixins.SchoolMixin, api_mixins.BatchCreateModelMixin, viewsets.ModelViewSet):
    queryset = models.Session.objects.all()
    serializer_class = serializers.SessionSerializer

    def get_queryset(self):
        return super(SessionViewSet, self).get_queryset().filter(
            school=self.request.user.as_saas_worker.party.as_school)

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.as_saas_worker.party.as_school)


register(Config.label, 'session', SessionViewSet)


class ClazzViewSet(mixins.SchoolMixin, api_mixins.BatchCreateModelMixin, viewsets.ModelViewSet):
    queryset = models.Clazz.objects.all()
    serializer_class = serializers.ClazzSerializer


register(Config.label, 'clazz', ClazzViewSet)


class MinimalMetadata(SimpleMetadata):
    def get_field_info(self, field):
        field_info = super(MinimalMetadata, self).get_field_info(field)
        if isinstance(field, (serializers.RelatedField, serializers.ManyRelatedField)):
            field_info['choices_url'] = 'http://baidu.com'
        return field_info


class StudentViewSet(api_mixins.BatchCreateModelMixin, viewsets.ModelViewSet):
    queryset = models.Student.objects.all()
    serializer_class = serializers.StudentSerializer
    filter_fields = ('name', 'number')
    metadata_class = MinimalMetadata

    def perform_create(self, serializer):
        serializer.save(school=self.request.user.as_saas_worker.party.as_school)

    def metadata(self, request, *args, **kwargs):
        return {"hello"}

    @decorators.list_route(['post'])
    def pre_import(self, request):
        importer = importers.StudentImporter()
        data = importer.clean(importer.get_excel_data(request.data['file']))
        return Response(data)

    @decorators.list_route(['post'])
    def post_import(self, request):
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            importer = importers.StudentImporter()
            data = importer.run(serializer.data)
            return Response(data)
        else:
            return Response({'detail': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


register(Config.label, 'student', StudentViewSet)
