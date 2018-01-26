#!/usr/bin/env python
# -*- coding: utf-8 -*-

#    Copyright (c) 2017, 2018 Ying Jun <WandyYing@users.noreply.github.com>

# Default seconds to wait for page elements to appear before performing actions
TINY_TIMEOUT = 0.1
MINI_TIMEOUT = 2
SMALL_TIMEOUT = 5
LARGE_TIMEOUT = 10
EXTREME_TIMEOUT = 30


# Waiting
POLL_FREQUENCY = 0.2
BROWSER_BREATH_DELAY = 0.5

'''
This adds wait_for_angularjs() after wait_for_ready_state_complete()
after various browser actions.  Setting this to True may improve reliability
of AngularJs applications at the cost of speed.
NOTE: This requires WAIT_FOR_RSC_ON_PAGE_LOADS and/or WAIT_FOR_RSC_ON_CLICKS
to be True since it's part of wait_for_ready_state_complete().
'''
# Called after each wait_for_ready_state_complete()
WAIT_FOR_ANGULARJS = True

# JavaScript
JQUERY_URL = '//code.jquery.com/jquery-1.11.3.min.js'
JQUERY_BOOTSTRAP = 'var a=document.getElementsByTagName(\'head\')[0];' \
                   'var b=document.createElement(\'script\');' \
                   'b.type=\'text/javascript\';b.src=document.location.' \
                   'protocol+\'%(jquery_url)s\';a.appendChild(b);'

NG_WRAPPER = '%(prefix)s' \
             'var $inj;try{$inj=angular.element(document.querySelector(' \
             '\'[data-ng-app],[ng-app],.ng-scope\')||document).injector()||' \
             'angular.injector([\'ng\'])}catch(ex){' \
             '$inj=angular.injector([\'ng\'])};$inj.get=$inj.get||$inj;' \
             '$inj.get(\'$browser\').notifyWhenNoOutstandingRequests(%(handler)s)' \
             '%(suffix)s'

PAGE_READY_WRAPPER = 'var cb=arguments[arguments.length-1];if(window.jQuery){' \
                     '$(document).ready(function(){cb(true)})}else{' \
                     '%(jquery_bootstrap)s' \
                     'cb(document.readyState===\'complete\' && document.body && ' \
                     'document.body.childNodes.length)}'
# NG_WRAPPER = '%(prefix)s' \
#              'var $elm=document.querySelector(' \
#              '\'[data-ng-app],[ng-app],.ng-scope\')||document;' \
#              'if(window.angular && angular.getTestability){' \
#              'angular.getTestability($elm).whenStable(%(handler)s)' \
#              '}else{' \
#              'var $inj;try{$inj=angular.element($elm).injector()||' \
#              'angular.injector([\'ng\'])}catch(ex){' \
#              '$inj=angular.injector([\'ng\'])};$inj.get=$inj.get||' \
#              '$inj;$inj.get(\'$browser\').' \
#              'notifyWhenNoOutstandingRequests(%(handler)s)}' \
#              '%(suffix)s'