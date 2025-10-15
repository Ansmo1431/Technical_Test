"""
Ejecutor Principal de Pruebas QA - Automatización
=================================================

Este es el punto de entrada principal para ejecutar todas las pruebas
de automatización (Web + API) de la prueba técnica QA.

Ejecuta de forma secuencial y organizada:
1. Pruebas de automatización web (Selenium)
2. Pruebas de automatización API (REST)
3. Genera reportes consolidados
4. Limpia recursos automáticamente

Optimizaciones implementadas:
- Manejo centralizado de errores
- Reportes detallados de ejecución  
- Limpieza automática de recursos
- Tiempo de ejecución optimizado
"""

import time
import sys
import traceback
from datetime import datetime
from web_automation import run_all_web_tests
from api_automation import run_all_api_tests

# =============================================================================
# CONFIGURACIÓN DEL EJECUTOR
# =============================================================================

class TestRunner:
    """
    Clase principal para ejecutar y coordinar todos los tests.
    Maneja la ejecución secuencial, reportes y limpieza de recursos.
    """
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.web_test_success = False
        self.api_test_success = False
        
    def run_all_tests(self):
        """
        Ejecuta todas las pruebas de automatización de forma coordinada.
        """
        print("INICIANDO BATERÍA COMPLETA DE PRUEBAS QA")
        print("=" * 80)
        print(f"Fecha de ejecución: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("Alcance: Automatización Web (Selenium) + API (REST)")
        print("=" * 80)
        
        self.start_time = time.time()
        
        try:
            # Ejecutar pruebas web
            print("\n" + "WEB: AUTOMATIZACIÓN WEB".center(80, "="))
            self.web_test_success = self._execute_test_suite(
                run_all_web_tests, 
                "Automatización Web"
            )
            
            # Separador visual entre fases
            print("\n" + "Preparando siguiente fase...".center(80, "-"))
            time.sleep(2)
            
            # Ejecutar pruebas API
            print("\n" + "API: AUTOMATIZACIÓN API".center(80, "="))
            self.api_test_success = self._execute_test_suite(
                run_all_api_tests, 
                "Automatización API"
            )
            
        except KeyboardInterrupt:
            print("\nADVERTENCIA: Ejecución interrumpida por el usuario (Ctrl+C)")
            return False
        except Exception as e:
            print(f"\nERROR CRÍTICO: Error crítico en la ejecución: {str(e)}")
            traceback.print_exc()
            return False
        finally:
            self.end_time = time.time()
            self._generate_final_report()
        
        return self.web_test_success and self.api_test_success
    
    def _execute_test_suite(self, test_function, suite_name):
        """
        Ejecuta una suite de tests con manejo de errores.
        
        Args:
            test_function: Función de la suite a ejecutar
            suite_name: Nombre descriptivo de la suite
            
        Returns:
            bool: True si la ejecución fue exitosa
        """
        suite_start_time = time.time()
        
        try:
            print(f"Iniciando suite: {suite_name}")
            test_function()
            
            suite_end_time = time.time()
            suite_duration = suite_end_time - suite_start_time
            
            print(f"EXITOSO: Suite completada: {suite_name}")
            print(f"Duración: {suite_duration:.2f} segundos")
            
            return True
            
        except Exception as e:
            suite_end_time = time.time()
            suite_duration = suite_end_time - suite_start_time
            
            print(f"ERROR: Error en suite: {suite_name}")
            print(f"ERROR: {str(e)}")
            print(f"Duración antes del error: {suite_duration:.2f} segundos")
            
            # Log detallado del error para debugging
            print("\nDETALLES DEL ERROR:")
            print("-" * 50)
            traceback.print_exc()
            print("-" * 50)
            
            return False
    
    def _generate_final_report(self):
        """
        Genera el reporte final consolidado de todas las pruebas.
        """
        total_duration = self.end_time - self.start_time if self.start_time and self.end_time else 0
        
        print("\n" + "REPORTE FINAL DE EJECUCIÓN".center(80, "="))
        print(f"Tiempo total de ejecución: {total_duration:.2f} segundos")
        print(f"Inicio: {datetime.fromtimestamp(self.start_time).strftime('%H:%M:%S')}")
        print(f"Fin: {datetime.fromtimestamp(self.end_time).strftime('%H:%M:%S')}")
        print()
        
        # Estado por suite
        print("ESTADO POR SUITE:")
        print(f"Automatización Web: {'EXITOSO' if self.web_test_success else 'FALLÓ'}")
        print(f"Automatización API: {'EXITOSO' if self.api_test_success else 'FALLÓ'}")
        print()
        
        # Resumen ejecutivo
        total_suites = 2
        successful_suites = sum([self.web_test_success, self.api_test_success])
        success_rate = (successful_suites / total_suites) * 100
        
        print("RESUMEN EJECUTIVO:")
        print(f"Suites ejecutadas: {total_suites}")
        print(f"EXITOSO: Suites exitosas: {successful_suites}")
        print(f"ERROR: Suites fallidas: {total_suites - successful_suites}")
        print(f"Tasa de éxito: {success_rate:.1f}%")
        print()
        
        # Mensaje final basado en resultados
        if success_rate == 100:
            print("EXCELENTE: ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
        elif success_rate >= 50:
            print("ADVERTENCIA: Algunas pruebas fallaron, revisar logs anteriores")
            print("ACCIÓN REQUERIDA: Se requiere corrección antes de despliegue")
        else:
            print("ALERTA: La mayoría de pruebas fallaron")
            print("ACCIÓN REQUERIDA: Se requiere revisión completa del código")
        
        print("=" * 80)

# =============================================================================
# UTILIDADES ADICIONALES
# =============================================================================

def check_environment():
    """
    Verifica que el entorno esté correctamente configurado.
    
    Returns:
        bool: True si el entorno está listo
    """
    print("Verificando entorno de ejecución...")
    
    # Verificar Python
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        print("ERROR: Se requiere Python 3.8 o superior")
        return False
    
    print(f"EXITOSO: Python {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Verificar dependencias críticas
    try:
        import selenium
        print(f"EXITOSO: Selenium {selenium.__version__}")
    except ImportError:
        print("ERROR: Selenium no instalado - ejecutar: pip install selenium")
        return False
    
    try:
        import requests
        print(f"EXITOSO: Requests {requests.__version__}")
    except ImportError:
        print("ERROR: Requests no instalado - ejecutar: pip install requests")
        return False
    
    try:
        import jsonschema
        print(f"EXITOSO: JSONSchema {jsonschema.__version__}")
    except ImportError:
        print("ERROR: JSONSchema no instalado - ejecutar: pip install jsonschema")
        return False
    
    print("EXITOSO: Entorno verificado correctamente")
    return True

def display_usage_info():
    """
    Muestra información de uso del ejecutor.
    """
    print("INFORMACIÓN DE USO")
    print("=" * 50)
    print("Este script ejecuta automáticamente todas las pruebas QA:")
    print()
    print("Pruebas Web incluye:")
    print("   • Login/Logout con validaciones")
    print("   • Elementos dinámicos y cargas asíncronas")
    print("   • Formularios complejos (checkboxes, dropdowns)")
    print("   • Drag & Drop con validaciones")
    print()
    print("Pruebas API incluye:")
    print("   • CRUD completo en JSONPlaceholder")
    print("   • Validación de esquemas JSON")
    print("   • Autenticación en ReqRes API")
    print("   • Rate limiting y robustez")
    print()
    print("Prerrequisitos:")
    print("   • Python 3.8+")
    print("   • Chrome/Chromium instalado")
    print("   • Dependencias: pip install -r requirements.txt")
    print()
    print("Ejecución:")
    print("   python test_runner.py")
    print("=" * 50)

# =============================================================================
# FUNCIÓN PRINCIPAL
# =============================================================================

def main():
    """
    Función principal del ejecutor.
    Coordina verificación de entorno y ejecución de pruebas.
    """
    # Mostrar información de uso
    display_usage_info()
    print()
    
    # Verificar entorno antes de ejecutar
    if not check_environment():
        print("\nERROR: El entorno no está correctamente configurado")
        print("ACCIÓN REQUERIDA: Por favor, instala las dependencias faltantes y vuelve a intentar")
        return sys.exit(1)
    
    print("\nIniciando en 3 segundos...")
    time.sleep(3)
    
    # Ejecutar todas las pruebas
    runner = TestRunner()
    success = runner.run_all_tests()
    
    # Código de salida basado en resultados
    if success:
        print("\nOK: Ejecución completada exitosamente")
        sys.exit(0)
    else:
        print("\nADVERTENCIA: Ejecución completada con errores")
        sys.exit(1)

# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nADVERTENCIA: Ejecución cancelada por el usuario")
        sys.exit(130)  # Código estándar para interrupción por Ctrl+C
    except Exception as e:
        print(f"\nERROR FATAL: Error fatal: {str(e)}")
        traceback.print_exc()
        sys.exit(1)
