"""
Automatización de Pruebas Web con Selenium
==========================================

Este módulo contiene todas las pruebas de automatización web optimizadas
siguiendo principios KISS (Keep It Simple, Stupid) y mejores prácticas
de rendimiento y mantenibilidad.

Funcionalidades incluidas:
- Login/Logout con manejo de errores
- Elementos dinámicos y cargas asíncronas  
- Formularios complejos (checkboxes, dropdowns, controles dinámicos)
- Drag & Drop con validaciones
- Hover effects y múltiples ventanas
- Manejo de JavaScript alerts
- Carga de archivos

Optimizaciones implementadas:
- Driver singleton reutilizable
- Waits explícitos optimizados
- Manejo centralizado de errores
- Configuración externalizada
"""

import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import (
    NoSuchElementException, 
    TimeoutException, 
    WebDriverException
)
from config import (
    WEB_BASE_URL, 
    LOGIN_CREDENTIALS, 
    SELENIUM_TIMEOUTS, 
    BROWSER_CONFIG
)

# =============================================================================
# CLASE SINGLETON PARA EL DRIVER (OPTIMIZACIÓN DE RENDIMIENTO)
# =============================================================================

class WebDriverManager:
    """
    Gestor singleton del WebDriver para optimizar rendimiento.
    Evita crear múltiples instancias del navegador.
    """
    _instance = None
    _driver = None
    
    def __new__(cls, download_dir=None):
        if cls._instance is None:
            cls._instance = super(WebDriverManager, cls).__new__(cls)
            cls._instance.download_dir = download_dir
            cls._instance._driver = None
        return cls._instance
    
    def get_driver(self):
        """
        Retorna una instancia única del WebDriver.
        Crea la instancia solo si no existe (lazy loading).
        """
        if self._driver is None:
            self._driver = self._create_driver()
        return self._driver
    
    def _create_driver(self):
        """
        Crea y configura el WebDriver optimizado.
        Aplica configuraciones de rendimiento y timeouts.
        Detecta automáticamente si está ejecutándose en Docker.
        """
        chrome_options = Options()
        
        # Configuraciones de rendimiento
        if BROWSER_CONFIG["headless"]:
            chrome_options.add_argument("--headless")
        
        # Configuraciones básicas
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument(f"--window-size={BROWSER_CONFIG['window_size'][0]},{BROWSER_CONFIG['window_size'][1]}")
        
        # Optimizaciones adicionales
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-plugins")
        chrome_options.add_argument("--disable-images")
        
        # Configuración de descargas
        downloads_dir = os.path.abspath("downloads")
        os.makedirs(downloads_dir, exist_ok=True)
        prefs = {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.password_manager_leak_detection": False,
            "download.default_directory": downloads_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Configuraciones específicas para Docker
        if os.getenv('QA_ENV') == 'docker' or os.getenv('HEADLESS_MODE') == 'true':
            chrome_options.add_argument("--disable-features=VizDisplayCompositor")
            chrome_options.add_argument("--remote-debugging-port=9222")
            chrome_options.add_argument("--disable-default-apps")
            chrome_options.add_argument("--disable-background-timer-throttling")
            chrome_options.add_argument("--disable-backgrounding-occluded-windows")
            chrome_options.add_argument("--disable-renderer-backgrounding")
        
        # Intentar crear el driver con manejo de errores mejorado
        try:
            driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"ERROR: Fallo al crear WebDriver: {str(e)}")
            print("INTENTANDO: Usar webdriver-manager como alternativa...")
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                from selenium.webdriver.chrome.service import Service
                
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                print("EXITOSO: WebDriver creado con webdriver-manager")
            except ImportError:
                print("ADVERTENCIA: webdriver-manager no disponible")
                raise e
            except Exception as e2:
                print(f"ERROR: Falló webdriver-manager: {str(e2)}")
                raise e
        
        # Configurar timeouts optimizados
        driver.implicitly_wait(SELENIUM_TIMEOUTS["implicit_wait"])
        driver.set_page_load_timeout(SELENIUM_TIMEOUTS["page_load"])
        driver.set_script_timeout(SELENIUM_TIMEOUTS["script"])
        
        return driver
    
    def quit_driver(self):
        """
        Cierra el driver y limpia la instancia.
        """
        if self._driver:
            try:
                self._driver.quit()
            except Exception as e:
                print(f"Error cerrando driver: {e}")
            finally:
                self._driver = None

# =============================================================================
# UTILIDADES COMUNES PARA OPTIMIZACIÓN
# =============================================================================

def wait_and_find_element(driver, locator, timeout=None):
    """
    Utilidad optimizada para encontrar elementos con espera explícita.
    
    Args:
        driver: Instancia del WebDriver
        locator: Tupla (By.METHOD, "selector")
        timeout: Timeout personalizado (opcional)
    
    Returns:
        WebElement encontrado
        
    Raises:
        TimeoutException: Si el elemento no se encuentra
    """
    timeout = timeout or SELENIUM_TIMEOUTS["explicit_wait"]
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_element_located(locator))

def wait_and_click_element(driver, locator, timeout=None):
    """
    Utilidad optimizada para hacer click con espera hasta que sea clickeable.
    
    Args:
        driver: Instancia del WebDriver
        locator: Tupla (By.METHOD, "selector")
        timeout: Timeout personalizado (opcional)
    """
    timeout = timeout or SELENIUM_TIMEOUTS["explicit_wait"]
    wait = WebDriverWait(driver, timeout)
    element = wait.until(EC.element_to_be_clickable(locator))
    element.click()
    return element

def navigate_to_section(driver, section_name):
    """
    Navega a una sección específica desde la página principal.
    Optimizado para reutilización y manejo de errores.
    
    Args:
        driver: Instancia del WebDriver
        section_name: Nombre del link a clickear
    """
    try:
        # Ir a la página principal si no estamos ahí
        if WEB_BASE_URL not in driver.current_url:
            driver.get(WEB_BASE_URL)
        
        # Buscar y hacer click en el link de la sección
        link_locator = (By.XPATH, f"//a[text()='{section_name}']")
        wait_and_click_element(driver, link_locator)
        
    except TimeoutException:
        raise Exception(f"No se pudo encontrar la sección: {section_name}")

# =============================================================================
# TESTS DE AUTENTICACIÓN (LOGIN/LOGOUT)
# =============================================================================

def test_authentication():
    """
    Prueba completa de autenticación: login exitoso y logout.
    Incluye validaciones de elementos y manejo de errores.
    """
    print("Iniciando pruebas de autenticación...")
    
    driver_manager = WebDriverManager()
    driver = driver_manager.get_driver()
    
    try:
        # Navegar a la sección de Form Authentication
        navigate_to_section(driver, "Form Authentication")
        
        # Verificar que llegamos a la página de login
        login_title = wait_and_find_element(
            driver, 
            (By.XPATH, "//h2[text()='Login Page']")
        )
        assert login_title.is_displayed(), "No se encontró el título de la página de login"
        
        # Realizar login con credenciales válidas
        _perform_login(driver, LOGIN_CREDENTIALS["valid"])
        
        # Verificar login exitoso
        secure_area_title = wait_and_find_element(
            driver,
            (By.XPATH, "//h2[contains(text(),'Secure Area')]")
        )
        assert secure_area_title.is_displayed(), "Login falló - no se encontró Secure Area"
        
        # Verificar mensaje de éxito
        success_message = wait_and_find_element(
            driver,
            (By.ID, "flash")
        )
        assert "You logged into a secure area!" in success_message.text
        
        # Realizar logout
        _perform_logout(driver)
        
        # Verificar logout exitoso
        login_title_after_logout = wait_and_find_element(
            driver,
            (By.XPATH, "//h2[text()='Login Page']")
        )
        assert login_title_after_logout.is_displayed(), "Logout falló"
        
        print("EXITOSO: Pruebas de autenticación completadas")
        driver_manager.quit_driver()
    except Exception as e:
        print(f"ERROR: Error en pruebas de autenticación: {str(e)}")
        raise

def _perform_login(driver, credentials):
    """
    Función auxiliar para realizar el proceso de login.
    
    Args:
        driver: Instancia del WebDriver
        credentials: Diccionario con username y password
    """
    # Localizar campos de entrada
    username_field = wait_and_find_element(driver, (By.ID, "username"))
    password_field = wait_and_find_element(driver, (By.ID, "password"))
    
    # Limpiar campos (buena práctica)
    username_field.clear()
    password_field.clear()
    
    # Ingresar credenciales
    username_field.send_keys(credentials["username"])
    password_field.send_keys(credentials["password"])
    
    # Hacer click en botón de login
    wait_and_click_element(driver, (By.XPATH, "//button[@class='radius']"))

def _perform_logout(driver):
    """
    Función auxiliar para realizar el proceso de logout.
    
    Args:
        driver: Instancia del WebDriver
    """
    logout_button = wait_and_click_element(
        driver,
        (By.XPATH, "//a[@class='button secondary radius']")
    )

# =============================================================================
# TESTS DE ELEMENTOS DINÁMICOS
# =============================================================================

def test_dynamic_loading():
    """
    Prueba la carga dinámica de elementos (Dynamic Loading Examples 1 & 2).
    Valida el manejo de elementos que aparecen/desaparecen dinámicamente.
    """
    print("Iniciando pruebas de carga dinámica...")
    
    driver_manager = WebDriverManager()
    driver = driver_manager.get_driver()
    
    try:
        # Navegar a Dynamic Loading
        navigate_to_section(driver, "Dynamic Loading")
        
        # Verificar página de Dynamic Loading
        title = wait_and_find_element(
            driver,
            (By.XPATH, "//h3[text()='Dynamically Loaded Page Elements']")
        )
        assert title.is_displayed()
        
        # Probar Example 1 (elemento oculto que se hace visible)
        _test_dynamic_example(driver, "Example 1")
        
        # Volver a la página principal de Dynamic Loading
        driver.back()
        
        # Probar Example 2 (elemento que se crea dinámicamente)
        _test_dynamic_example(driver, "Example 2")
        
        print("EXITOSO: Pruebas de carga dinámica completadas")
        driver_manager.quit_driver()
    except Exception as e:
        print(f"ERROR: Error en pruebas de carga dinámica: {str(e)}")
        raise

def _test_dynamic_example(driver, example_name):
    """
    Función auxiliar para probar un ejemplo específico de carga dinámica.
    
    Args:
        driver: Instancia del WebDriver
        example_name: Nombre del ejemplo ("Example 1" o "Example 2")
    """
    # Hacer click en el ejemplo
    example_link = wait_and_find_element(
        driver,
        (By.XPATH, f"//a[contains(text(),'{example_name}')]")
    )
    example_link.click()
    
    # Verificar que llegamos a la página del ejemplo
    wait_and_find_element(
        driver,
        (By.XPATH, f"//h4[contains(text(),'{example_name}')]")
    )
    
    # Hacer click en Start para iniciar la carga dinámica
    start_button = wait_and_click_element(driver, (By.XPATH, "//button[text()='Start']"))
    
    # Esperar a que aparezca el mensaje "Hello World!"
    # Usar un timeout mayor para la carga dinámica
    hello_message = WebDriverWait(driver, 20).until(
        EC.visibility_of_element_located((By.XPATH, "//h4[text()='Hello World!']"))
    )
    
    # Validar que el mensaje es correcto
    assert hello_message.text == "Hello World!", f"Mensaje incorrecto en {example_name}"

# =============================================================================
# TESTS DE FORMULARIOS COMPLEJOS
# =============================================================================

def test_complex_forms():
    """
    Prueba formularios complejos: checkboxes, dropdowns y controles dinámicos.
    Valida interacciones complejas con elementos de formulario.
    """
    print("Iniciando pruebas de formularios complejos...")
    
    driver_manager = WebDriverManager()
    driver = driver_manager.get_driver()
    
    try:
        # Probar checkboxes
        _test_checkboxes(driver)
        
        # Probar dropdown
        _test_dropdown(driver)
        
        # Probar controles dinámicos
        _test_dynamic_controls(driver)
        
        print("EXITOSO: Pruebas de formularios complejos completadas")
        driver_manager.quit_driver()
    except Exception as e:
        print(f"ERROR: Error en pruebas de formularios complejos: {str(e)}")
        raise

def _test_checkboxes(driver):
    """
    Prueba la funcionalidad de checkboxes.
    """
    navigate_to_section(driver, "Checkboxes")
    
    # Verificar título
    wait_and_find_element(driver, (By.XPATH, "//h3[text()='Checkboxes']"))
    
    # Obtener todos los checkboxes
    checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
    
    # Seleccionar todos los checkboxes que no estén seleccionados
    for checkbox in checkboxes:
        if not checkbox.is_selected():
            checkbox.click()
            # Usar lambda para esperar el cambio de estado
            WebDriverWait(driver, 5).until(lambda d: checkbox.is_selected())
            assert checkbox.is_selected(), "Checkbox no se seleccionó correctamente"
    
    # Deseleccionar todos los checkboxes
    for checkbox in checkboxes:
        if checkbox.is_selected():
            checkbox.click()
            WebDriverWait(driver, 5).until(lambda d: not checkbox.is_selected())
            assert not checkbox.is_selected(), "Checkbox no se deseleccionó correctamente"
    
    driver.back()

def _test_dropdown(driver):
    """
    Prueba la funcionalidad de dropdown/select.
    """
    navigate_to_section(driver, "Dropdown")
    
    # Verificar título
    wait_and_find_element(driver, (By.XPATH, "//h3[text()='Dropdown List']"))
    
    # Localizar el dropdown
    dropdown_element = wait_and_find_element(driver, (By.ID, "dropdown"))
    select = Select(dropdown_element)
    
    # Probar todas las opciones válidas (omitir opción vacía)
    for option in select.options:
        value = option.get_attribute("value")
        if value:  # Omitir opción vacía
            select.select_by_value(value)
            selected_option = select.first_selected_option
            assert selected_option.text == option.text, "Opción no seleccionada correctamente"
    
    driver.back()

def _test_dynamic_controls(driver):
    """
    Prueba controles dinámicos (add/remove, enable/disable).
    """
    navigate_to_section(driver, "Dynamic Controls")
    
    # Verificar título
    wait_and_find_element(driver, (By.XPATH, "//h4[text()='Dynamic Controls']"))
    
    # Test: Remove/Add checkbox
    checkbox = wait_and_find_element(driver, (By.XPATH, "//input[@type='checkbox']"))
    checkbox.click()  # Seleccionar checkbox antes de remover
    
    # Remover checkbox
    wait_and_click_element(driver, (By.XPATH, "//button[text()='Remove']"))
    
    # Verificar mensaje de eliminación
    delete_message = wait_and_find_element(
        driver,
        (By.XPATH, "//p[text()=\"It's gone!\"]")
    )
    assert delete_message.text == "It's gone!"
    
    # Agregar checkbox de vuelta
    wait_and_click_element(driver, (By.XPATH, "//button[text()='Add']"))
    
    # Verificar mensaje de adición
    add_message = wait_and_find_element(
        driver,
        (By.XPATH, "//p[text()=\"It's back!\"]")
    )
    assert add_message.text == "It's back!"
    
    # Test: Enable/Disable text input
    wait_and_click_element(driver, (By.XPATH, "//button[text()='Enable']"))
    
    # Esperar a que el input se habilite y escribir texto
    text_input = wait_and_find_element(driver, (By.XPATH, "//input[@type='text']"))
    WebDriverWait(driver, 10).until(lambda d: text_input.is_enabled())
    text_input.send_keys("Texto de prueba")
    
    # Deshabilitar input
    wait_and_click_element(driver, (By.XPATH, "//button[text()='Disable']"))
    
    # Verificar que se deshabilitó
    WebDriverWait(driver, 10).until(
        lambda d: not d.find_element(By.XPATH, "//input[@type='text']").is_enabled()
    )

# =============================================================================
# TESTS DE DRAG & DROP
# =============================================================================

def test_drag_and_drop():
    """
    Prueba la funcionalidad de arrastrar y soltar elementos.
    Valida que los elementos se mueven correctamente.
    """
    print("Iniciando pruebas de Drag & Drop...")
    
    driver_manager = WebDriverManager()
    driver = driver_manager.get_driver()
    
    try:
        navigate_to_section(driver, "Drag and Drop")
        
        # Verificar título
        wait_and_find_element(driver, (By.XPATH, "//h3[text()='Drag and Drop']"))
        
        # Localizar elementos source y target
        source = wait_and_find_element(driver, (By.ID, "column-a"))
        target = wait_and_find_element(driver, (By.ID, "column-b"))
        
        # Verificar contenido inicial
        initial_source_text = source.text
        initial_target_text = target.text
        
        # Realizar drag and drop usando ActionChains
        actions = ActionChains(driver)
        actions.drag_and_drop(source, target).perform()
        
        # Esperar a que se complete el movimiento y verificar el intercambio
        WebDriverWait(driver, 10).until(
            lambda d: initial_source_text in target.text or initial_target_text in source.text
        )
        
        # Validar que se intercambiaron las posiciones
        assert initial_source_text in target.text, "El elemento no se movió correctamente al destino"
        
        # Realizar drag and drop inverso para probar bidireccionalidad  
        actions.drag_and_drop(target, source).perform()
        
        WebDriverWait(driver, 10).until(
            lambda d: initial_target_text in target.text or initial_source_text in source.text
        )
        
        print("EXITOSO: Pruebas de Drag & Drop completadas")
        driver_manager.quit_driver()
    except Exception as e:
        print(f"ERROR: Error en pruebas de Drag & Drop: {str(e)}")
        raise

# =============================================================================
# TESTS DE FILE UPLOAD/DOWNLOAD
# =============================================================================

def test_file_operations():
    """
    Prueba la funcionalidad de carga y descarga de archivos.
    Valida tanto upload como download con verificaciones de archivos.
    """
    print("Iniciando pruebas de operaciones con archivos...")

    driver_manager = WebDriverManager()
    driver = driver_manager.get_driver()
    
    try:
        # Probar descarga de archivos
        _test_file_download(driver)
        
        # Probar carga de archivos  
        _test_file_upload(driver)
        
        print("EXITOSO: Pruebas de operaciones con archivos completadas")
        driver_manager.quit_driver()
    except Exception as e:
        print(f"ERROR: Error en pruebas de operaciones con archivos: {str(e)}")
        raise

def _test_file_download(driver):
    """
    Prueba la descarga de archivos con verificación automática.
    
    Args:
        driver: Instancia del WebDriver
    """
    # Crear directorio de descarga si no existe
    downloads_dir = os.path.abspath("downloads")
    os.makedirs(downloads_dir, exist_ok=True)

    # Navegar a la sección de descarga de archivos
    navigate_to_section(driver, "File Download")

    # Archivo de prueba disponible en el sitio
    test_file = "drag_drop.txt"
    file_path = os.path.join(downloads_dir, test_file)
    
    # Eliminar archivo si ya existe (para prueba limpia)
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Hacer click en el link de descarga
    download_link = wait_and_find_element(driver, (By.LINK_TEXT, test_file))
    download_link.click()
    
    # Esperar a que el archivo se descargue (usando polling optimizado)
    download_timeout = 30  # segundos
    start_time = time.time()
    
    while not os.path.exists(file_path):
        if time.time() - start_time > download_timeout:
            raise TimeoutException(f"Archivo no descargado en {download_timeout}s")
        time.sleep(0.5)  # Polling cada medio segundo
    
    # Verificar que el archivo se descargó correctamente
    assert os.path.exists(file_path), f"Archivo no encontrado: {file_path}"
    
    print(f"EXITOSO: Archivo descargado: {test_file}")
    
    driver.back()

def _test_file_upload(driver):
    """
    Prueba la carga de archivos con validaciones completas.
    
    Args:
        driver: Instancia del WebDriver
    """
    navigate_to_section(driver, "File Upload")
    
    # Verificar título
    wait_and_find_element(driver, (By.XPATH, "//h3[text()='File Uploader']"))
    
    # Usar archivo de prueba (debe existir en el directorio del proyecto)
    test_file = "drag_drop.txt"
    
    # Buscar el archivo en posibles ubicaciones
    possible_paths = [
        os.path.abspath(test_file),
        os.path.abspath(f"automation_test/automation/{test_file}"),
        os.path.abspath(f"downloads/{test_file}")
    ]
    
    file_path = None
    for path in possible_paths:
        if os.path.exists(path):
            file_path = path
            break
    
    if not file_path:
        # Crear archivo de prueba mínimo si no existe
        file_path = os.path.abspath(test_file)
        with open(file_path, "w") as f:
            f.write("test file content for upload")
        print(f"ADVERTENCIA: Archivo de prueba creado: {file_path}")
    
    # Localizar campo de carga de archivos
    file_input = wait_and_find_element(driver, (By.ID, "file-upload"))
    
    # Enviar ruta del archivo al input
    file_input.send_keys(file_path)
    
    # Hacer click en botón de upload
    upload_button = wait_and_click_element(driver, (By.ID, "file-submit"))
    
    # Verificar mensaje de éxito
    success_message = wait_and_find_element(
        driver,
        (By.XPATH, "//h3[text()='File Uploaded!']")
    )
    assert success_message.text == "File Uploaded!", "Mensaje de éxito no encontrado"
    
    # Verificar que se muestra el nombre del archivo cargado
    uploaded_file_name = wait_and_find_element(driver, (By.ID, "uploaded-files"))
    expected_name = os.path.basename(file_path)
    assert expected_name in uploaded_file_name.text, f"Nombre de archivo no coincide: esperado {expected_name}, actual {uploaded_file_name.text}"
    
    print(f"EXITOSO: Archivo cargado: {os.path.basename(file_path)}")

# =============================================================================
# TESTS DE HOVERS Y TOOLTIPS
# =============================================================================

def test_hover_interactions():
    """
    Prueba las interacciones de hover y tooltips.
    Valida que los elementos aparezcan correctamente al hacer hover.
    """
    print("Iniciando pruebas de hover e interacciones...")
    
    driver_manager = WebDriverManager()
    driver = driver_manager.get_driver()
    
    try:
        navigate_to_section(driver, "Hovers")
        
        # Verificar título
        wait_and_find_element(driver, (By.XPATH, "//h3[text()='Hovers']"))
        
        # Textos esperados para cada avatar
        expected_texts = [
            "name: user1",
            "name: user2", 
            "name: user3"
        ]
        
        # Localizar todos los avatares
        avatars = driver.find_elements(By.XPATH, "//img[@alt='User Avatar']")
        actions = ActionChains(driver)
        
        assert len(avatars) >= 3, "No se encontraron suficientes avatares para probar"
        
        # Probar hover en cada avatar
        for i, avatar in enumerate(avatars[:3]):  # Limitar a 3 para coincidir con expected_texts
            print(f"Probando hover en avatar #{i+1}")
            
            # Hacer hover sobre el avatar
            actions.move_to_element(avatar).perform()
            
            # Esperar a que aparezca el texto del hover
            expected_text = expected_texts[i]
            hover_text_element = wait_and_find_element(
                driver,
                (By.XPATH, f"//h5[contains(text(), '{expected_text}')]")
            )
            
            # Verificar que el texto es correcto
            actual_text = hover_text_element.text.lower()
            assert expected_text.lower() in actual_text, f"Texto de hover incorrecto para avatar #{i+1}"
            
            print(f"EXITOSO: Hover #{i+1} verificado: {expected_text}")
            
            # Pequeña pausa entre hovers para estabilidad
            time.sleep(0.5)
        
        print("EXITOSO: Pruebas de hover completadas")
        driver_manager.quit_driver()
    except Exception as e:
        print(f"ERROR: Error en pruebas de hover: {str(e)}")
        raise

# =============================================================================
# TESTS DE JAVASCRIPT ALERTS
# =============================================================================

def test_javascript_alerts():
    """
    Prueba el manejo de diferentes tipos de alertas JavaScript.
    Incluye: Alert simple, Confirm, y Prompt con entrada de texto.
    """
    print("Iniciando pruebas de JavaScript Alerts...")
    
    driver_manager = WebDriverManager()
    driver = driver_manager.get_driver()
    
    try:
        navigate_to_section(driver, "JavaScript Alerts")
        
        # Verificar título
        wait_and_find_element(driver, (By.XPATH, "//h3[text()='JavaScript Alerts']"))
        
        # Test 1: Alert simple
        _test_js_alert(driver)
        
        # Test 2: Confirm (aceptar)
        _test_js_confirm(driver, accept=True)
        
        # Test 3: Confirm (cancelar)
        _test_js_confirm(driver, accept=False)
        
        # Test 4: Prompt con texto
        _test_js_prompt(driver, input_text="Texto de prueba QA")
        
        print("EXITOSO: Pruebas de JavaScript Alerts completadas")
        driver_manager.quit_driver()
    except Exception as e:
        print(f"ERROR: Error en pruebas de JavaScript Alerts: {str(e)}")
        raise

def _test_js_alert(driver):
    """
    Prueba alert JavaScript simple.
    
    Args:
        driver: Instancia del WebDriver
    """
    # Hacer click en botón de JS Alert
    alert_button = wait_and_click_element(
        driver,
        (By.XPATH, "//button[contains(text(),'JS Alert')]")
    )
    
    # Esperar a que aparezca la alert
    WebDriverWait(driver, 10).until(EC.alert_is_present())
    
    # Cambiar foco a la alert y aceptarla
    alert = driver.switch_to.alert
    alert_text = alert.text
    alert.accept()
    
    # Verificar mensaje resultado
    result_element = wait_and_find_element(driver, (By.ID, "result"))
    assert "You successfully clicked an alert" in result_element.text
    
    print("EXITOSO: JS Alert manejada correctamente")

def _test_js_confirm(driver, accept=True):
    """
    Prueba confirm JavaScript.
    
    Args:
        driver: Instancia del WebDriver
        accept: True para aceptar, False para cancelar
    """
    # Hacer click en botón de JS Confirm
    confirm_button = wait_and_click_element(
        driver,
        (By.XPATH, "//button[contains(text(),'JS Confirm')]")
    )
    
    # Esperar a que aparezca la confirm
    WebDriverWait(driver, 10).until(EC.alert_is_present())
    
    # Manejar la confirm
    alert = driver.switch_to.alert
    if accept:
        alert.accept()
        expected_text = "You clicked: Ok"
    else:
        alert.dismiss()
        expected_text = "You clicked: Cancel"
    
    # Verificar resultado
    result_element = wait_and_find_element(driver, (By.ID, "result"))
    assert expected_text in result_element.text
    
    action = "aceptada" if accept else "cancelada"
    print(f"EXITOSO: JS Confirm {action} correctamente")

def _test_js_prompt(driver, input_text):
    """
    Prueba prompt JavaScript con entrada de texto.
    
    Args:
        driver: Instancia del WebDriver
        input_text: Texto a introducir en el prompt
    """
    # Hacer click en botón de JS Prompt
    prompt_button = wait_and_click_element(
        driver,
        (By.XPATH, "//button[contains(text(),'JS Prompt')]")
    )
    
    # Esperar a que aparezca el prompt
    WebDriverWait(driver, 10).until(EC.alert_is_present())
    
    # Manejar el prompt
    alert = driver.switch_to.alert
    alert.send_keys(input_text)
    alert.accept()
    
    # Verificar resultado
    result_element = wait_and_find_element(driver, (By.ID, "result"))
    assert f"You entered: {input_text}" in result_element.text
    
    print(f"EXITOSO: JS Prompt manejado correctamente con texto: '{input_text}'")

# =============================================================================
# TESTS DE MULTIPLE WINDOWS
# =============================================================================

def test_multiple_windows():
    """
    Prueba el manejo de múltiples ventanas del navegador.
    Valida apertura, cambio de contexto y cierre de ventanas.
    """
    print("Iniciando pruebas de múltiples ventanas...")
    
    driver_manager = WebDriverManager()
    driver = driver_manager.get_driver()
    
    try:
        # Guardar handle de ventana principal
        main_window = driver.current_window_handle
        initial_window_count = len(driver.window_handles)
        
        navigate_to_section(driver, "Multiple Windows")
        
        # Verificar título
        wait_and_find_element(driver, (By.XPATH, "//h3[text()='Opening a new window']"))
        
        # Hacer click en el link que abre nueva ventana
        new_window_link = wait_and_click_element(
            driver,
            (By.XPATH, "//a[text()='Click Here']")
        )
        
        # Esperar a que se abra la nueva ventana
        WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > initial_window_count)
        
        # Encontrar y cambiar a la nueva ventana
        new_window = None
        for handle in driver.window_handles:
            if handle != main_window:
                new_window = handle
                driver.switch_to.window(handle)
                break
        
        assert new_window is not None, "No se encontró la nueva ventana"
        
        # Verificar contenido de la nueva ventana
        new_window_title = wait_and_find_element(
            driver,
            (By.XPATH, "//h3[text()='New Window']")
        )
        assert "New Window" in new_window_title.text
        
        # Verificar que estamos en una ventana diferente
        assert driver.current_window_handle != main_window
        
        print("EXITOSO: Nueva ventana abierta y verificada correctamente")
        
        # Cerrar la nueva ventana
        driver.close()
        
        # Volver a la ventana principal
        driver.switch_to.window(main_window)
        
        # Verificar que volvimos a la ventana principal
        assert driver.current_window_handle == main_window
        
        # Verificar que estamos de vuelta en la página correcta
        wait_and_find_element(driver, (By.XPATH, "//h3[text()='Opening a new window']"))
        
        print("EXITOSO: Pruebas de múltiples ventanas completadas")
        driver_manager.quit_driver()
    except Exception as e:
        print(f"ERROR: Error en pruebas de múltiples ventanas: {str(e)}")
        # Asegurar que volvemos a la ventana principal en caso de error
        try:
            driver.switch_to.window(main_window)
        except:
            pass
        raise

# =============================================================================
# FUNCIÓN PRINCIPAL PARA EJECUTAR TODOS LOS TESTS WEB
# =============================================================================

def run_all_web_tests():
    """
    Ejecuta todos los tests de automatización web de forma secuencial.
    Maneja errores globalmente y asegura limpieza de recursos.
    """
    print("Iniciando batería completa de pruebas web...")
    print("=" * 60)
    
    driver_manager = WebDriverManager()
    
    try:
        # Lista de tests a ejecutar
        test_functions = [
            test_authentication,
            test_dynamic_loading, 
            test_complex_forms,
            test_drag_and_drop,
            test_file_operations,
            test_hover_interactions,
            test_javascript_alerts,
            test_multiple_windows
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
        print("REPORTE FINAL DE PRUEBAS WEB:")
        print(f"EXITOSO: Tests exitosos: {successful_tests}")
        print(f"ERROR: Tests fallidos: {failed_tests}")
        print(f"Tasa de éxito: {(successful_tests/(successful_tests+failed_tests))*100:.1f}%")
        
    except Exception as e:
        print(f"ERROR CRÍTICO: Error crítico en la ejecución: {str(e)}")
    
    finally:
        # Asegurar limpieza de recursos
        print("Limpiando recursos...")
        driver_manager.quit_driver()
        print("EXITOSO: Recursos liberados correctamente")

# =============================================================================
# EJECUCIÓN DIRECTA DEL MÓDULO
# =============================================================================

if __name__ == "__main__":
    run_all_web_tests()
