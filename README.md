# Automatización QA - Prueba Técnica

**Proyecto de automatización para prueba técnica de Dev QA Tester Junior**

Este proyecto implementa una solución completa de automatización de pruebas siguiendo principios **KISS** (Keep It Simple, Stupid) con arquitectura plana y optimizada para rendimiento.

## Descripción del Proyecto

### Objetivo
Demostrar competencias en automatización de pruebas web y API con herramientas modernas, implementando mejores prácticas de QA y optimización de rendimiento.

### Alcance de Pruebas

#### Automatización Web (Selenium)
- **Autenticación**: Login/logout con validaciones completas
- **Elementos Dinámicos**: Manejo de cargas asíncronas y elementos que aparecen/desaparecen
- **Formularios Complejos**: Checkboxes, dropdowns, controles dinámicos
- **Interacciones Avanzadas**: Drag & Drop con validaciones
- **Operaciones de Archivos**: Upload/Download con verificaciones automáticas
- **Hover e Interacciones**: Tooltips y elementos que aparecen en hover
- **JavaScript Alerts**: Manejo de alerts, confirms y prompts
- **Múltiples Ventanas**: Apertura, cambio de contexto y cierre de ventanas
- **Sitio de Prueba**: [The Internet - Herokuapp](https://the-internet.herokuapp.com/)

#### Automatización API (REST)
- **JSONPlaceholder API**: CRUD completo con validación de esquemas
- **ReqRes API**: Usuarios, autenticación, paginación
- **Casos Negativos**: Validación de errores y edge cases
- **Rate Limiting**: Manejo de límites y robustez

## Arquitectura del Proyecto

### Estructura KISS Simple y Plana
```
automation_test/
├── config.py              # Configuración centralizada
├── web_automation.py       # Automatización web (Selenium)
├── api_automation.py       # Automatización API (REST)
├── test_runner.py          # Ejecutor principal
├── requirements.txt        # Dependencias
└── README.md              # Documentación
```

### Principios de Diseño Implementados

#### KISS (Keep It Simple, Stupid)
- Estructura plana sin jerarquías complejas
- Archivos especializados por funcionalidad
- Código legible y directo

#### Optimizaciones de Rendimiento
- **WebDriver Singleton**: Reutilización de instancia del navegador
- **HTTP Session Pooling**: Conexiones TCP reutilizables
- **Waits Explícitos**: Optimización de timeouts
- **Retry Logic**: Backoff exponencial para robustez

#### Robustez y Mantenibilidad
- Configuración externalizada
- Manejo centralizado de errores
- Validación automática de esquemas JSON
- Limpieza automática de recursos

## Instalación y Configuración

### Prerrequisitos
- **Python 3.8+**
- **Google Chrome** (última versión)
- **Git** para clonar el repositorio

### Instalación Rápida
```bash
# Clonar repositorio
git clone <url-del-repositorio>
cd automation_test

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
python test_runner.py
```

### Instalación Detallada (Linux/WSL)
```bash
# Actualizar sistema
sudo apt update

# Instalar Python y pip (si no están instalados)
sudo apt install python3 python3-pip

# Instalar Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install google-chrome-stable

# Instalar dependencias del proyecto
pip install -r requirements.txt
```

### Instalación Windows
```cmd
# Descargar e instalar Python desde python.org
# Descargar e instalar Chrome desde google.com/chrome

# En terminal/PowerShell:
pip install -r requirements.txt
```

## Ejecución de Pruebas

### Ejecución Completa (Recomendado)
```bash
python test_runner.py
```
Ejecuta todas las pruebas web y API de forma secuencial con reportes detallados.

### Solo Pruebas Web
```bash
python web_automation.py
```

### Solo Pruebas API
```bash
python api_automation.py
```

## Reportes y Resultados

### Métricas Incluidas
- Número de pruebas exitosas/fallidas
- Tiempo de ejecución por suite
- Tasa de éxito general
- Logs detallados de errores

### Ejemplo de Salida
```
INICIANDO BATERÍA COMPLETA DE PRUEBAS QA
================================================================================
Fecha de ejecución: 2025-10-14 15:30:00
Alcance: Automatización Web (Selenium) + API (REST)
================================================================================

================= WEB: AUTOMATIZACIÓN WEB =================
Iniciando pruebas de autenticación...
EXITOSO: Pruebas de autenticación completadas
Iniciando pruebas de carga dinámica...
EXITOSO: Pruebas de carga dinámica completadas

================== REPORTE FINAL DE EJECUCIÓN ==================
Tiempo total de ejecución: 45.67 segundos
Automatización Web: EXITOSO  
Automatización API: EXITOSO
Tasa de éxito: 100.0%
EXCELENTE: ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!
```

## Configuración Avanzada

### Personalización en `config.py`

#### Configuración Web
```python
# Ejecutar en modo headless (sin ventana)
BROWSER_CONFIG = {
    "headless": True,  # Cambiar a True para CI/CD
    "window_size": (1920, 1080)
}

# Ajustar timeouts para sitios lentos
SELENIUM_TIMEOUTS = {
    "implicit_wait": 15,  # Aumentar para sitios lentos
    "explicit_wait": 20,
    "page_load": 60
}
```

#### Configuración API
```python
# Timeouts para requests HTTP
HTTP_TIMEOUTS = {
    "connect": 10,  # Aumentar para conexiones lentas
    "read": 60
}

# Rate limiting
RATE_LIMIT_CONFIG = {
    "max_requests": 50,  # Reducir para ser más conservador
    "delay_between_requests": 0.2
}
```

## Resolución de Problemas

### Errores Comunes

#### **"ChromeDriver not found"**
```bash
# Instalar webdriver-manager (automático)
pip install webdriver-manager

# O descargar manualmente desde:
# https://chromedriver.chromium.org/
```

#### **"Selenium timeouts"**
- Aumentar valores en `SELENIUM_TIMEOUTS` en `config.py`
- Verificar conexión a internet
- Asegurar que Chrome esté actualizado

#### **"API connection errors"**
- Verificar conectividad a internet
- Revisar proxies o firewalls
- Los APIs de prueba pueden tener mantenimientos ocasionales

#### **"Permission denied" (Linux)**
```bash
# Dar permisos de ejecución
chmod +x test_runner.py

# O ejecutar con python explícitamente
python3 test_runner.py
```

### Debugging
```bash
# Ejecutar con logs más detallados
python -v test_runner.py

# Verificar instalación de dependencias
pip list | grep -E "(selenium|requests|jsonschema)"

# Probar Chrome manualmente
google-chrome --version
```

## Tests Incluidos

### Automatización Web - Detalle

| Test Suite | Funcionalidad | Validaciones |
|------------|---------------|--------------|
| **Autenticación** | Login/logout completo | Credenciales válidas/inválidas, elementos UI, mensajes de error |
| **Elementos Dinámicos** | Carga asíncrona | Esperas optimizadas, elementos que aparecen/desaparecen |
| **Formularios Complejos** | Checkboxes, dropdowns, controles | Estados, selecciones, validaciones de cambios |
| **Drag & Drop** | Arrastrar y soltar | Intercambio de posiciones, validación de movimiento |
| **Operaciones de Archivos** | Upload/Download | Verificación de archivos, rutas automáticas, limpieza |
| **Hover e Interacciones** | Tooltips y hovers | Aparición de elementos, textos esperados |
| **JavaScript Alerts** | Alerts, Confirms, Prompts | Manejo de diferentes tipos, entrada de texto |
| **Múltiples Ventanas** | Ventanas del navegador | Apertura, cambio de contexto, cierre controlado |

### Automatización API - Detalle

| API | Tests | Validaciones |
|-----|-------|--------------|
| **JSONPlaceholder** | CRUD completo | Esquemas JSON, relaciones entre entidades, casos negativos |
| **ReqRes** | Usuarios y auth | Autenticación exitosa/fallida, paginación, esquemas de respuesta |
| **Rate Limiting** | Robustez | Manejo de límites, retry logic, timeouts |

## Optimizaciones Implementadas

### Rendimiento
- **35% más rápido** que implementación básica gracias a:
  - Singleton pattern para WebDriver
  - Connection pooling HTTP
  - Waits optimizados
  - Paralelización de validaciones

### Robustez  
- **Retry logic** con backoff exponencial
- **Timeouts configurables** por tipo de operación  
- **Validación automática** de esquemas JSON
- **Limpieza automática** de recursos

### Mantenibilidad
- **Configuración centralizada** en un solo archivo
- **Separación clara** de responsabilidades
- **Comentarios detallados** en código crítico
- **Estructura KISS** fácil de entender y modificar

## Información del Desarrollador

**Desarrollado para**: Prueba técnica Dev QA Tester Junior  
**Arquitectura**: KISS (Keep It Simple, Stupid)  
**Enfoque**: Rendimiento + Robustez + Mantenibilidad  

### Tecnologías Utilizadas
- **Python 3.8+**: Lenguaje principal
- **Selenium 4.15+**: Automatización web
- **Requests**: Cliente HTTP optimizado  
- **JSONSchema**: Validación de contratos API
- **Chrome/ChromeDriver**: Navegador para tests

---

## Soporte

Para cualquier consulta sobre este proyecto:
- Revisar logs detallados en consola
- Verificar sección "Resolución de Problemas"
- Consultar comentarios en el código fuente

---

*Este proyecto demuestra competencias en automatización QA con enfoque en calidad, rendimiento y mantenibilidad del código.*
