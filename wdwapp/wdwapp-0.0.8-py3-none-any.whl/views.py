""" Main programm 

Show wheater data and mamange configuration

To do
- Add message to send with alarm
- Add authentication to allow some users to change values and/or
  configuration data.
- Added auth.secret in ini files. Please merge your ini files with them on
  http://static.frkb.fr/wdwapp
"""
import pdb
import colander
import deform.widget

from wdwapp import __version__, __year__

from pyramid.httpexceptions import HTTPFound
from pyramid.view import view_config

from pyramid.httpexceptions import HTTPFound
from pyramid.security import (
    remember,
    forget,
)

from .models import (
    DBSession,
    Location,
    Sensor,
    WeatherData,
)

from sqlalchemy import desc, func

from datetime import datetime

class WikiPage(colander.MappingSchema):
    title = colander.SchemaNode(colander.String())
    body = colander.SchemaNode(
        colander.String(),
        widget=deform.widget.RichTextWidget()
    )

class WeatherViews(object):
    def __init__(self, request):
        self.request = request
        self.mode = ''
        self.version = __version__
        self.year = __year__
        self.stg = self.request.registry.settings


    @property
    def wiki_form(self):
        schema = WikiPage()
        btns=['submit',]
        if self.mode == 'e':
            btns.append('delete')
        return deform.Form(schema, buttons=btns)


    @property
    def reqts(self):
        return self.wiki_form.get_widget_resources()


    @view_config(route_name='overview', renderer='templates/overview.pt')
    def overview(self):

        """Main view with an overview of locations
        """

        # Load session data
        session = self.request.session

        # Get last reading time
        lt = DBSession.query(func.max(WeatherData.timestp))
        #pdb.set_trace()
        ltime = lt[0][0].strftime('le %d %b à %H:%M')
        
        # Retrieve and read last data for active locations
        datas = []
        for loc in DBSession.query(Location).filter_by(active = True).order_by('rank'):
            lt = DBSession.query(func.max(WeatherData.timestp)).filter_by(lid = loc.id)[0][0]
            wdt = DBSession.query(WeatherData).filter_by(lid = loc.id, timestp = lt)[0]
            datas.append({'id': loc.id,
                'name': loc.name,
                'temperature': wdt.temperature,
                'humidity': wdt.humidity,
                'tunit': '°' + self.stg['wd.t_unit'].upper()})
        #pdb.set_trace()

        return dict(ltime=ltime, datas=datas)

    
    @view_config(route_name='detail', renderer='templates/detail.pt')
    def detail(self):

        """Detail of a location.
            Display the list of last 24h.
        """
        
        lid = self.request.matchdict['lid']
        lname = DBSession.query(Location.name, Location.sid).filter_by(id = lid)[0][0]
        datas = DBSession.query(WeatherData).\
                filter_by(lid = lid).\
                filter(func.MINUTE(WeatherData.timestp) == 0).\
                order_by(desc('timestp')).limit(96).all()
        return dict(lname = lname, datas = datas,
            tunit = '°' + self.stg['wd.t_unit'].upper())


    @view_config(route_name='wikipage_add',
                 renderer='wikipage_addedit.pt')
    def wikipage_add(self):
        self.mode = 'a'
        form = self.wiki_form.render()

        if 'submit' in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = self.wiki_form.validate(controls)
            except deform.ValidationFailure as e:
                # Form is NOT valid
                return dict(form=e.render())

            # Form is valid, Add a new page to the database
            new_title = appstruct['title']
            new_body = appstruct['body']
            DBSession.add(Page(title=new_title, body=new_body))

            # Get the new ID and redirect
            page = DBSession.query(Page).filter_by(title=new_title).one()
            new_uid = page.uid

            # Now visit new page
            url = self.request.route_url('wikipage_view', uid=new_uid)
            return HTTPFound(url)

        return dict(form=form)

    @view_config(route_name='wikipage_edit',
                 renderer='wikipage_addedit.pt')
    def wikipage_edit(self):
        uid = self.request.matchdict['uid']
        page = DBSession.query(Page).filter_by(uid=uid).one()

        self.mode = 'e'
        wiki_form = self.wiki_form

        if 'submit' in self.request.params:
            controls = self.request.POST.items()
            try:
                appstruct = wiki_form.validate(controls)
            except deform.ValidationFailure as e:
                return dict(page=page, form=e.render())

            # Change the content and redirect to the view
            page.title = appstruct['title']
            page.body  = appstruct['body']

            url = self.request.route_url('wikipage_view', uid=uid)
            return HTTPFound(url)
        
        if 'delete' in self.request.params:
            session = self.request.session
            session['msg'] = 'Page "' + page.title + '" deleted.'
            DBSession.delete(page)

            url = self.request.route_url('wiki_view')
            return HTTPFound(url)

        form = wiki_form.render(dict(
            uid=page.uid, title=page.title, body=page.body)
        )

        return dict(page=page, form=form)

    @view_config(route_name='home')
    def home(self):
        first = self.request.matchdict['first']
        last = self.request.matchdict['last']
        return {
            'name': 'Home View',
            'first': first,
            'last': last
        }

