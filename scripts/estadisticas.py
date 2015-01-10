# Script para generar las estadísticas a un archivo json
# Tiene que ejecutarse con django-extensions instalado y después
# ./manage.py runscript estadisticas

import csv
import datetime
import os.path
from django.db.models import Count
from base.models import Incidencia, CambioEstado

DIR = '/home/kudrom/datos/clase/pgpi/GIT'
FORMATO_FECHA = '%d-%m-%Y'

def run():
    data_dir = os.path.join(DIR, 'base/static')
    nuevas = CambioEstado.objects.filter(estado_inicial='SO').values('fecha_cambio').annotate(numero=Count('fecha_cambio'))
    cerradas = CambioEstado.objects.filter(estado_inicial='AS').values('fecha_cambio').annotate(numero=Count('fecha_cambio'))
    indice_nuevas = indice_cerradas = 0
    with open(os.path.join(data_dir, 'incidencias.csv'), 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['fecha','nuevas','cerradas'])
        for i in range(min([len(nuevas), len(cerradas)])):
            fecha = max([nuevas[i]['fecha_cambio'], cerradas[i]['fecha_cambio']])
            row = [fecha.strftime(FORMATO_FECHA), '', '']
            if fecha == nuevas[i]['fecha_cambio']:
                row[1] = nuevas[i]['numero']
                indice_nuevas += i
            if fecha == cerradas[i]['fecha_cambio']:
                row[2] = cerradas[i]['numero']
                indice_cerradas += 1
            writer.writerow(row)
        if len(nuevas) > len(cerradas):
            for i in nuevas[len(cerradas):]:
                writer.writerow([i['fecha_cambio'].strftime(FORMATO_FECHA), i['numero'], ''])
        elif len(cerradas) > len(nuevas):
            for i in cerradas[len(nuevas):]:
                writer.writerow([i['fecha_cambio'].strftime(FORMATO_FECHA), '', i['numero']])
