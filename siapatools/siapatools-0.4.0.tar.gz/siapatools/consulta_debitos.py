import pandas as pd
from pandas import ExcelWriter
from siapatools import SIAPA

'''
Consulta os débitos de uma lista de RIPS, em todo ou histórico ou em
exercícios selecionados
'''


def consulta_debitos(lista_rips, exercicio=None):
    '''
    Consulta os débitos de uma lista de RIPS, em todo ou histórico ou em
    exercícios selecionados

    .:param lista_rips(list) - Lista de RIPS (sem dv) para consulta.
    .:param exercicio(int, list) - Ano do exercício da data base de cálculo
                                   para seleção dos débitos.
    '''
    siapa = SIAPA()

    DATA_INICIAL_SPU = 1964
    if exercicio is None:
        siapa.minAnoDtBase = DATA_INICIAL_SPU
    else:
        if isinstance(exercicio, list):
            siapa.minAnoDtBase = min(exercicio)
        elif isinstance(exercicio, int):
            siapa.minAnoDtBase = exercicio
            exercicio = [exercicio]

    debitos_encontrados = pd.DataFrame()
    for n, chunk in enumerate(siapa.debitos):
        # filtra apenas por número do RIP
        if exercicio is None:
            query = chunk["nu_rip"].isin(lista_rips)
        # filtra por núemro do RIP e exercício
        else:
            filtra_ano = lambda x: x.year in exercicio
            query = (chunk["da_base_calculo"].map(filtra_ano)) & \
                    (chunk["nu_rip"].isin(lista_rips))

        chunk = chunk[query]

        debitos_encontrados = debitos_encontrados.append(chunk)

    return debitos_encontrados
