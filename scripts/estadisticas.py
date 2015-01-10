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
    """
        La ejecuta manage.py cuando se le pasa el archivo como un script de django
    """
    data_dir = os.path.join(DIR, 'base/static')

    # Selecciono las incidencias que interesan para el gráfico de incidencias
    nuevas = CambioEstado.objects.filter(estado_inicial='SO').values('fecha_cambio').annotate(numero=Count('fecha_cambio'))
    cerradas = CambioEstado.objects.filter(estado_inicial='AS').values('fecha_cambio').annotate(numero=Count('fecha_cambio'))
    indice_nuevas = indice_cerradas = 0

    # Escribo en incidencias.csv las incidencias
    with open(os.path.join(data_dir, 'incidencias.csv'), 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['fecha','nuevas','cerradas'])
        # Escribo en el csv intercalando las incidencias de ambas listas
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

        # Escribo las incidencias que quedan por escribir en el csv
        if len(nuevas) > len(cerradas):
            for i in nuevas[len(cerradas):]:
                writer.writerow([i['fecha_cambio'].strftime(FORMATO_FECHA), i['numero'], ''])
        elif len(cerradas) > len(nuevas):
            for i in cerradas[len(nuevas):]:
                writer.writerow([i['fecha_cambio'].strftime(FORMATO_FECHA), '', i['numero']])

    def indexar(estado_inicial, estado_final):
        """
            Indexa las incidencias por el tiempo que pasaron desde estado_inicial a estado_final.
            El estado_inicial y estado_final son los de la relación, sin embargo, a la hora de
            medir la duración siempre hay que coger los estados finales.
        """
        cambios_final = CambioEstado.objects.filter(estado_final=estado_inicial)
        total = 0
        index = {}
        for cambio in cambios_final:
            try:
                cambio_inicial = CambioEstado.objects.filter(estado_final=estado_final).get(incidencia=cambio.incidencia)
            except CambioEstado.DoesNotExist:
                continue
            total += 1
            diferencia_tiempo = cambio_inicial.fecha_cambio - cambio.fecha_cambio
            if diferencia_tiempo.days not in index:
                index[diferencia_tiempo.days] = 0
            index[diferencia_tiempo.days] += 1
        return index, total

    def escribir_datos(index, csvfile, total):
        """
            Función auxiliar para reducir la repetición de código
        """
        writer = csv.writer(csvfile)
        writer.writerow(['duracion', 'dato'])
        for duracion in index:
            writer.writerow([duracion, index[duracion]/total * 100])

    # Datos para las duraciones de incidencias asignadas
    index, total = indexar('AC', 'AS')
    with open(os.path.join(data_dir, 'asignada.csv'), 'w', newline='') as csvfile:
        escribir_datos(index, csvfile, total)

    # Datos para las duraciones de incidencias cerradas con éxito
    index, total = indexar('AS', 'CTE')
    with open(os.path.join(data_dir, 'cerrada-exito.csv'), 'w', newline='') as csvfile:
        escribir_datos(index, csvfile, total)

    # Datos para las duraciones de incidencias cerradas con fracaso
    index, total = indexar('AS', 'CTF')
    with open(os.path.join(data_dir, 'cerrada-fracaso.csv'), 'w', newline='') as csvfile:
        escribir_datos(index, csvfile, total)
