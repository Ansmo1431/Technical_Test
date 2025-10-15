#!/bin/bash
# ===============================================================================
# LANZADOR DOCKER - AUTOMATIZACIÓN QA
# ===============================================================================
# Script de lanzamiento simplificado para ejecutar pruebas con Docker
# Maneja la construcción, ejecución y limpieza automática

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m'

# Variables
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_NAME="qa-automation"
IMAGE_NAME="$PROJECT_NAME:latest"
CONTAINER_NAME="$PROJECT_NAME-container"

# ===============================================================================
# FUNCIONES AUXILIARES
# ===============================================================================

show_banner() {
    echo -e "${BLUE}${BOLD}"
    echo "==============================================================================="
    echo "                    AUTOMATIZACIÓN QA - LANZADOR DOCKER                       "
    echo "==============================================================================="
    echo -e "${NC}"
}

log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

show_usage() {
    echo -e "${BOLD}Uso:${NC} $0 [OPCIÓN] [ARGUMENTOS]"
    echo ""
    echo -e "${BOLD}Opciones disponibles:${NC}"
    echo "  build              Construir la imagen Docker"
    echo "  run               Ejecutar todas las pruebas (por defecto)"
    echo "  web               Ejecutar solo pruebas web"
    echo "  api               Ejecutar solo pruebas API"
    echo "  debug             Iniciar contenedor en modo debug"
    echo "  clean             Limpiar contenedores e imágenes"
    echo "  shell             Abrir shell en el contenedor"
    echo "  status            Mostrar estado de contenedores"
    echo "  help              Mostrar esta ayuda"
    echo ""
    echo -e "${BOLD}Ejemplos:${NC}"
    echo "  $0 build          # Construir imagen"
    echo "  $0 run            # Ejecutar todas las pruebas"
    echo "  $0 web            # Solo pruebas web"
    echo "  $0 api            # Solo pruebas API"
    echo "  $0 debug          # Modo debug interactivo"
}

# ===============================================================================
# VERIFICACIONES PREVIAS
# ===============================================================================

check_requirements() {
    log "Verificando requisitos..."
    
    # Verificar Docker
    if ! command -v docker &> /dev/null; then
        error "Docker no está instalado. Por favor instala Docker primero."
    fi
    
    # Verificar Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        error "Docker Compose no está instalado."
    fi
    
    # Verificar que Docker está ejecutándose
    if ! docker info &> /dev/null; then
        error "Docker no está ejecutándose. Por favor inicia el servicio Docker."
    fi
    
    log "Requisitos verificados correctamente"
}

# ===============================================================================
# FUNCIONES PRINCIPALES
# ===============================================================================

build_image() {
    log "Construyendo imagen Docker '$IMAGE_NAME'..."
    
    cd "$SCRIPT_DIR"
    
    # Construir imagen con cache
    docker build -t "$IMAGE_NAME" . \
        --build-arg BUILDKIT_INLINE_CACHE=1 \
        --progress=plain
    
    log "Imagen construida exitosamente"
}

run_tests() {
    local test_type="$1"
    
    log "Ejecutando pruebas: $test_type"
    
    # Crear directorios locales si no existen
    mkdir -p downloads
    
    # Limpiar contenedor anterior si existe
    cleanup_container
    
    # Ejecutar contenedor
    local cmd="test"
    case "$test_type" in
        "web") cmd="web" ;;
        "api") cmd="api" ;;
        *) cmd="test" ;;
    esac
    
    docker run --rm \
        --name "$CONTAINER_NAME" \
        -v "$(pwd)/downloads:/app/downloads" \
        --shm-size=2g \
        "$IMAGE_NAME" "$cmd"
}

debug_mode() {
    log "Iniciando contenedor en modo debug..."
    
    cleanup_container
    
    docker run -it --rm \
        --name "$CONTAINER_NAME-debug" \
        -v "$(pwd):/app" \
        -v "$(pwd)/downloads:/app/downloads" \
        --shm-size=2g \
        "$IMAGE_NAME" debug
}

open_shell() {
    log "Abriendo shell en el contenedor..."
    
    cleanup_container
    
    docker run -it --rm \
        --name "$CONTAINER_NAME-shell" \
        -v "$(pwd):/app" \
        --shm-size=2g \
        "$IMAGE_NAME" bash
}

show_logs() {
    log "Mostrando logs..."
    
    # Intentar mostrar logs del contenedor si existe
    if docker ps -a --format "table {{.Names}}" | grep -q "$CONTAINER_NAME"; then
        docker logs "$CONTAINER_NAME"
    else
        # Mostrar logs desde archivos
        if [ -d "logs" ] && [ "$(ls -A logs)" ]; then
            log "Logs desde archivos:"
            find logs -name "*.log" -exec echo "=== {} ===" \; -exec cat {} \;
        else
            warn "No se encontraron logs"
        fi
    fi
}


show_status() {
    log "Estado de contenedores:"
    
    echo -e "${BOLD}Contenedores activos:${NC}"
    docker ps --filter "name=$PROJECT_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    echo -e "\n${BOLD}Imágenes disponibles:${NC}"
    docker images --filter "reference=$PROJECT_NAME*" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
    
    echo -e "\n${BOLD}Volúmenes:${NC}"
    docker volume ls --filter "name=$PROJECT_NAME*" --format "table {{.Name}}\t{{.Driver}}"
}

cleanup_container() {
    # Parar y eliminar contenedor si existe
    if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
        log "Deteniendo contenedor existente..."
        docker stop "$CONTAINER_NAME" >/dev/null 2>&1 || true
    fi
    
    if docker ps -aq -f name="$CONTAINER_NAME" | grep -q .; then
        docker rm "$CONTAINER_NAME" >/dev/null 2>&1 || true
    fi
}

clean_all() {
    log "Limpiando recursos Docker..."
    
    # Parar y eliminar contenedores
    docker ps -aq --filter "name=$PROJECT_NAME" | xargs -r docker stop
    docker ps -aq --filter "name=$PROJECT_NAME" | xargs -r docker rm
    
    # Eliminar imágenes
    docker images -q "$PROJECT_NAME*" | xargs -r docker rmi
    
    # Limpiar volúmenes huérfanos
    docker volume prune -f
    
    log "Limpieza completada"
}

# ===============================================================================
# LÓGICA PRINCIPAL
# ===============================================================================

main() {
    show_banner
    
    # Si no hay argumentos, mostrar ayuda
    if [ $# -eq 0 ]; then
        show_usage
        exit 0
    fi
    
    # Verificar requisitos
    check_requirements
    
    # Procesar argumentos
    case "$1" in
        "build")
            build_image
            ;;
        "run"|"test"|"tests")
            build_image
            run_tests "all"
            ;;
        "web")
            build_image
            run_tests "web"
            ;;
        "api")
            build_image
            run_tests "api"
            ;;
        "debug")
            build_image
            debug_mode
            ;;
        "shell"|"bash")
            build_image
            open_shell
            ;;
        "logs")
            show_logs
            ;;
        "status")
            show_status
            ;;
        "clean")
            clean_all
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            error "Opción desconocida: $1. Usa '$0 help' para ver las opciones disponibles."
            ;;
    esac
}

# Ejecutar función principal
main "$@"
