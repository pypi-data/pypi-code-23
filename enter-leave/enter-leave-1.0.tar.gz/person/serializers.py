import datetime
from rest_framework import serializers
from . import models
from pytz import utc
from django.utils import timezone


class PersonListSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Person
        exclude = ('id',)


class EnterOrLeaveSerializer(serializers.ModelSerializer):
    person = PersonListSerializer()

    class Meta:
        model = models.EnterOrLeave
        fields = '__all__'
        read_only_fields = ('leave_time', 'history', 'create_on', 'enter_status')

    def create(self, validated_data):
        per = models.Person()
        per.id_card = validated_data['person'].get('id_card')
        per.name = validated_data['person'].get('name')
        per.gender = validated_data['person'].get('gender')
        per.birthday = validated_data['person'].get('birthday')
        per.native_place = validated_data['person'].get('native_place')
        per.duty = validated_data['person'].get('duty')
        per.project_unit = validated_data['person'].get('project_unit')
        per.department = validated_data['person'].get('department')
        per.team = validated_data['person'].get('team')
        per.work = validated_data['person'].get('work')
        per.images = validated_data['person'].get('images')
        per.certificate = validated_data['person'].get('certificate')
        per.identity = validated_data['person'].get('identity') if validated_data.get(
            'identity') else 0
        per.remark = validated_data['person'].get('remark')
        per.save()
        per.enterorleave.enter_time = validated_data.get('enter_time').replace(tzinfo=utc) if validated_data.get(
            'enter_time') else timezone.now()
        per.enterorleave.enter_status = 0
        per.enterorleave.create_on = timezone.now()
        per.enterorleave.save()
        return per.enterorleave

    def update(self, instance, validated_data):
        person = instance.person
        person.name = validated_data['person'].get('name') if validated_data['person'].get(
            'name') else person.name
        person.id_card = validated_data['person'].get('id_card') if validated_data['person'].get(
            'id_card') else person.id_card
        person.gender = validated_data['person'].get('gender') if validated_data['person'].get(
            'gender') else person.gender
        person.birthday = validated_data['person'].get('birthday') if validated_data[
            'person'].get('birthday') else person.birthday
        person.native_place = validated_data['person'].get('native_place') if validated_data[
            'person'].get('native_place') else person.native_place
        person.duty = validated_data['person'].get('duty') if validated_data['person'].get(
            'duty') else person.duty
        person.project_unit = validated_data['person'].get('project_unit') if validated_data[
            'person'].get('project_unit') else person.project_unit
        person.department = validated_data['person'].get('department') if validated_data[
            'person'].get('department') else person.department
        person.team = validated_data['person'].get('team') if validated_data['person'].get(
            'team') else person.team
        person.work = validated_data['person'].get('work') if validated_data['person'].get(
            'work') else person.work
        person.images = validated_data['person'].get('images') if validated_data['person'].get(
            'images') else person.images
        person.certificate = validated_data['person'].get('certificate') if validated_data[
            'person'].get('certificate') else person.certificate
        person.identity = validated_data['person'].get('identity') if validated_data[
            'person'].get('identity') else person.identity
        person.remark = validated_data['person'].get('remark') if validated_data['person'].get(
            'remark') else person.remark
        person.save()
        instance.save()
        return instance

    def validate(self, attrs):
        method = self.context.get('request').method if self.context.get('request') else 'POST' 
        if method == 'POST':
            id_card = attrs.get('person', {}).get('id_card')
            if models.EnterOrLeave.objects.filter(person__id_card=id_card):
                raise serializers.ValidationError('id_card already exists')
        return attrs


