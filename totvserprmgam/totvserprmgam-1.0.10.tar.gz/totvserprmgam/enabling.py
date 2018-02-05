# -*- coding: utf-8 -*-
from totvserprmgam.baseapi import BaseApi


class EnablingStudent(BaseApi):
    dataservername = 'EduHabilitacaoAlunoData'

    def create(self, **kwargs):
        return super(EnablingStudent, self).create({
            'NewDataSet':{
                'SHabilitacaoAluno':{
                    'CODCOLIGADA': kwargs.get('codcoligada'),
                    'IDHABILITACAOFILIAL': kwargs.get('idhabilitacaofilial'),
                    'RA': kwargs.get('ra'),
                    'CODSTATUS': kwargs.get('codstatus'),
                    'MEDIAVESTIBULAR':0.0000,
                    'REALIZOUPROVAO': 'N',
                    'INDICECARENCIA': 0.0000,
                    'CODCURSO': kwargs.get('codcurso'),
                    'CODHABILITACAO': 1,
                    'CODGRADE': 1,
                    'CODFILIAL': 1,
                    'NOMECURSO': kwargs.get('nomecurso'),
                    'NOMETURNO': kwargs.get('nometurno'),
                    'CODTURNO': kwargs.get('codturno'),
                    'CODCAMPUS': kwargs.get('codcampus')
                },
                'SHabilitacaoAlunoCompl':{
                    'CODCOLIGADA': kwargs.get('codcoligada'),
                    'IDHABILITACAOFILIAL': kwargs.get('idhabilitacaofilial'),
                    'RA': kwargs.get('ra')
                }
            }
        }, 'CODCOLIGADA={0};IDHABILITACAOFILIAL={1};RA={2}'.format(kwargs.get('codcoligada'), kwargs.get('idhabilitacaofilial'), kwargs.get('ra')))