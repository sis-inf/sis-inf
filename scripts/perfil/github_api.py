feat/orquestador
import os
import logging
import urllib.request
import json

class ClienteGitHub:
    def __init__(self, token=None):
        self.token = token or os.getenv("GITHUB_TOKEN")
        self.headers = {
            "Accept": "application/vnd.github.v3+json"
        }
        if self.token:
            self.headers["Authorization"] = f"token {self.token}"

    def obtener_repositorios(self, usuario="owner"):
        """Obtiene los repositorios del usuario desde la API de GitHub o retorna datos de respaldo si no hay token/red."""
        url = f"https://api.github.com/users/{usuario}/repos" if usuario != "owner" else "https://api.github.com/user/repos"
        
        try:
            req = urllib.request.Request(url, headers=self.headers)
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.status == 200:
                    return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            logging.warning(f"No se pudo conectar a la API de GitHub (modo local/simulación activo): {e}")
        
        # Datos de respaldo (fallback) para pruebas locales sin conexión o sin token
        return [
            {"name": "sis-inf", "stargazers_count": 5, "language": "Python", "fork": False},
            {"name": "proyecto-java", "stargazers_count": 2, "language": "Java", "fork": False}
        ]

"""
Módulo que implementa el cliente para interactuar con la API REST y GraphQL
de GitHub utilizando exclusivamente la biblioteca estándar de Python.
"""

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, Optional, Tuple


class ClienteGitHub:
    """Cliente para realizar peticiones REST y GraphQL a la API de GitHub."""

    def __init__(self, token: Optional[str] = None) -> None:
        """Inicializa el cliente de GitHub con un token opcional.

        Args:
            token (str | None): Token de acceso personal de GitHub.
        """
        self.token = token
        self.base_url = "https://api.github.com"

    def _hacer_peticion(
        self,
        url: str,
        data: Optional[bytes] = None,
        metodo: Optional[str] = None,
    ) -> Tuple[Any, Optional[str]]:
        """Realiza una petición HTTP con reintentos ante errores 5xx y manejo de errores 4xx.

        Args:
            url (str): URL completa de la petición.
            data (bytes | None): Datos en bytes para peticiones POST.
            metodo (str | None): Método HTTP (ej. 'POST').

        Returns:
            tuple[Any, str | None]: Tupla con el JSON decodificado y el encabezado Link.
        """
        headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "Python-GitHub-Client",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if data is not None:
            headers["Content-Type"] = "application/json"

        intentos = 3
        for intento in range(intentos):
            req = urllib.request.Request(
                url, data=data, headers=headers, method=metodo
            )
            try:
                with urllib.request.urlopen(req) as respuesta:
                    cuerpo = respuesta.read().decode("utf-8")
                    link_header = respuesta.headers.get("Link")
                    json_data = json.loads(cuerpo) if cuerpo else {}
                    return json_data, link_header
            except urllib.error.HTTPError as e:
                status = e.code
                error_msg = e.read().decode("utf-8", errors="ignore")
                try:
                    error_json = json.loads(error_msg)
                    mensaje_gh = error_json.get("message", error_msg)
                except (json.JSONDecodeError, TypeError, AttributeError):
                    mensaje_gh = error_msg

                if 500 <= status < 600:
                    if intento < intentos - 1:
                        time.sleep(2**intento)
                        continue
                    raise RuntimeError(
                        f"Error de servidor {status} tras {intentos} intentos: {mensaje_gh}"
                    ) from e
                elif 400 <= status < 500:
                    raise RuntimeError(
                        f"Error de cliente {status}: {mensaje_gh}"
                    ) from e
                else:
                    raise RuntimeError(
                        f"Error HTTP {status}: {mensaje_gh}"
                    ) from e
            except urllib.error.URLError as e:
                if intento < intentos - 1:
                    time.sleep(2**intento)
                    continue
                raise RuntimeError(f"Error de red: {e.reason}") from e

        raise RuntimeError("Se agotaron los reintentos para la petición.")

    def rest(
        self, ruta: str, params: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Realiza una petición REST a la API de GitHub.

        Si la respuesta es una lista, sigue automáticamente el encabezado
        Link rel="next" y concatena todas las páginas.

        Args:
            ruta (str): Ruta del endpoint (ej. '/repos/owner/repo/issues').
            params (dict | None): Parámetros opcionales de la URL.

        Returns:
            Any: Datos JSON de la respuesta (diccionario o lista combinada).
        """
        url = f"{self.base_url}{ruta}"
        if params:
            separador = "&" if "?" in url else "?"
            url = f"{url}{separador}{urllib.parse.urlencode(params)}"

        resultado_total: Any = None

        while url:
            datos, link_header = self._hacer_peticion(url)

            if resultado_total is None:
                if isinstance(datos, list):
                    resultado_total = list(datos)
                else:
                    resultado_total = datos
                    break
            else:
                if isinstance(datos, list) and isinstance(resultado_total, list):
                    resultado_total.extend(datos)

            siguiente_url = None
            if link_header:
                partes = link_header.split(",")
                for parte in partes:
                    if 'rel="next"' in parte:
                        inicio = parte.find("<")
                        fin = parte.find(">")
                        if inicio != -1 and fin != -1:
                            siguiente_url = parte[inicio + 1 : fin]
                            break
            url = siguiente_url

        return resultado_total

    def graphql(
        self, consulta: str, variables: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Ejecuta una consulta GraphQL en la API de GitHub.

        Args:
            consulta (str): Cadena de la consulta GraphQL.
            variables (dict): Diccionario de variables para la consulta.

        Returns:
            dict: Contenido del campo 'data' de la respuesta.

        Raises:
            RuntimeError: Si la API de GitHub devuelve errores en la ejecución.
        """
        url = f"{self.base_url}/graphql"
        payload: Dict[str, Any] = {"query": consulta}
        if variables:
            payload["variables"] = variables

        data_bytes = json.dumps(payload).encode("utf-8")
        datos_json, _ = self._hacer_peticion(url, data=data_bytes, metodo="POST")

        if isinstance(datos_json, dict) and "errors" in datos_json:
            raise RuntimeError(
                f"Errores en la consulta GraphQL: {datos_json['errors']}"
            )

        return datos_json.get("data", {})
dev
