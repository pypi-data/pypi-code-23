# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
import datetime
from slugify import slugify
from trytond.model import ModelView, ModelSQL, fields, Workflow
from trytond.pool import Pool
from trytond.pyson import Eval
from trytond.transaction import Transaction

__all__ = [
    'Article', 'ArticleRelation'
]

STATES = {
    'readonly': ~Eval('active', True),
    }
DEPENDS = ['active']


class Article(Workflow, ModelSQL, ModelView):
    "CMS Article"
    __name__ = 'cms.article'

    name = fields.Char(
        'Name or Title', required=True, translate=True, select=True)
    slug = fields.Char('URI Slug', select=True,
        states=STATES, depends=DEPENDS)
    active = fields.Boolean('Active', select=True)
    author = fields.Many2One('party.party', 'Author')
    priority = fields.Integer('Sort Priority', required=True, select=True)
    publish_date = fields.DateTime('Publish Date')
    archive_date = fields.DateTime('Archived Date')
    parents = fields.Many2Many('cms.article-cms.article',
              'child', 'parent', 'Parents', states=STATES, depends=DEPENDS)
    children = fields.Many2Many('cms.article-cms.article',
               'parent', 'child', 'Children', states=STATES, depends=DEPENDS)
    summary = fields.Text('Summary', translate=True)
    content = fields.Text('Content', translate=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived')
    ], 'State', required=True, select=True, readonly=True)

    @fields.depends('name', 'slug')
    def on_change_with_slug(self):
        if self.name and not self.slug:
            return slugify(self.name, only_ascii=True)
        return self.slug

    @classmethod
    def __setup__(cls):
        super(Article, cls).__setup__()
        cls._order.insert(0, ('priority', 'ASC'))
        cls._order.insert(1, ('publish_date', 'DESC'))
        cls._transitions |= set((
                ('draft', 'published'),
                ('published', 'draft'),
                ('published', 'archived'),
                ('archived', 'draft'),
        ))
        cls._buttons.update({
            'archive': {
                'invisible': Eval('state') != 'published',
            },
            'publish': {
                'invisible': Eval('state').in_(['published', 'archived']),
            },
            'draft': {
                'invisible': Eval('state') == 'draft',
            }
        })

    @classmethod
    @ModelView.button
    @Workflow.transition('archived')
    def archive(cls, articles):
        for article in articles:
            article.archive_date = datetime.datetime.now()

    @classmethod
    @ModelView.button
    @Workflow.transition('published')
    def publish(cls, articles):
        for article in articles:
            article.publish_date = datetime.datetime.now()

    @classmethod
    @ModelView.button
    @Workflow.transition('draft')
    def draft(cls, articles):
        for article in articles:
            article.publish_date = None
            article.archive_date = None

    @staticmethod
    def default_state():
        if 'published' in Transaction().context:
            return 'published'
        return 'draft'


class ArticleRelation(ModelSQL):
    "CMS Article Relationships"
    __name__ = 'cms.article-cms.article'
    _table = 'cms_article_rel'
    parent = fields.Many2One('cms.article', 'Parent', ondelete='CASCADE',
             required=True, select=True)
    child = fields.Many2One('cms.article', 'Child', ondelete='CASCADE',
            required=True, select=True)



