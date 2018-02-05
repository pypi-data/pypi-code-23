# coding: utf-8
"""
This module responsibility is to hold
classes and functions that are related
with cloning projects and tasks.
"""
import logging
from .models import (
    Project,
    Task,
    TaskStatus,
    TaskAttachment,
    Comment,
    Reminder,
)
logger = logging.getLogger(__name__)
from django.db.models import Min
from datetime import timedelta

def clone_project(source,
                  new_name,
                  new_enterprise=None,
                  new_type=None,
                  new_responsible=None,
                  new_date=None,
                  new_status=None,
                  keep_tasks=False,
                  keep_comments=False,
                  keep_attachments=False,
                  keep_tags=False):
    try:
        if not source:
            raise ValueError('source is mandatory')
        if not new_name:
            raise ValueError('new_name is mandatory')
        logger.info('cloning project %s into %s', source, new_name)

        new_enterprise = new_enterprise if new_enterprise else source.enterprise
        new_type = new_type if new_type else source.type
        new_status = new_status if new_status else TaskStatus.objects.get(code='OPEN')
        new_responsible = new_responsible if new_responsible else source.responsible
        new = Project()
        new.enterprise = new_enterprise
        new.name = new_name
        new.description = source.description
        new.type = new_type
        new.responsible = new_responsible
        new.save()

        if keep_tags:
            logger.info('cloning project %s tags', source)
            for tag in source.tags.all():
                new.tags.add(tag)

        if keep_tasks:
            logger.info('cloning project %s tasks', source)
            for task in source.root_tasks.all():
                clone_task(
                    task,
                    new_project=new,
                    new_date=new_date,
                    new_status=new_status,
                    keep_comments=keep_comments,
                    keep_attachments=keep_attachments,
                    keep_tags=keep_tags
                )

        return new
    except Exception as ex:
        logger.error(
            'error while cloning project %s. error: %s',
            source,
            ex.message,
            exc_info=True
        )
        return None


def clone_task(source,
               new_project=None,
               new_node=None,
               new_status=None,
               new_date=None,
               new_responsible=None,
               keep_comments=False,
               keep_attachments=False,
               keep_tags=False):
    if not source:
        raise ValueError('source is mandatory')
    if not new_project and not new_node:
        raise ValueError('new_project and new_node cannot be null. you must choose one to be the target of the copied task.')  # noqa
    if new_node and new_project.pk != new_node.project.pk:
        raise ValueError('new_node must be contained in new_project')
    logger.info('cloning task %s', source)
    if new_project:
        project = new_project
    else:
        if new_node.project:
            project = new_node.project
        else:
            project = source.project

    project = new_project if new_project else source.project
    parent = new_node  # this does not coerce because new_node == None is also valid
    responsible = new_responsible if new_responsible else source.responsible

    status = new_status if new_status else source.status    

    start_date = new_date if new_date else source.start_date
    minimal_date_start = source.project.tasks.aggregate(Min('start_date'))
    minimal_date_end = source.project.tasks.aggregate(Min('end_date'))

    root_start_date = None
    root_end_date = None

    if start_date:
        if minimal_date_start['start_date__min']:
            if source.start_date:
                delta = source.start_date - minimal_date_start['start_date__min']
                absolute_delta = timedelta(seconds=delta.total_seconds() * -1 if delta.total_seconds() < 0 else delta.total_seconds())
                root_start_date = start_date + absolute_delta

    if root_start_date and source.end_date:
        delta = source.end_date - source.start_date
        root_end_date = root_start_date + delta
    elif minimal_date_end['end_date__min']:
        if source.end_date:
            delta = source.end_date - minimal_date_end['end_date__min']
            absolute_delta = timedelta(seconds=delta.total_seconds() * -1 if delta.total_seconds() < 0 else delta.total_seconds())
            root_end_date = start_date + absolute_delta

    new = Task(
        project=project,
        parent=parent,
        responsible=responsible,
        status=status,
        name=source.name,
        description=source.description,
        start_date=root_start_date,
        end_date=root_end_date
    )
    new.save()
    if keep_comments:
        logger.info('cloning task %s comments', source)
        for c in source.comments.all():
            new_comment = Comment(
                created_by=c.created_by,
                task=new,
                text=c.text
            )
            new_comment.save()
    if keep_attachments:
        logger.info('cloning task %s attachments', source)
        for a in source.attachments.all():
            new_attachment = TaskAttachment(
                created_by=a.created_by,
                task=new,
                content_object=a.content_object
            )
            new_attachment.save()
    if keep_tags:
        logger.info('cloning task %s tags', source)
        for tag in source.tags.all():
            new.tags.add(tag)

    logger.info('cloning task %s children', source)
    children = source.get_children()
    for child in children:
        child.clone(
            new_project=project,
            new_node=new,
            new_status=new_status,
            new_date=start_date,
            new_responsible=new_responsible,
            keep_comments=keep_comments,
            keep_attachments=keep_attachments
        )

    return new
