# Automatización QA - Prueba Técnica

**Proyecto de automatización para prueba técnica de Dev QA Tester Junior**

Este proyecto implementa una solución completa de automatización de pruebas siguiendo principios **KISS** (Keep It Simple, Stupid) con arquitectura plana y optimizada para rendimiento.

## Descripción del Proyecto

### Objetivo
Demostrar competencias en automatización de pruebas web y API con herramientas modernas, implementando mejores prácticas de QA, validación funcional y pruebas de performance orientadas a la optimización de tiempos de respuesta, estabilidad bajo carga, y análisis de métricas clave como percentiles, throughput y tasa de error.

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

#### Pruebas de Performance (API)
- **JSONPlaceholder API**: 100 solicitudes concurrentes a /posts durante 2 minutos
- **ReqRes API**: 50 usuarios simultáneos en /api/users
- **Swagger Petstore API**: 200 solicitudes por minuto en endpoints de /pet
- **Casos Negativos**: Validación de errores 4xx/5xx bajo carga
- **Puntos de Quiebre**: Identificación de límites de rendimiento y estabilidad

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
### Estructura Archivos JMeter
```
├── jsonplaceholder/         # Carpeta con las pruebas del servicio JSONPlaceholder
│ ├── jsonplaceholder.jmx    # Archivo principal de configuración JMeter para este servicio
│ ├── resultadoF.jtl         # Resultado final con 100 usuarios concurrentes durante 2 minutos
│ ├── resultado800.jtl       # Resultado de prueba con 800 usuarios concurrentes
│ ├── resultado1400.jtl      # Resultado de prueba con 1400 usuarios concurrentes
│ ├── resultado1500.jtl      # Resultado con 1500 usuarios (acercándose al punto de quiebre)
│ └── ...                    # Otros resultados con distintas cargas de usuarios
│
├── reqres/                  # Carpeta con las pruebas del servicio ReqRes
│ ├── reqres.jmx             # Plan de prueba principal para ReqRes API
│ ├── resultadoF.jtl         # Resultado final de la ejecución con carga máxima (100 usuarios)
│ ├── resultado50.jtl        # Resultado parcial con carga reducida
│ ├── resultado80.jtl        # Resultado parcial con más carga
│ └── ...                    # Archivos adicionales con pruebas incrementales
│
├── swagger/                 # Carpeta con las pruebas del servicio Swagger Petstore
│ ├── swagger.jmx            # Archivo principal de configuración para la API Swagger
│ ├── resultadoF.jtl         # Resultado de la prueba principal (100 usuarios)
│ ├── resultado50.jtl        # Resultados intermedios con 50 usuarios
│ ├── resultado200.jtl       # Resultados intermedios con 200 usuarios
│ └── ...                    # Archivos adicionales para diferentes niveles de carga
│
├── METRICAS_TESTP.CSV       # Archivo consolidado con todas las métricas de rendimiento
│ # (tiempos de respuesta, errores, throughput, punto de quiebre)              # Documentación
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
- **Java 8 o superior**
- **Apache JMeter**
- **Maven** (si se desea ejecutar pruebas automatizadas)

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

### **Instalación JMeter**: Instalación en Windows / Linux / macOS

-**Descarga la última versión desde**: https://jmeter.apache.org/download_jmeter.cgi

-**Descomprime el archivo ZIP/TGZ**:
```bash
tar -xvzf apache-jmeter-<versión>.tgz
cd apache-jmeter-<versión>
```

-**Verifica que JMeter funcione**:
```bash
./bin/jmeter -v
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
### Ejecución JMeter

- Abre **Apache JMeter**
- Carga el archivo `.jmx` correspondiente al servicio que desees probar.
- Ajusta los parámetros de usuarios y duración si es necesario.
- Ejecuta la prueba.
- Los resultados se almacenan automáticamente en archivos `.jtl` dentro de la carpeta correspondiente.

## Ejecución con Docker

### Instalación de Docker
Instalar Docker Desktop desde [docker.com](https://www.docker.com/products/docker-desktop)

### Lanzador Rápido

#### Linux/macOS:
```bash
# Ejecutar todas las pruebas
./run-docker.sh run

# Solo pruebas web  
./run-docker.sh web

# Solo pruebas API
./run-docker.sh api

# Modo debug interactivo
./run-docker.sh debug
```

#### Windows:
```cmd
# Ejecutar todas las pruebas
run-docker.bat run

# Solo pruebas web
run-docker.bat web  

# Solo pruebas API
run-docker.bat api

# Modo debug interactivo
run-docker.bat debug
```

### Comandos Docker Avanzados

#### Construcción Manual:
```bash
# Construir imagen
docker build -t qa-automation:latest .

# Ejecutar contenedor
docker run --rm \
  -v $(pwd)/downloads:/app/downloads \
  --shm-size=2g \
  qa-automation:latest
```

#### Docker Compose:
```bash
# Ejecutar con compose
docker-compose up qa-automation

# Con servidor de reportes
docker-compose --profile reports up
```

### Opciones del Lanzador Docker

| Comando | Descripción |
|---------|-------------|
| `build` | Construir la imagen Docker |
| `run` | Ejecutar todas las pruebas |
| `web` | Ejecutar solo pruebas web |
| `api` | Ejecutar solo pruebas API |
| `debug` | Modo debug interactivo |
| `shell` | Abrir shell en contenedor |
| `logs` | Mostrar logs de ejecución |
| `status` | Estado de contenedores |
| `clean` | Limpiar recursos Docker |
| `help` | Mostrar ayuda |

### Ventajas de Docker

#### Consistencia de Entorno
- **Mismo entorno** en desarrollo, CI/CD y producción
- **Chrome y ChromeDriver** preinstalados y configurados
- **Dependencias fijas** sin conflictos de versiones

#### Facilidad de Uso  
- **Un solo comando** para ejecutar todas las pruebas
- **No requiere** instalación local de Chrome/ChromeDriver
- **Funciona en cualquier** sistema operativo

#### Aislamiento y Seguridad
- **Contenedor aislado** no afecta el sistema host
- **Recursos limitados** para evitar consumo excesivo
- **Limpieza automática** de archivos temporales

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
- **Java 8 o superior**
- **Apache JMeter**

---

## Soporte

Para cualquier consulta sobre este proyecto:
- Revisar salida detallada en consola
- Verificar sección "Resolución de Problemas"
- Consultar comentarios en el código fuente

---
