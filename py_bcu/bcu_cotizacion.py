# -*- coding: utf-8 -*-
import sys
from datetime import datetime

import zeep


def get_ultimo_cierre():
    """Retorna la fecha de ultimo cierre.

    Info: https://es.scribd.com/document/371380764/Especificacion-WS-Cotizaciones página 7.

    :return: datetime.date
    """
    client = get_soap_client('awsultimocierre')
    result = client.service.Execute()

    return result


def get_cotizacion(fecha=None, moneda=2225, grupo=0):
    """Retorna la cotización solicitada según los parámetros pasados.
    Por defecto se devuelve la cotización de DLS. USA BILLETE para la
    última fecha de cierre disponible y el grupo 0.

    Info: https://es.scribd.com/document/371380764/Especificacion-WS-Cotizaciones página 4.

    :param fecha: string - Fecha en formato AAAA-MM-DD de la cotización deseada.
    :param moneda: int - Código de moneda deseada.
    :param grupo: int - Código de grupo deseado
    :return: (float, float) - Tupla con los valores de compra y venta respectivamente.
    """
    if fecha is not None:
        try:
            fecha = datetime.strptime(fecha, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError("Formato de fecha no es AAAA-MM-DD")
    else:
        fecha = get_ultimo_cierre()

    fecha = fecha.strftime("%Y-%m-%d")

    params = {
        'FechaDesde': fecha,
        'FechaHasta': fecha,
        'Grupo': grupo,
        'Moneda': [
            {'item': moneda}
        ]
    }

    client = get_soap_client('awsbcucotizaciones')
    result = client.service.Execute(params)

    return (
        result.datoscotizaciones["datoscotizaciones.dato"][0]["TCC"],
        result.datoscotizaciones["datoscotizaciones.dato"][0]["TCV"]
    )


def get_monedas_valores(grupo=0):
    """Retorna la lista de monedas y valores posible para un grupo dado.

    Info: https://es.scribd.com/document/371380764/Especificacion-WS-Cotizaciones página 6.

    :param grupo: int - Código de grupo deseado
    :return: [{'Codigo': int, 'Nombre': string }]
    """
    params = {
        'Grupo': grupo,
    }

    client = get_soap_client('awsbcumonedas')
    result = client.service.Execute(params)

    return result


def get_soap_client(ws):
    """ Retonra el cliente SOAP para el wedservice pasado por parámetro.
    Webservices disponibles: https://es.scribd.com/document/371380764/Especificacion-WS-Cotizaciones

    :param ws: string - Nombre del webservice deseado.
    :return: zeep.Client
    """
    wsdl = 'https://cotizaciones.bcu.gub.uy/wscotizaciones/servlet/{0}?wsdl'.format(ws)
    return zeep.Client(wsdl=wsdl)


if __name__ == '__main__':
    """Permite ejecutar las funciones desde la línea de comandos.
    Info: https://stackoverflow.com/a/52837375/2686243
    """
    if len(sys.argv) > 1:
        globals()[sys.argv[1]]()
