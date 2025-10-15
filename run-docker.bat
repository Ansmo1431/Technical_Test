@echo off
REM ===============================================================================
REM LANZADOR DOCKER - AUTOMATIZACIÓN QA (WINDOWS)
REM ===============================================================================
REM Script de lanzamiento para Windows - Ejecutar pruebas con Docker

setlocal enabledelayedexpansion

REM Variables
set PROJECT_NAME=qa-automation
set IMAGE_NAME=%PROJECT_NAME%:latest
set CONTAINER_NAME=%PROJECT_NAME%-container

REM ===============================================================================
REM FUNCIONES AUXILIARES
REM ===============================================================================

:show_banner
echo ===============================================================================
echo                    AUTOMATIZACION QA - LANZADOR DOCKER                       
echo ===============================================================================
echo.
goto :eof

:show_usage
echo Uso: %~nx0 [OPCION] [ARGUMENTOS]
echo.
echo Opciones disponibles:
echo   build              Construir la imagen Docker
echo   run               Ejecutar todas las pruebas (por defecto)
echo   web               Ejecutar solo pruebas web
echo   api               Ejecutar solo pruebas API
echo   debug             Iniciar contenedor en modo debug
echo   clean             Limpiar contenedores e imagenes
echo   shell             Abrir shell en el contenedor
echo   status            Mostrar estado de contenedores
echo   help              Mostrar esta ayuda
echo.
echo Ejemplos:
echo   %~nx0 build          # Construir imagen
echo   %~nx0 run            # Ejecutar todas las pruebas
echo   %~nx0 web            # Solo pruebas web
echo   %~nx0 api            # Solo pruebas API
echo   %~nx0 debug          # Modo debug interactivo
goto :eof

REM ===============================================================================
REM VERIFICACIONES PREVIAS
REM ===============================================================================

:check_requirements
echo [INFO] Verificando requisitos...

REM Verificar Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker no esta instalado. Por favor instala Docker Desktop primero.
    exit /b 1
)

REM Verificar Docker Compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose no esta instalado.
    exit /b 1
)

REM Verificar que Docker está ejecutándose
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker no esta ejecutandose. Por favor inicia Docker Desktop.
    exit /b 1
)

echo [INFO] Requisitos verificados correctamente
goto :eof

REM ===============================================================================
REM FUNCIONES PRINCIPALES
REM ===============================================================================

:build_image
echo [INFO] Construyendo imagen Docker '%IMAGE_NAME%'...
docker build -t %IMAGE_NAME% . --build-arg BUILDKIT_INLINE_CACHE=1
if errorlevel 1 (
    echo [ERROR] Error construyendo la imagen
    exit /b 1
)
echo [INFO] Imagen construida exitosamente
goto :eof

:run_tests
set test_type=%1
echo [INFO] Ejecutando pruebas: %test_type%

REM Crear directorios locales si no existen
if not exist downloads mkdir downloads

REM Limpiar contenedor anterior si existe
call :cleanup_container

REM Determinar comando
set cmd=test
if "%test_type%"=="web" set cmd=web
if "%test_type%"=="api" set cmd=api

REM Ejecutar contenedor
docker run --rm --name %CONTAINER_NAME% -v "%cd%\downloads:/app/downloads" --shm-size=2g %IMAGE_NAME% %cmd%
goto :eof

:debug_mode
echo [INFO] Iniciando contenedor en modo debug...
call :cleanup_container
docker run -it --rm --name %CONTAINER_NAME%-debug -v "%cd%:/app" -v "%cd%\downloads:/app/downloads" --shm-size=2g %IMAGE_NAME% debug
goto :eof

:open_shell
echo [INFO] Abriendo shell en el contenedor...
call :cleanup_container
docker run -it --rm --name %CONTAINER_NAME%-shell -v "%cd%:/app" --shm-size=2g %IMAGE_NAME% bash
goto :eof

:show_logs
echo [INFO] Mostrando logs...
docker logs %CONTAINER_NAME% 2>nul || (
    echo [WARN] No se encontraron logs del contenedor. Mostrando logs desde archivos:
    if exist logs\*.log (
        for %%f in (logs\*.log) do (
            echo === %%f ===
            type "%%f"
        )
    ) else (
        echo [WARN] No se encontraron logs
    )
)
goto :eof


:show_status
echo [INFO] Estado de contenedores:
echo.
echo Contenedores activos:
docker ps --filter "name=%PROJECT_NAME%" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
echo.
echo Imagenes disponibles:
docker images --filter "reference=%PROJECT_NAME%*" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
goto :eof

:cleanup_container
REM Parar y eliminar contenedor si existe
docker stop %CONTAINER_NAME% >nul 2>&1
docker rm %CONTAINER_NAME% >nul 2>&1
goto :eof

:clean_all
echo [INFO] Limpiando recursos Docker...
for /f %%i in ('docker ps -aq --filter "name=%PROJECT_NAME%" 2^>nul') do docker stop %%i && docker rm %%i
for /f %%i in ('docker images -q "%PROJECT_NAME%*" 2^>nul') do docker rmi %%i
docker volume prune -f
echo [INFO] Limpieza completada
goto :eof

REM ===============================================================================
REM LÓGICA PRINCIPAL
REM ===============================================================================

:main
call :show_banner

REM Si no hay argumentos, mostrar ayuda
if "%~1"=="" (
    call :show_usage
    exit /b 0
)

REM Verificar requisitos
call :check_requirements
if errorlevel 1 exit /b 1

REM Procesar argumentos
if "%1"=="build" (
    call :build_image
) else if "%1"=="run" (
    call :build_image && call :run_tests all
) else if "%1"=="test" (
    call :build_image && call :run_tests all
) else if "%1"=="tests" (
    call :build_image && call :run_tests all
) else if "%1"=="web" (
    call :build_image && call :run_tests web
) else if "%1"=="api" (
    call :build_image && call :run_tests api
) else if "%1"=="debug" (
    call :build_image && call :debug_mode
) else if "%1"=="shell" (
    call :build_image && call :open_shell
) else if "%1"=="bash" (
    call :build_image && call :open_shell
) else if "%1"=="logs" (
    call :show_logs
) else if "%1"=="status" (
    call :show_status
) else if "%1"=="clean" (
    call :clean_all
) else if "%1"=="help" (
    call :show_usage
) else if "%1"=="-h" (
    call :show_usage
) else if "%1"=="--help" (
    call :show_usage
) else (
    echo [ERROR] Opcion desconocida: %1. Usa '%~nx0 help' para ver las opciones disponibles.
    exit /b 1
)

goto :eof

REM Ejecutar función principal
call :main %*
