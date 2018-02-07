# -*- coding: utf-8 -*-

from django.conf import settings
from django.core.urlresolvers import reverse
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.views.decorators.cache import never_cache
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from djangohelpers.utils import gen_url as gen_hash

from models import EmailUser, EmailUserForm, manual_create_email_user

@never_cache
def auth(request, user_id, token):
    get_user = get_object_or_404(User, pk=user_id)
    user = authenticate(email=get_user.email, token=token)
    if user is not None:
        if user.is_active:
            login(request, user)
    return render(request, "user/auth.html", {"user": user})


@never_cache
def login_view(request):
    sended = False
    if request.method == 'POST': 
        form = EmailUserForm(request.POST) 
        if form.is_valid(): # All validation rules pass
            email = form.cleaned_data['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                username = email.split('@')[0].lower()
                bad_username = True
                while bad_username:
                    try: # check if username taken already
                        user = User.objects.get(username=username)
                    except User.DoesNotExist: # good we can use it
                        bad_username = False
                    else: # gen new username
                        username = "%s_%s" % (username, gen_hash(2))
                password = '%s' % gen_hash(20)
                user = User.objects.create_user(\
                    email=form.cleaned_data["email"], 
                    username=username,
                    password=password) 
                user.save()

            try:    
                token = user.emailuser.generate_token()
            except:
                manual_create_email_user(user)
                token = user.emailuser.generate_token()
            #try:
            #if settings.DEBUG:
            #    print "Token - %s" % token
            auth_url = reverse('emailuser:auth', kwargs={"user_id": user.pk, "token":token},
                               current_app="emailuser", )
            #print auth_url
            try:
                base_url = settings.SITE_LOGIN_URL
            except AttributeError:
                base_url = settings.SITE_URL
            send_mail(u'Вход на сайт %s' % base_url, 
                      (u'\nДля входа на сайт пройдите по ссылке:'
                       u'%s%s \n' 
                       u'Если у Вас возникли проблемы со входом '
                       u'напишите письмо на %s' % (settings.SITE_URL,
                                                   auth_url,
                                                   settings.SERVER_EMAIL)),
                       settings.SERVER_EMAIL , [email], fail_silently=settings.DEBUG)
            
            sended = True
    else:
        form = EmailUserForm()
    return render(request, "user/login.html", {'form':form, 'sended':sended,
                                               "SERVER_EMAIL":settings.SERVER_EMAIL})


@never_cache
def logout_view(request):
    logout(request)
    return redirect('/')
