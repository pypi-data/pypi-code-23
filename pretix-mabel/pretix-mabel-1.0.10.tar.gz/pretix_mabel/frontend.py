from enum import Enum
import json
from datetime import datetime, timedelta
from django.utils.translation import pgettext_lazy, ugettext as _
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Q
import raven_auth
from django import forms
import requests

from pretix.base.models.orders import OrderPosition, Order
from pretix.base.models.event import Event
from pretix.presale.views import CartMixin
from pretix.presale.checkoutflow import TemplateFlowStep

from .models import TicketLimit


MABEL_USER_TYPE_KEY = "mabel_user_type"


class LoginForm(forms.Form):
    email = forms.CharField(label='Email', max_length=100)
    password = forms.CharField(label='Password', widget=forms.PasswordInput)


class UserType(Enum):
    COLLEGE_STUDENT = "COLLEGE_STUDENT"
    COLLEGE_ALUMNUS = "COLLEGE_ALUMNUS"
    UNLIMITED = "UNLIMITED"
    EXTERNAL = "EXTERNAL"

    def __str__(self):
        return self.value


class MabelStep(CartMixin, TemplateFlowStep):
    priority = 10
    identifier = "auth"
    template_name = "pretix_mabel/loginform.html"
    label = pgettext_lazy('mabel', 'Authentication')

    def is_applicable(self, request):
        return True

    def get_raven_url(self, request):
        url = self.get_raven_redirect_url(request)
        return str(raven_auth.Request(url=url, desc="Ticketing"))

    def get_raven_redirect_url(self, request):
        return request.scheme + "://" +request.get_host() + self.get_step_url(request)

    def is_logged_in(self, request):
        return "email" in self.cart_session and MABEL_USER_TYPE_KEY in request.session

    def check_limit(self, email, user_type=UserType.EXTERNAL, warn=False):
        limits = TicketLimit.objects.filter(event=self.request.event)
        result = True
        for l in limits:
            print(l.item)
            if user_type == UserType.COLLEGE_STUDENT:
                limit = l.current_student_limit
            elif user_type == UserType.COLLEGE_ALUMNUS:
                limit = l.alumnus_limit
            elif user_type == UserType.UNLIMITED:
                continue
            else:
                limit = l.external_limit

            for p in self.positions:
                print([1 for p in self.positions if p.item == l.item])
            in_cart = len([1 for p in self.positions if p.item == l.item])

            positions = OrderPosition.objects.filter(
                order__event=self.request.event,
                order__email=email,
                item=l.item
            ).filter(
                Q(order__status=Order.STATUS_PENDING) | 
                Q(order__status=Order.STATUS_PAID)
            )
            print(positions)
            in_books = len(positions)
            if in_cart + in_books > limit:
                if warn:
                    messages.error(self.request,
                                     _("You may only book %(limit)d %(limit_type)s tickets in total, "
                                       "but you have previously booked %(in_books)d and now have %(in_cart)d in your cart. "
                                       "Please go back and remove some items before proceeding.") % {
                                         "in_books": in_books,
                                         "in_cart": in_cart,
                                         "limit": limit,
                                         "limit_type": str(l.item)
                                     })
                result = False

        return result

    def get(self, request):
        # three expected options - logout, raven callback or first load
        self.request = request
        new_login = False

        logout = request.GET.get("logout")
        if logout is not None:
            if "email" in self.cart_session:
                del self.cart_session["email"]
            if MABEL_USER_TYPE_KEY in self.request.session:
                del self.request.session[MABEL_USER_TYPE_KEY]

        # check if this is after a raven callback
        wls = request.GET.get("WLS-Response")
        if wls is not None:
            r = raven_auth.Response(wls)

            now = datetime.now()
            url = self.get_raven_redirect_url(request)
            if (r.success and r.url == url):
                if (r.issue > now - timedelta(minutes=10)):
                #if "current" in r.ptags:
                    crsid = r.principal
                    # TODO: check with ibis whether current college or university students
                    ibis = requests.get(request.event.settings.ibis_proxy_url  + "?crsid=" + crsid)
                    if ibis.status_code == 200:
                        json = ibis.json()
                        allowed_ids = [i.strip() for i in request.event.settings.ibis_institution_id.split(",")]
                        if any(
                                i["cancelled"] == False and 
                                any(allowed == i["instid"] for allowed in allowed_ids)
                                for i in json["institutions"]):
                            user_type = UserType.COLLEGE_STUDENT
                        else:
                            user_type = UserType.EXTERNAL
                    else:
                        user_type = UserType.EXTERNAL

                    email = r.principal + "@cam.ac.uk"

                    self.cart_session['email'] = email
                    self.request.session[MABEL_USER_TYPE_KEY] = user_type.value
                    new_login = True

        if self.is_completed(request, True) and new_login:
            return redirect(self.get_next_url(request))

        return self.render()

    def post(self, request):
        self.request = request
        email = request.POST.get("email")
        password = request.POST.get("password")

        print(request.event.settings.google_sheets_API_key)
        sheet_url = "https://sheets.googleapis.com/v4/spreadsheets/%(id)s/values/A2:C?key=%(key)s" % {
            "key": request.event.settings.google_sheets_API_key,
            "id": request.event.settings.user_sheet_id
        }
        print(sheet_url)
        r = requests.get(sheet_url)
        if r.status_code != 200:
            passed = False
            messages.error(request, _("Could not contact credentials server"))
        else:
            values = r.json()["values"]
            passed = False
            for v in values:
                if v[0] == email:
                    if v[1] == password:
                        passed = True
                        user_type = v[2]
                    break

        if passed:
            self.cart_session['email'] = email
            if user_type == "Student":
                self.request.session[MABEL_USER_TYPE_KEY] = UserType.COLLEGE_STUDENT.value
            elif user_type == "Alumnus":
                self.request.session[MABEL_USER_TYPE_KEY] = UserType.COLLEGE_ALUMNUS.value
            elif user_type == "Unlimited":
                self.request.session[MABEL_USER_TYPE_KEY] = UserType.UNLIMITED.value
            else:
                self.request.session[MABEL_USER_TYPE_KEY] = UserType.EXTERNAL.value

            if self.is_completed(request, True):
                return redirect(self.get_next_url(request))

        if not passed:
            messages.error(request,
                           _("Those credentials were not accepted"))

        return self.render()

    def is_completed(self, request, warn=False):
        print("Checking if completed")
        self.request = request

        if not self.is_logged_in(request):
            if warn:
                messages.warning(
                    request, _("You must log in before checking out"))
            return False

        email = self.cart_session.get("email")
        user_type = UserType[self.request.session.get(MABEL_USER_TYPE_KEY)]

        return self.check_limit(email, user_type, warn)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['step_url'] = self.get_step_url(self.request)
        ctx['raven_url'] = self.get_raven_url(self.request)
        ctx['next_url'] = self.get_next_url(self.request)
        ctx['logged_in'] = self.is_logged_in(self.request)
        ctx['login_form'] = LoginForm(
            data=self.request.POST if self.request.method == "POST" else None,
        )
        ctx['continue'] = ctx['logged_in'] and self.is_completed(self.request,False)
        # ctx['message'] = self.message
        # ctx['contact_form'] = self.contact_form
        # ctx['invoice_form'] = self.invoice_form
        # ctx['reverse_charge_relevant'] = self.eu_reverse_charge_relevant
        ctx['cart'] = self.get_cart()
        return ctx

