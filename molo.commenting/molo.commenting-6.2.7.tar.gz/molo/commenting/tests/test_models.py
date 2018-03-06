from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.sites.models import Site
from django.test import TestCase
from django.utils import timezone
from django.core.urlresolvers import reverse

from molo.commenting.models import MoloComment, CommentingSettings
from django_comments.models import CommentFlag
from django_comments import signals

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import Main, Languages, SiteLanguageRelation


class MoloCommentTest(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)
        self.user = User.objects.create_user(
            'test', 'test@example.org', 'test')
        self.content_type = ContentType.objects.get_for_model(self.user)

        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')
        self.article1 = self.mk_article(
            title='article 1', slug='article-1', parent=self.yourmind)

    def mk_comment(self, comment):
        return MoloComment.objects.create(
            content_type=self.content_type,
            object_pk=self.article1.pk,
            content_object=self.user,
            site=Site.objects.get_current(),
            user=self.user,
            comment=comment,
            submit_date=timezone.now())

    def mk_comment_flag(self, comment, flag):
        return CommentFlag.objects.create(
            user=self.user,
            comment=comment,
            flag_date=timezone.now(),
            flag=flag)

    def test_parent(self):
        first_comment = self.mk_comment('first comment')
        second_comment = self.mk_comment('second comment')
        second_comment.parent = first_comment
        second_comment.save()
        [child] = first_comment.children.all()
        self.assertEqual(child, second_comment)

    def test_auto_remove_off(self):
        comment = self.mk_comment('first comment')
        comment.save()
        comment_flag = self.mk_comment_flag(comment,
                                            CommentFlag.SUGGEST_REMOVAL)
        comment_flag.save()
        signals.comment_was_flagged.send(
            sender=comment.__class__,
            comment=comment,
            flag=comment_flag,
            created=True,
        )
        altered_comment = MoloComment.objects.get(pk=comment.pk)
        self.assertFalse(altered_comment.is_removed)

    def test_auto_remove_on(self):
        comment = self.mk_comment('first comment')
        comment.save()
        comment_flag = self.mk_comment_flag(comment,
                                            CommentFlag.SUGGEST_REMOVAL)
        comment_flag.save()
        with self.settings(COMMENTS_FLAG_THRESHHOLD=1):
            signals.comment_was_flagged.send(
                sender=comment.__class__,
                comment=comment,
                flag=comment_flag,
                created=True,
            )
        altered_comment = MoloComment.objects.get(pk=comment.pk)
        self.assertTrue(altered_comment.is_removed)

    def test_auto_remove_approved_comment(self):
        comment = self.mk_comment('first comment')
        comment.save()
        comment_approved_flag = self.mk_comment_flag(
            comment,
            CommentFlag.MODERATOR_APPROVAL)
        comment_approved_flag.save()
        comment_reported_flag = self.mk_comment_flag(
            comment,
            CommentFlag.SUGGEST_REMOVAL)
        comment_reported_flag.save()
        with self.settings(COMMENTS_FLAG_THRESHHOLD=1):
            signals.comment_was_flagged.send(
                sender=comment.__class__,
                comment=comment,
                flag=comment_reported_flag,
                created=True,
            )
        altered_comment = MoloComment.objects.get(pk=comment.pk)
        self.assertFalse(altered_comment.is_removed)

    def test_auto_remove_for_non_remove_flag(self):
        comment = self.mk_comment('first comment')
        comment.save()
        comment_approved_flag = self.mk_comment_flag(
            comment,
            CommentFlag.MODERATOR_APPROVAL)
        comment_approved_flag.save()
        with self.settings(COMMENTS_FLAG_THRESHHOLD=1):
            signals.comment_was_flagged.send(
                sender=comment.__class__,
                comment=comment,
                flag=comment_approved_flag,
                created=True,
            )
        altered_comment = MoloComment.objects.get(pk=comment.pk)
        self.assertFalse(altered_comment.is_removed)


class CommentingSettingsTest(TestCase, MoloTestCaseMixin):
    """Test if the anonymous commengting alias value is set properly."""

    def setUp(self):
        self.mk_main()
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)
        self.user = User.objects.create_user(
            'test', 'test@example.org', 'test')
        self.content_type = ContentType.objects.get_for_model(self.user)
        self.yourmind = self.mk_section(
            self.section_index, title='Your mind')
        self.article1 = self.mk_article(
            title='article 1', slug='article-2', parent=self.yourmind)
        self.setting = CommentingSettings.for_site(self.site)

        self.french = SiteLanguageRelation.objects.create(
            language_setting=Languages.for_site(self.site),
            locale='fr',
            is_active=True)
        self.translated_article = self.mk_article_translation(
            self.article1, self.french,
            title=self.article1.title + ' in french',
            subtitle=self.article1.subtitle + ' in french')

    def test_get_comments_anonymous(self):
        article = self.article1
        MoloComment.objects.create(
            content_object=article, object_pk=article.id,
            content_type=ContentType.objects.get_for_model(article),
            site=Site.objects.get_current(), user=self.user,
            comment='This is a comment, you dig?', submit_date=timezone.now())
        response = self.client.get(
            reverse('molo.commenting:more-comments', args=(article.pk,)))
        self.assertContains(response, "Anonymous")

    def test_get_comments_anonymous_alias(self):
        self.setting.commenting_anonymous = "Little Sister"
        self.setting.save()
        article = self.article1
        MoloComment.objects.create(
            content_object=article, object_pk=article.id,
            content_type=ContentType.objects.get_for_model(article),
            site=Site.objects.get_current(), user=self.user,
            comment='This is another comment', submit_date=timezone.now())
        response = self.client.get(
            reverse('molo.commenting:more-comments', args=(article.pk,)))
        self.assertContains(response, "Little Sister")

    def test_anonymous_comment_translation(self):
        article = self.article1
        MoloComment.objects.create(
            content_object=self.translated_article,
            object_pk=self.translated_article.id,
            content_type=ContentType.objects.get_for_model(article),
            site=Site.objects.get_current(), user=self.user,
            comment='This is another comment for French',
            submit_date=timezone.now())
        response = self.client.get(
            reverse('molo.commenting:more-comments', args=(
                self.translated_article.pk,)))
        self.assertContains(response, "This is another comment for French")
        # we test for translation of anonymous in project tests
        self.assertContains(response, "Anonymous")
