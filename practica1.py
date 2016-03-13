#!/usr/bin/python
# -*- coding: utf-8 -*-

# Jesús Galán Barba
# Ing. en Sistemas de Telecomunicaciones

import webapp
import sys
import csv
import urllib


hostname = "localhost"
port = 1234

class acortador_URLs(webapp.webApp):

    diccionario_URLs = {} # Diccionario donde la clave es la URL acortada
    diccionario_URLs_acortadas = {} # Diccionario donde la clave es la URL original
    with open('redireccion.csv') as fich:
        reader = csv.reader(fich)
        for row in reader:
            URL_acortada = row[0]
            URL_original = row[1]
            diccionario_URLs[URL_acortada] = URL_original
            diccionario_URLs_acortadas[URL_original] = URL_acortada

    URL_inicial = "http://" + hostname + ":" + str(port) + "/"

    # 'Parseamos' la respuesta HTTP para encontrar el metodo, recurso y cuerpo
    def parse(self, request):
        try:
            metodo = request.split(' ',2)[0]
            recurso = request.split(' ',2)[1]
            try:
                cuerpo = request.split('\r\n\r\n')[1]
            except IndexError:
                cuerpo =""
        except IndexError:
            return None

        elementos_peticion = [metodo, recurso, cuerpo]
        return elementos_peticion

    def obtener_lista_URLs(self):
        lista = ""
        for url in self.diccionario_URLs:
            URL_acortada = url
            URL_original = self.diccionario_URLs[URL_acortada]
            lista = lista + "<p><a href=" +  URL_original + ">" + URL_original + "</a>" \
                    " --> " + "<a href=" + URL_acortada + ">" + \
                    URL_acortada + "</a></p>"

        return lista

    def process(self, elementos_peticion):
        try:
            metodo = elementos_peticion[0]
            recurso = elementos_peticion[1]
            cuerpo = elementos_peticion[2]
        except TypeError:
            httpCode = "400 Bad Request"
            htmlResp = "<html><body>Error en la solitud!</body></html>"
            return (httpCode, htmlResp)

        if metodo == "GET" and recurso == "/":
            info_incial = "<p><h2> Aplicacion web que acorta URLs</h2></p>"
            formulario = '<form action="http://localhost:1234"' + \
                         ' method="POST" accept-charset="UTF-8">' + \
                         'Introducir URL: <input type="text" name="url">' + \
                         '<input type="submit" value="Acortar"></p></form>'

            if len(self.diccionario_URLs) != 0:
                info_lista_URLs = "<p><font color='green'><h4>Lista de URLs ya " + \
                                    "acortadas en este momento:</h4></font></p>" + \
                                    "<h5>(Accede, si lo deseas, a las paginas a " + \
                                    "traves de los enlaces disponibles)</h5>"
                lista_URLs = self.obtener_lista_URLs()
            else:
                info_lista_URLs = "<p><font color='green'><h4>Lista de URLs " + \
                                    "acortadas, actualmente vacia!</h4></font></p>"
                lista_URLs = ""

            httpCode = "200 OK"
            htmlResp = "<html><body>" + info_incial + formulario + info_lista_URLs + \
                        lista_URLs + "</body></html>"

        elif metodo == "POST" and recurso == "/":

            info_incial = "<p><h2> Aplicacion web que acorta URLs</h2></p>"
            url_cuerpo = cuerpo.split("=")[1]

            if url_cuerpo == "":
                httpCode = "400 Bad Request"
                htmlResp = "<html><body><h3>Error: Formulario no correcto! " + \
                            "Vuelve a intentarlo...</h3>" + \
                            "<p>Accede a la pagina incial a traves se este enlace: " + \
                            "<a href=" + self.URL_inicial + ">" + self.URL_inicial + \
                            "</p></body></html>"
            else:
                url_cuerpo = urllib.unquote(url_cuerpo).decode('utf8')

                if url_cuerpo.split("://")[0] != "http" and url_cuerpo.split("://")[0] != "https":
                    url_cuerpo = "http://" + url_cuerpo

                try:
                    # Si encuentra una url acortada, para dicha url del cuerpo
                    # entonces, la url ya habia sido acortado anteriormente
                    # o está en la lista de las urls que maneja la apliación.
                    url_corta = self.diccionario_URLs_acortadas[url_cuerpo]
                    info_mensaje_url_ya_acort = "<font color='red'> Esta URL ya " + \
                                                "habia sido acortada previamente. " + \
                                                "Mirar lista URL acortadas!</font>"
                except KeyError:
                    # Si salta un error KeyError, quiere decir que antes no habia
                    # sido acortada la URL, es decir, no la tenemos en la lista_URLs
                    # Generamos una nueva URL acortada para la URL del cuerpo.
                    if len(self.diccionario_URLs) == 0:
                        self.indice_recurso = 0
                    else:
                        self.indice_recurso = (len(self.diccionario_URLs)-1) + 1

                    url_corta = "http://" + hostname + ":" + str(port) + "/" + str(self.indice_recurso)

                    # Introducimos la nueva url acortada en el diccionario
                    self.diccionario_URLs[url_corta] = url_cuerpo
                    # Actualizamos la lista de urls ya acortadas previamente
                    self.diccionario_URLs_acortadas[url_cuerpo] = url_corta

                    with open('redireccion.csv', 'a') as fich:
                        # Introducimos la nueva url acortada en el fichero csv
                        escribir = csv.writer(fich)
                        escribir.writerow([url_corta, url_cuerpo])

                    info_mensaje_url_ya_acort = ""

                httpCode = "200 OK"
                htmlResp = "<html><body>" + info_incial + \
                            "<p><h4>" + info_mensaje_url_ya_acort + "</h4></p>" + \
                            "<p>URL original: <a href=" + url_cuerpo + ">" + url_cuerpo + \
                            "</a> --> URL acortada: <a href=" + url_corta + ">" + \
                            url_corta + "</a></p></body></html>"


        elif metodo == "GET" and len(recurso) > 1:
            # Si la longitud del recurso es mayor que 1, quiere decir que es /num
            try:
                recurso_num = int(recurso[1:])
            except ValueError:
                httpCode = "400 Bad Request"
                htmlResp = "<html><body><h3>Error: Introduce un recurso numerico! " + \
                            "Vuelve a intentarlo...</h3>" + \
                            "<p>Accede a la pagina incial a traves se este enlace: " + \
                            "<a href=" + self.URL_inicial + ">" + self.URL_inicial + \
                            "</p></body></html>"
                return (httpCode, htmlResp)

            url_acortada = "http://" + hostname + ":" + str(port) + recurso
            try:
                url_original = self.diccionario_URLs[url_acortada]
            except KeyError:
                httpCode = "404 Not Found"
                htmlResp = "<html><body><h3>Recurso no disponible! " + \
                            "Vuelve a intentarlo...</h3>" + \
                            "<p>Accede a la pagina incial a traves se este enlace: " + \
                            "<a href=" + self.URL_inicial + ">" + self.URL_inicial + \
                            "</p></body></html>"
                return (httpCode, htmlResp)

            httpCode = "301 Moved Permanently"
            htmlResp = '<html><head><meta http-equiv="Refresh" content="3; url=' + \
    		 			url_original + '"/></head' + \
     					'<body>Seras redirigido a la siguiente URL tras 3 segundos ' + \
                        'de espera: <b>' + url_original + '</b></body></html>'

        else:
            httpCode = "405 Method Not Allowed"
            htmlResp = "<html><body>Metodo no identificado!</body></html>"

        return (httpCode, htmlResp)


if __name__ == "__main__":
    try:
        Test_URLs = acortador_URLs(hostname, port)
    except KeyboardInterrupt:
        print "\nAplicación cerrada por el usuario en el terminal!\n"
        sys.exit()
