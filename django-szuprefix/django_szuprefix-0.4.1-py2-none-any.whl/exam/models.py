# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models

from django_szuprefix.saas.models import Party
from django.contrib.auth.models import User
from django_szuprefix.utils import modelutils


class Paper(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = u"试卷"
        ordering = ('-create_time',)

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="exam_papers",
                              on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name=User._meta.verbose_name, related_name="exam_papers",
                             on_delete=models.PROTECT)
    title = models.CharField(u"标题", max_length=255, blank=False)
    content = models.TextField(u"内容", blank=True, null=True)
    content_object = modelutils.JSONField(u"内容对象", blank=True, null=True, help_text="")
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)
    is_active = models.BooleanField(u"有效", blank=False)

    def __unicode__(self):
        return self.title

    def save(self, **kwargs):
        if not self.title:
            self.title = u"试卷"
        return super(Paper, self).save(**kwargs)


class Stat(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = u"统计"

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="exam_stats",
                              on_delete=models.PROTECT)
    paper = models.OneToOneField(Paper, verbose_name=Paper._meta.verbose_name, related_name="stat",
                                 on_delete=models.PROTECT)
    detail = modelutils.JSONField(u"详情", help_text="")

    def add_answer(self, answer):
        d = self.detail or {}
        from . import helper
        questions = d.setdefault('questions', {})
        score_level = str(answer.performance.get('stdScore', 0) / 5 * 5)
        helper.distrib_count(d.setdefault('scores', {}), score_level)
        seconds_level = str((answer.seconds / 60 + 1) * 60)
        helper.distrib_count(d.setdefault('seconds', {}), seconds_level)
        ad = answer.detail
        for a in ad:
            num = str(a.get('number'))
            questions[num] = questions.setdefault(num, 0) + (a.get('right') is False and 1 or 0)
        self.detail = d


class Answer(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = u"用户答卷"
        ordering = ('-create_time',)

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="exam_answers",
                              on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name=User._meta.verbose_name, related_name="exam_answers",
                             on_delete=models.PROTECT)
    paper = models.ForeignKey(Paper, verbose_name=Paper._meta.verbose_name, related_name="answers",
                              on_delete=models.PROTECT)
    detail = modelutils.JSONField(u"详情", help_text="")
    seconds = models.PositiveSmallIntegerField(u"用时", default=0, blank=True, null=True, help_text=u"单位(秒)")
    performance = modelutils.JSONField(u"成绩表现", blank=True, null=True, help_text="")
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)

    def __unicode__(self):
        return u"%s by %s" % (self.paper, self.user)

    def save(self, **kwargs):
        self.performance = self.cal_performance()
        return super(Answer, self).save(**kwargs)

    def cal_performance(self):
        wc = 0
        rc = 0
        score = 0
        fsc = 0
        for a in self.detail:
            sc = a.get('score', 1)
            fsc += sc
            if a.get('answer') == a.get('userAnswer'):
                score += sc
                rc += 1
            else:
                wc += 1
        return dict(wrongCount=wc, rightCount=rc, fullScore=fsc, score=score, stdScore=score * 100 / fsc)


class Performance(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = u"用户成绩"
        unique_together = ('party', 'user', 'paper')
        # ordering = ('-create_time',)

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="exam_performances",
                              on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name=User._meta.verbose_name, related_name="exam_performances",
                             on_delete=models.PROTECT)
    paper = models.ForeignKey(Paper, verbose_name=Paper._meta.verbose_name, related_name="performances",
                              on_delete=models.PROTECT)
    score = models.PositiveSmallIntegerField(u"得分", default=0, blank=True, null=True)
    detail = modelutils.JSONField(u"详情", blank=True, null=True, help_text="")
    create_time = models.DateTimeField(u"创建时间", auto_now_add=True)

    def __unicode__(self):
        return u"%s by %s" % (self.paper, self.user)

    def cal_performance(self):
        scs = [a.performance.get('stdScore', 0) for a in self.paper.answers.all()]
        lastAnswer = self.paper.answers.first()
        return dict(
            maxScore=max(scs),
            minScore=min(scs),
            avgScore=sum(scs) / len(scs),
            lastScore=scs[0],
            times=len(scs),
            lastTime=lastAnswer and lastAnswer.create_time.isoformat()
        )

    def save(self, **kwargs):
        p = self.cal_performance()
        self.detail = p
        self.score = p.get('lastScore', 0)
        return super(Performance, self).save(**kwargs)
