# -*- coding: utf-8 -*-

"""This code is a part of Hydra Toolkit

.. module:: hydratk.extensions.security.translation.cs
   :platform: Unix
   :synopsis: Czech language translation for Security extension
.. moduleauthor:: Petr Rašek <bowman@hydratk.org>

"""

language = {
    'name': 'Čeština',
    'ISO-639-1': 'cs'
}


msg = {
    'sec_received_cmd': ["Obdržen příkaz: '{0}'"],
    'msf_start': ["Spouštím MSF cesta: {0}, host: {1}, port: {2}, user: {3}, heslo: {4}"],
    'msf_started': ["MSF úspěšně spuštěn"],
    'msf_stop': ["Zastavuji MSF"],
    'msf_stopped': ["MSF úspěšně zastaven"],
    'msf_call_req': ["Volám MSF metodu: {0}, parametry: {1}"],
    'msf_call_res': ["MSF metoda vrátila {0}"],
    'zap_start': ["Spouštím ZAP cesta: {0}, host: {1}, port: {2}"],
    'zap_started': ["ZAP úspěšně spuštěn"],
    'zap_stop': ["Zastavuji ZAP"],
    'zap_stopped': ["ZAP úspěšně zastaven"],
    'zap_spider_start': ["Pouštím spider na URL: {0}, parametry: {1}"],
    'zap_spider_finish': ["Spider dokončen"],
    'zap_scan_start': ["Pouštím scan na URL: {0}, metoda: {1}, parametry: {2}, url: {3}"],
    'zap_scan_finish': ["Scan dokončen"],
    'zap_export_start': ["Spouštím export typ: {0}, formát: {1}, output: {2}"],
    'zap_export_finish': ["Export dokončen"],
    'zap_progress': ["Průběh {0}: {1}%"]
}
