# -*- coding: utf-8 -*-

"""This code is a part of Hydra Toolkit

.. module:: hydratk.extensions.security.translation.en
   :platform: Unix
   :synopsis: English language translation for Security extension
.. moduleauthor:: Petr Czaderna <pc@hydratk.org>

"""

language = {
    'name': 'English',
    'ISO-639-1': 'en'
}

msg = {
    'sec_received_cmd': ["Received command: '{0}'"],
    'msf_start': ["Starting MSF path: {0}, host: {1}, port: {2}, user: {3}, passw: {4}"],
    'msf_started': ["MSF successfully started"],
    'msf_stop': ["Stopping MSF"],
    'msf_stopped': ["MSF successfully stopped"],
    'msf_call_req': ["Calling MSF method: {0}, params: {1}"],
    'msf_call_res': ["MSF method returned {0}"],
    'zap_start': ["Starting ZAP path: {0}, host: {1}, port: {2}"],
    'zap_started': ["ZAP successfully started"],
    'zap_stop': ["Stopping ZAP"],
    'zap_stopped': ["ZAP successfully stopped"],
    'zap_spider_start': ["Starting to spider URL: {0}, params:{1}"],
    'zap_spider_finish': ["Spider finished"],
    'zap_scan_start': ["Starting to scan URL: {0}, method: {1}, params: {2}"],
    'zap_scan_finish': ["Scan finished"],
    'zap_export_start': ["Starting export type: {0}, format: {1}, output: {2}, url: {3}"],
    'zap_export_finish': ["Export finished"],
    'zap_progress': ["Progress {0}: {1}%"]
}
