# coding: utf-8
from optparse import make_option
from django.core.management import BaseCommand
from onivoro.sincronizador import Sincronizador
from onivoro.models import FonteExterna


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--fonte',
                    action='store',
                    type='string',
                    default='',
                    dest='nome_fonte'),
    )

    help = """Atualiza dados externos"""

    def handle(self, *args, **options):
        nome_fonte = options.get('nome_fonte')

        fonte_list = FonteExterna.objects.all()
        if nome_fonte:
            fonte_list = fonte_list.filter(nome=nome_fonte)

        for fe in fonte_list:
            self.stdout.write(u'Atualizando %s' % fe.nome)
            s = Sincronizador(fe)
            s.sincronizar()
