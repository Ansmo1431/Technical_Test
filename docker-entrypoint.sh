#!/bin/bash
# ===============================================================================
# DOCKER ENTRYPOINT SCRIPT
# ===============================================================================
# Script de inicialización para el contenedor Docker
# Configura el entorno y ejecuta las pruebas de automatización

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

# ===============================================================================
# CONFIGURACIÓN DEL ENTORNO
# ===============================================================================

log "Iniciando configuración del entorno Docker..."

# Configurar variables de entorno para Chrome en Docker
export CHROME_BIN=/usr/bin/google-chrome
export CHROME_PATH=/usr/bin/google-chrome
export CHROMEDRIVER_PATH=/usr/local/bin/chromedriver

# Configurar display virtual para modo headless
export DISPLAY=:99

# Iniciar Xvfb (X Virtual Framebuffer) para pruebas headless
log "Iniciando display virtual Xvfb..."
Xvfb :99 -screen 0 1920x1080x24 > /dev/null 2>&1 &
XVFB_PID=$!

# Esperar a que Xvfb esté listo
sleep 2

# Verificar que Chrome está disponible
log "Verificando instalación de Google Chrome..."
if command -v google-chrome >/dev/null 2>&1; then
    CHROME_VERSION=$(google-chrome --version)
    log "Chrome encontrado: $CHROME_VERSION"
else
    error "Google Chrome no encontrado"
    exit 1
fi

# Verificar que ChromeDriver está disponible
log "Verificando ChromeDriver..."
if command -v chromedriver >/dev/null 2>&1; then
    CHROMEDRIVER_VERSION=$(chromedriver --version)
    log "ChromeDriver encontrado: $CHROMEDRIVER_VERSION"
else
    error "ChromeDriver no encontrado"
    exit 1
fi

# Verificar dependencias Python
log "Verificando dependencias Python..."
python -c "
import sys
try:
    import selenium
    import requests
    import jsonschema
    print('EXITOSO: Todas las dependencias Python están instaladas')
except ImportError as e:
    print(f'ERROR: Dependencia faltante: {e}')
    sys.exit(1)
"

# Crear directorios necesarios si no existen
mkdir -p /app/downloads

# ===============================================================================
# CONFIGURACIÓN ESPECÍFICA PARA DOCKER
# ===============================================================================

log "Aplicando configuración específica para Docker..."

# Crear archivo de configuración temporal para Docker
cat > /tmp/docker_config_override.py << 'EOF'
"""
Configuración específica para ejecución en Docker
Sobrescribe configuraciones necesarias para el entorno containerizado
"""

# Configuración Chrome para Docker
DOCKER_CHROME_OPTIONS = [
    "--headless",
    "--no-sandbox", 
    "--disable-dev-shm-usage",
    "--disable-gpu",
    "--disable-features=VizDisplayCompositor",
    "--window-size=1920,1080",
    "--remote-debugging-port=9222",
    "--disable-extensions",
    "--disable-plugins",
    "--disable-images",
    "--disable-javascript",
    "--disable-default-apps",
    "--disable-background-timer-throttling",
    "--disable-backgrounding-occluded-windows",
    "--disable-renderer-backgrounding"
]

# Timeouts extendidos para Docker (puede ser más lento)
DOCKER_TIMEOUTS = {
    "implicit_wait": 15,
    "explicit_wait": 20, 
    "page_load": 45,
    "script": 45
}

# Configurar modo headless forzado
DOCKER_BROWSER_CONFIG = {
    "headless": True,
    "window_size": (1920, 1080),
    "implicit_wait": 15
}
EOF

# ===============================================================================
# FUNCIÓN DE LIMPIEZA
# ===============================================================================

cleanup() {
    log "Limpiando recursos antes de salir..."
    
    # Matar proceso Xvfb si existe
    if kill -0 $XVFB_PID 2>/dev/null; then
        kill $XVFB_PID
        log "Proceso Xvfb terminado"
    fi
    
    # Limpiar archivos temporales
    rm -f /tmp/docker_config_override.py
    
    log "Limpieza completada"
}

# Configurar trap para limpieza al salir
trap cleanup EXIT INT TERM

# ===============================================================================
# MANEJO DE ARGUMENTOS Y EJECUCIÓN
# ===============================================================================

log "Configuración completada. Ejecutando comando: $@"

# Si no se proporciona comando, ejecutar el test runner por defecto
if [ $# -eq 0 ]; then
    log "No se proporcionó comando, ejecutando test runner por defecto..."
    exec python test_runner.py
fi

# Casos especiales para diferentes tipos de ejecución
case "$1" in
    "web")
        log "Ejecutando solo pruebas WEB..."
        exec python web_automation.py
        ;;
    "api") 
        log "Ejecutando solo pruebas API..."
        exec python api_automation.py
        ;;
    "test"|"tests")
        log "Ejecutando todas las pruebas..."
        exec python test_runner.py
        ;;
    "bash"|"shell")
        log "Iniciando shell interactivo..."
        exec /bin/bash
        ;;
    "debug")
        log "Iniciando modo debug..."
        log "Información del entorno:"
        echo "Python: $(python --version)"
        echo "Chrome: $(google-chrome --version 2>/dev/null || echo 'No disponible')"
        echo "ChromeDriver: $(chromedriver --version 2>/dev/null || echo 'No disponible')"
        echo "Display: $DISPLAY"
        echo "Directorio actual: $(pwd)"
        echo "Archivos disponibles:"
        ls -la
        exec /bin/bash
        ;;
    *)
        log "Ejecutando comando personalizado: $@"
        exec "$@"
        ;;
esac
