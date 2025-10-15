"""
Configuración centralizada para los tests de automatización
================================================

Este archivo contiene todas las configuraciones necesarias para ejecutar
los tests de automatización web y API de forma optimizada.
"""

# =============================================================================
# CONFIGURACIÓN WEB AUTOMATION (SELENIUM)
# =============================================================================

# URLs de testing web
WEB_BASE_URL = "https://the-internet.herokuapp.com/"

# Credenciales de prueba
LOGIN_CREDENTIALS = {
    "valid": {
        "username": "tomsmith", 
        "password": "SuperSecretPassword!"
    },
    "invalid": {
        "username": "wronguser",
        "password": "wrongpass"
    }
}

# Timeouts para optimizar rendimiento
SELENIUM_TIMEOUTS = {
    "implicit_wait": 10,        # Espera implícita del driver
    "explicit_wait": 15,        # Esperas explícitas
    "page_load": 30,           # Carga de página
    "script": 30               # Ejecución de JavaScript
}

# Configuración del navegador
BROWSER_CONFIG = {
    "headless": False,          # Cambiar a True para CI/CD o Docker
    "window_size": (1920, 1080),
    "implicit_wait": SELENIUM_TIMEOUTS["implicit_wait"]
}

# Configuración específica para Docker (se detecta automáticamente)
import os
if os.getenv('QA_ENV') == 'docker' or os.getenv('HEADLESS_MODE') == 'true':
    BROWSER_CONFIG.update({
        "headless": True,       # Forzar modo headless en Docker
        "window_size": (1920, 1080),
        "docker_mode": True
    })
    # Extender timeouts para Docker (puede ser más lento)
    SELENIUM_TIMEOUTS.update({
        "implicit_wait": 15,
        "explicit_wait": 20,
        "page_load": 45,
        "script": 45
    })

# =============================================================================
# CONFIGURACIÓN API AUTOMATION
# =============================================================================

# URLs de APIs de prueba
API_ENDPOINTS = {
    "jsonplaceholder": {
        "base": "https://jsonplaceholder.typicode.com",
        "posts": "/posts",
        "comments": "/comments", 
        "users": "/users"
    },
    "reqres": {
        "base": "https://reqres.in/api",
        "users": "/users",
        "login": "/login",
        "register": "/register"
    }
}

# Headers comunes para requests HTTP
DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "User-Agent": "QA-Automation-Tests/1.0"
}

# Headers específicos para ReqRes API
REQRES_HEADERS = {
    **DEFAULT_HEADERS,
    "Accept": "application/json",
    "Host": "reqres.in",
    "x-api-key": "reqres-free-v1",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive"
}

# Timeouts para requests HTTP (optimización de rendimiento)
HTTP_TIMEOUTS = {
    "connect": 5,              # Tiempo de conexión
    "read": 30                 # Tiempo de lectura
}

# Configuración para rate limiting
RATE_LIMIT_CONFIG = {
    "max_requests": 100,       # Máximo de requests por test
    "delay_between_requests": 0.1,  # Delay mínimo entre requests
    "retry_attempts": 3,       # Intentos de reintento
    "backoff_factor": 2        # Factor de backoff exponencial
}

# =============================================================================
# ESQUEMAS JSON PARA VALIDACIÓN
# =============================================================================

# Schema para validar posts de JSONPlaceholder
JSONPLACEHOLDER_POST_SCHEMA = {
    "type": "object",
    "properties": {
        "userId": {"type": "integer", "minimum": 1},
        "id": {"type": "integer", "minimum": 1},
        "title": {"type": "string", "minLength": 1},
        "body": {"type": "string", "minLength": 1}
    },
    "required": ["userId", "id", "title", "body"],
    "additionalProperties": False
}

# Schema para validar usuarios de ReqRes
REQRES_USER_SCHEMA = {
    "type": "object", 
    "properties": {
        "id": {"type": "integer"},
        "email": {"type": "string", "format": "email"},
        "first_name": {"type": "string"},
        "last_name": {"type": "string"},
        "avatar": {"type": "string", "format": "uri"}
    },
    "required": ["id", "email", "first_name", "last_name"],
    "additionalProperties": True
}

# =============================================================================
# DATOS DE PRUEBA PARA TESTS
# =============================================================================

# Payloads válidos para crear posts
VALID_POST_PAYLOAD = {
    "userId": 1,
    "title": "Test Post - QA Automation",
    "body": "Este es un post de prueba creado por automatización QA"
}

# Payloads válidos para usuarios
VALID_USER_PAYLOAD = {
    "name": "QA Tester",
    "job": "Quality Assurance Engineer"
}

# Payloads para autenticación exitosa
VALID_AUTH_PAYLOAD = {
    "email": "eve.holt@reqres.in",
    "password": "cityslicka"
}

# Payloads inválidos para tests negativos
INVALID_PAYLOADS = {
    "post_invalid_types": {
        "userId": "string_instead_of_int",
        "title": 12345,  # número en lugar de string
        "body": None     # null en lugar de string
    },
    "auth_missing_password": {
        "email": "peter@klaven"  # falta password
    },
    "auth_missing_email": {
        "password": "password123"  # falta email
    }
}

# =============================================================================
# CONFIGURACIÓN DE LOGGING Y REPORTES
# =============================================================================

# Configuración de logs para debugging
LOGGING_CONFIG = {
    "level": "INFO",           # DEBUG, INFO, WARNING, ERROR
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "automation_tests.log"
}
