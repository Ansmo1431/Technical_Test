"""
Automatización de Pruebas API REST
==================================

Este módulo contiene todas las pruebas de automatización API optimizadas
siguiendo principios KISS (Keep It Simple, Stupid) y mejores prácticas
de testing de APIs REST.

APIs incluidas:
- JSONPlaceholder: Tests CRUD completos con validación de esquemas
- ReqRes: Tests de usuarios, autenticación y rate limiting

Optimizaciones implementadas:
- Session HTTP reutilizable con connection pooling
- Validación automática de esquemas JSON
- Retry logic con backoff exponencial
- Timeouts optimizados para performance
- Manejo robusto de errores HTTP
"""

import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from jsonschema import validate, ValidationError
from config import (
    API_ENDPOINTS,
    DEFAULT_HEADERS,
    REQRES_HEADERS, 
    HTTP_TIMEOUTS,
    RATE_LIMIT_CONFIG,
    JSONPLACEHOLDER_POST_SCHEMA,
    REQRES_USER_SCHEMA,
    VALID_POST_PAYLOAD,
    VALID_USER_PAYLOAD,
    VALID_AUTH_PAYLOAD,
    INVALID_PAYLOADS
)

# =============================================================================
# CLASE SINGLETON PARA SESSION HTTP (OPTIMIZACIÓN DE RENDIMIENTO)
# =============================================================================

class HTTPSessionManager:
    """
    Gestor singleton de sesiones HTTP para optimizar rendimiento.
    Mantiene connection pooling y reutiliza conexiones TCP.
    """
    _instance = None
    _sessions = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(HTTPSessionManager, cls).__new__(cls)
            cls._instance.sessions = {}
        return cls._instance

    
    def get_session(self, api_name="default", headers=None):
        """
        Retorna una sesión HTTP optimizada para el API especificado.
        
        Args:
            api_name: Nombre del API ("jsonplaceholder", "reqres", "default")
            headers: Headers personalizados (opcional)
            
        Returns:
            requests.Session: Sesión configurada y optimizada
        """
        if api_name not in self._sessions:
            self._sessions[api_name] = self._create_session(headers)
        return self._sessions[api_name]
    
    def _create_session(self, headers=None):
        """
        Crea una sesión HTTP optimizada con retry logic y timeouts.
        
        Args:
            headers: Headers personalizados
            
        Returns:
            requests.Session: Sesión configurada
        """
        session = requests.Session()
        
        # Configurar headers por defecto
        session.headers.update(headers or DEFAULT_HEADERS)
        
        # Configurar retry strategy para robustez
        retry_strategy = Retry(
            total=RATE_LIMIT_CONFIG["retry_attempts"],
            backoff_factor=RATE_LIMIT_CONFIG["backoff_factor"],
            status_forcelist=[429, 500, 502, 503, 504],  # Códigos a reintentar
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE"]
        )
        
        # Aplicar adapter con retry strategy
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=10)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session
    
    def close_all_sessions(self):
        """
        Cierra todas las sesiones y libera recursos.
        """
        for session_name, session in self._sessions.items():
            try:
                session.close()
                print(f"EXITOSO: Sesión {session_name} cerrada correctamente")
            except Exception as e:
                print(f"ADVERTENCIA: Error cerrando sesión {session_name}: {e}")
        
        self._sessions.clear()

# =============================================================================
# UTILIDADES COMUNES PARA APIS
# =============================================================================

def make_api_request(method, url, session=None, **kwargs):
    """
    Realiza una petición HTTP optimizada con manejo de errores.
    
    Args:
        method: Método HTTP (GET, POST, PUT, DELETE)
        url: URL completa del endpoint
        session: Sesión HTTP a utilizar (opcional)
        **kwargs: Argumentos adicionales para requests
        
    Returns:
        requests.Response: Respuesta HTTP
    """
    session = session or HTTPSessionManager().get_session()
    
    # Aplicar timeouts por defecto si no se especifican
    if 'timeout' not in kwargs:
        kwargs['timeout'] = (HTTP_TIMEOUTS["connect"], HTTP_TIMEOUTS["read"])
    
    try:
        response = session.request(method, url, **kwargs)
        
        # Log para debugging (opcional)
        print(f"REQUEST: {method} {url} -> {response.status_code}")
        
        return response
        
    except requests.exceptions.RequestException as e:
        print(f"ERROR: Error en petición {method} {url}: {str(e)}")
        raise

def validate_json_schema(data, schema, description=""):
    """
    Valida datos JSON contra un esquema específico.
    
    Args:
        data: Datos JSON a validar
        schema: Esquema JSON Schema
        description: Descripción para el reporte de errores
        
    Raises:
        ValidationError: Si la validación falla
    """
    try:
        validate(instance=data, schema=schema)
        print(f"EXITOSO: Esquema válido: {description}")
    except ValidationError as e:
        print(f"ERROR: Esquema inválido {description}: {e.message}")
        raise

def extract_ids_from_response(response_data, id_field="id"):
    """
    Extrae los IDs de una respuesta JSON de forma optimizada.
    
    Args:
        response_data: Lista de objetos JSON
        id_field: Campo que contiene el ID (por defecto "id")
        
    Returns:
        set: Conjunto de IDs únicos
    """
    return {item[id_field] for item in response_data if id_field in item}

def assert_status_code_in_range(response, expected_codes, description=""):
    """
    Valida que el código de estado esté dentro del rango esperado.
    
    Args:
        response: Objeto Response de requests
        expected_codes: Lista de códigos esperados
        description: Descripción para el reporte
    """
    assert response.status_code in expected_codes, (
        f"{description} - Esperado: {expected_codes}, "
        f"Recibido: {response.status_code}, "
        f"Respuesta: {response.text[:200]}"
    )

# =============================================================================
# TESTS DE JSONPLACEHOLDER API
# =============================================================================

def test_jsonplaceholder_api():
    """
    Prueba completa de JSONPlaceholder API: CRUD, validaciones y casos negativos.
    Incluye validación de esquemas y relaciones entre entidades.
    """
    print("Iniciando pruebas de JSONPlaceholder API...")
    
    session_manager = HTTPSessionManager()
    session = session_manager.get_session("jsonplaceholder")
    
    try:
        # Obtener datos de posts, comments y users
        posts_data = _get_jsonplaceholder_data(session, "posts")
        comments_data = _get_jsonplaceholder_data(session, "comments")
        users_data = _get_jsonplaceholder_data(session, "users")
        
        # Ejecutar flujo CRUD completo
        _test_jsonplaceholder_crud(session, posts_data)
        
        # Validar esquemas de datos
        _validate_jsonplaceholder_schemas(posts_data)
        
        # Probar relaciones entre entidades
        _test_jsonplaceholder_relationships(posts_data, comments_data, users_data)
        
        # Casos negativos y edge cases
        _test_jsonplaceholder_negative_cases(session)
        
        print("EXITOSO: Pruebas de JSONPlaceholder API completadas")
        
    except Exception as e:
        print(f"ERROR: Error en pruebas de JSONPlaceholder API: {str(e)}")
        raise

def _get_jsonplaceholder_data(session, endpoint, limit=10):
    """
    Obtiene datos de un endpoint de JSONPlaceholder con límite para optimizar.
    
    Args:
        session: Sesión HTTP
        endpoint: Endpoint a consultar ("posts", "comments", "users")
        limit: Límite de registros (para optimizar tests)
        
    Returns:
        list: Datos JSON limitados
    """
    base_url = API_ENDPOINTS["jsonplaceholder"]["base"]
    endpoint_url = API_ENDPOINTS["jsonplaceholder"][endpoint]
    url = f"{base_url}{endpoint_url}"
    
    response = make_api_request("GET", url, session)
    assert_status_code_in_range(response, [200], f"GET {endpoint}")
    
    data = response.json()
    
    # Limitar datos para optimizar rendimiento en tests
    return data[:limit]

def _test_jsonplaceholder_crud(session, posts_data):
    """
    Prueba las operaciones CRUD en JSONPlaceholder API.
    
    Args:
        session: Sesión HTTP
        posts_data: Datos de posts para validar READ
    """
    base_url = API_ENDPOINTS["jsonplaceholder"]["base"]
    posts_url = f"{base_url}{API_ENDPOINTS['jsonplaceholder']['posts']}"
    
    # READ - Verificar estructura de datos obtenidos
    assert all(
        field in post for post in posts_data 
        for field in ["userId", "id", "title", "body"]
    ), "Datos de posts no tienen la estructura esperada"
    
    # CREATE - Crear nuevo post
    response = make_api_request(
        "POST", 
        posts_url, 
        session, 
        json=VALID_POST_PAYLOAD
    )
    assert_status_code_in_range(response, [200, 201], "CREATE post")
    
    created_post = response.json()
    assert "id" in created_post, "Post creado no tiene ID"
    created_id = created_post["id"]
    
    # UPDATE - Actualizar post existente  
    update_payload = {
        "id": 1,
        "title": "Título actualizado por QA",
        "body": "Contenido modificado en tests",
        "userId": 1
    }
    
    response = make_api_request(
        "PUT",
        f"{posts_url}/1",
        session,
        json=update_payload
    )
    assert_status_code_in_range(response, [200], "UPDATE post")
    
    # DELETE - Eliminar post creado
    response = make_api_request(
        "DELETE",
        f"{posts_url}/{created_id}",
        session
    )
    assert_status_code_in_range(response, [200, 204], "DELETE post")

def _validate_jsonplaceholder_schemas(posts_data):
    """
    Valida esquemas JSON de los datos obtenidos.
    
    Args:
        posts_data: Datos de posts a validar
    """
    for i, post in enumerate(posts_data):
        validate_json_schema(
            post, 
            JSONPLACEHOLDER_POST_SCHEMA, 
            f"Post #{i+1}"
        )

def _test_jsonplaceholder_relationships(posts_data, comments_data, users_data):
    """
    Prueba las relaciones entre posts, comments y users.
    
    Args:
        posts_data: Datos de posts
        comments_data: Datos de comentarios  
        users_data: Datos de usuarios
    """
    # Extraer IDs para comparar relaciones
    post_ids = extract_ids_from_response(posts_data)
    comment_post_ids = extract_ids_from_response(comments_data, "postId")
    user_ids = extract_ids_from_response(users_data)
    post_user_ids = extract_ids_from_response(posts_data, "userId")
    
    # Verificar que los comments referencian posts existentes
    common_post_ids = post_ids & comment_post_ids
    assert len(common_post_ids) > 0, "No hay relación entre posts y comments"
    
    # Verificar que los posts referencian usuarios existentes
    common_user_ids = user_ids & post_user_ids
    assert len(common_user_ids) > 0, "No hay relación entre users y posts"
    
    print(f"EXITOSO: Relaciones validadas: {len(common_post_ids)} posts con comments, {len(common_user_ids)} posts con users")

def _test_jsonplaceholder_negative_cases(session):
    """
    Prueba casos negativos y edge cases.
    
    Args:
        session: Sesión HTTP
    """
    base_url = API_ENDPOINTS["jsonplaceholder"]["base"]
    posts_url = f"{base_url}{API_ENDPOINTS['jsonplaceholder']['posts']}"
    
    # GET con ID inexistente
    response = make_api_request("GET", f"{posts_url}/9999", session)
    assert_status_code_in_range(response, [404], "GET post inexistente")
    
    # POST con payload inválido
    response = make_api_request(
        "POST",
        posts_url,
        session,
        json=INVALID_PAYLOADS["post_invalid_types"]
    )
    # JSONPlaceholder es mock, acepta cualquier cosa con 201
    # En API real, esto debería dar 400
    assert_status_code_in_range(response, [200, 201, 400], "POST con payload inválido")
    
    # Método no permitido
    response = make_api_request("PUT", posts_url, session, json=VALID_POST_PAYLOAD)
    assert_status_code_in_range(response, [404, 405], "PUT en colección")

# =============================================================================
# TESTS DE REQRES API
# =============================================================================

def test_reqres_api():
    """
    Prueba completa de ReqRes API: usuarios, autenticación y rate limiting.
    """
    print("Iniciando pruebas de ReqRes API...")
    
    session_manager = HTTPSessionManager()
    session = session_manager.get_session("reqres", REQRES_HEADERS)
    
    try:
        # Probar operaciones CRUD de usuarios
        _test_reqres_users(session)
        
        # Probar autenticación y registro
        _test_reqres_authentication(session)
        
        # Probar rate limiting y robustez
        _test_reqres_rate_limiting(session)
        
        print("EXITOSO: Pruebas de ReqRes API completadas")
        
    except Exception as e:
        print(f"ERROR: Error en pruebas de ReqRes API: {str(e)}")
        raise

def _test_reqres_users(session):
    """
    Prueba operaciones CRUD de usuarios en ReqRes API.
    
    Args:
        session: Sesión HTTP
    """
    base_url = API_ENDPOINTS["reqres"]["base"]
    users_url = f"{base_url}{API_ENDPOINTS['reqres']['users']}"
    users_url2 =f"{base_url}{API_ENDPOINTS['reqres']['users']}?page=2"

    # CREATE - Crear usuario
    response = make_api_request(
        "POST",
        users_url,
        session,
        json=VALID_USER_PAYLOAD
    )
    assert_status_code_in_range(response, [201], "CREATE user")
    
    user_data = response.json()
    assert "id" in user_data, "Usuario creado no tiene ID"
    
    # READ - Obtener lista de usuarios
    response = make_api_request("GET",
                                f"{users_url}",
                                session
                                )
    assert_status_code_in_range(response, [200], "GET users")

    users_response = response.json()
    required_fields = ["page", "per_page", "total", "total_pages", "data"]
    assert all(field in users_response for field in required_fields), "Respuesta de usuarios incompleta"

    # Probar paginación
    response = make_api_request("GET", f"{users_url2}", session)
    assert_status_code_in_range(response, [200], "GET users page 2")
    assert response.status_code == 200
    page2_data = response.json()
    assert "page" in page2_data, "Error en el Json"
    assert page2_data["page"] == 2, "Paginación no funcionó correctamente"

    # Validar esquema de usuarios
    for user in page2_data["data"]:
        validate_json_schema(user, REQRES_USER_SCHEMA, f"Usuario {user.get('id')}")
    
    # UPDATE - Actualizar usuario
    update_payload = {
        "name": "QA Tester Updated",
        "job": "Senior QA Engineer"
    }
    
    response = make_api_request(
        "PUT",
        f"{users_url}/2",
        session,
        json=update_payload
    )
    assert_status_code_in_range(response, [200], "UPDATE user")
    
    # DELETE - Eliminar usuario
    response = make_api_request("DELETE", f"{users_url}/2", session)
    assert_status_code_in_range(response, [204], "DELETE user")

def _test_reqres_authentication(session):
    """
    Prueba flujos de autenticación y registro.
    
    Args:
        session: Sesión HTTP
    """
    base_url = API_ENDPOINTS["reqres"]["base"]
    login_url = f"{base_url}{API_ENDPOINTS['reqres']['login']}"
    register_url = f"{base_url}{API_ENDPOINTS['reqres']['register']}"
    
    # LOGIN EXITOSO
    response = make_api_request(
        "POST",
        login_url,
        session,
        json=VALID_AUTH_PAYLOAD
    )
    assert_status_code_in_range(response, [200], "Login exitoso")
    
    login_data = response.json()
    assert "token" in login_data, "Login exitoso no devolvió token"
    
    # LOGIN FALLIDO - falta password
    response = make_api_request(
        "POST",
        login_url,
        session,
        json=INVALID_PAYLOADS["auth_missing_password"]
    )
    assert_status_code_in_range(response, [400], "Login fallido")
    
    error_data = response.json()
    assert "error" in error_data, "Login fallido no devolvió error"
    
    # REGISTRO EXITOSO
    register_payload = {
        "email": "eve.holt@reqres.in",
        "password": "pistol"
    }
    
    response = make_api_request(
        "POST",
        register_url,
        session,
        json=register_payload
    )
    assert_status_code_in_range(response, [200], "Registro exitoso")
    
    register_data = response.json()
    required_fields = ["id", "token"]
    assert all(field in register_data for field in required_fields), "Registro exitoso incompleto"
    
    # REGISTRO FALLIDO - falta password
    response = make_api_request(
        "POST",
        register_url,
        session,
        json=INVALID_PAYLOADS["auth_missing_password"]
    )
    assert_status_code_in_range(response, [400], "Registro fallido")
    
    error_data = response.json()
    assert "error" in error_data, "Registro fallido no devolvió error"

def _test_reqres_rate_limiting(session):
    """
    Prueba el manejo de rate limiting y robustez de la API.
    
    Args:
        session: Sesión HTTP
    """
    base_url = API_ENDPOINTS["reqres"]["base"]
    test_url = f"{base_url}{API_ENDPOINTS['reqres']['users']}/2"
    
    print("Probando robustez con múltiples requests...")
    
    successful_requests = 0
    rate_limited_requests = 0
    
    # Realizar múltiples requests para probar rate limiting
    for i in range(RATE_LIMIT_CONFIG["max_requests"]):
        try:
            response = make_api_request("GET", test_url, session)
            
            if response.status_code == 429:  # Rate limited
                rate_limited_requests += 1
                
                # Respetar el header Retry-After si está presente
                retry_after = response.headers.get("Retry-After")
                wait_time = int(retry_after) if retry_after else 5
                
                print(f"Rate limit detectado, esperando {wait_time}s...")
                time.sleep(wait_time)
                continue
                
            elif response.status_code == 200:
                successful_requests += 1
            
            # Control de ritmo para ser respetuosos con la API
            time.sleep(RATE_LIMIT_CONFIG["delay_between_requests"])
            
        except Exception as e:
            print(f"ADVERTENCIA: Error en request #{i+1}: {str(e)}")
            continue
    
    print(f"Rate limiting test - Exitosos: {successful_requests}, Rate limited: {rate_limited_requests}")

# =============================================================================
# FUNCIÓN PRINCIPAL PARA EJECUTAR TODOS LOS TESTS API
# =============================================================================

def run_all_api_tests():
    """
    Ejecuta todos los tests de automatización API de forma secuencial.
    Maneja errores globalmente y asegura limpieza de recursos.
    """
    print("Iniciando batería completa de pruebas API...")
    print("=" * 60)
    
    session_manager = HTTPSessionManager()
    
    try:
        # Lista de tests a ejecutar
        test_functions = [
            test_jsonplaceholder_api,
            test_reqres_api
        ]
        
        successful_tests = 0
        failed_tests = 0
        
        for test_func in test_functions:
            try:
                test_func()
                successful_tests += 1
            except Exception as e:
                print(f"ERROR: Falló {test_func.__name__}: {str(e)}")
                failed_tests += 1
                continue
        
        # Reporte final
        print("=" * 60)
        print("REPORTE FINAL DE PRUEBAS API:")
        print(f"EXITOSO: Tests exitosos: {successful_tests}")
        print(f"ERROR: Tests fallidos: {failed_tests}")
        print(f"Tasa de éxito: {(successful_tests/(successful_tests+failed_tests))*100:.1f}%")
        
    except Exception as e:
        print(f"ERROR CRÍTICO: Error crítico en la ejecución: {str(e)}")
    
    finally:
        # Asegurar limpieza de recursos
        print("Limpiando recursos de red...")
        session_manager.close_all_sessions()
        print("EXITOSO: Sesiones HTTP cerradas correctamente")

# =============================================================================
# EJECUCIÓN DIRECTA DEL MÓDULO
# =============================================================================

if __name__ == "__main__":
    run_all_api_tests()
