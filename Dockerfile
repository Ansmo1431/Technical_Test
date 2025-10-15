# ===============================================================================
# DOCKERFILE PARA AUTOMATIZACIÓN QA - PRUEBA TÉCNICA
# ===============================================================================
# Imagen optimizada para ejecutar pruebas de automatización web y API
# Incluye Python, Chrome, ChromeDriver y todas las dependencias necesarias

# Usar imagen base de Python con Ubuntu para compatibilidad completa
FROM python:3.11-slim-bullseye

# Metadata del contenedor
LABEL maintainer="QA Automation Team"
LABEL description="Automatización de pruebas web y API para prueba técnica QA"
LABEL version="1.0"

# Variables de entorno para optimización
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV DISPLAY=:99
ENV DEBIAN_FRONTEND=noninteractive

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash qauser

# Actualizar sistema e instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    # Dependencias básicas
    wget \
    curl \
    unzip \
    gnupg \
    software-properties-common \
    # Dependencias para Chrome
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgcc1 \
    libgconf-2-4 \
    libgdk-pixbuf2.0-0 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    ca-certificates \
    fonts-liberation \
    libappindicator1 \
    libnss3 \
    lsb-release \
    xdg-utils \
    # Virtual display para modo headless
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Instalar Google Chrome (versión estable)
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Obtener versión de Chrome instalada y descargar ChromeDriver compatible
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}' | cut -d. -f1-3) \
    && echo "Chrome version detected: $CHROME_VERSION" \
    && CHROMEDRIVER_VERSION=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_$CHROME_VERSION") \
    && echo "ChromeDriver version to install: $CHROMEDRIVER_VERSION" \
    && wget -q "https://storage.googleapis.com/chrome-for-testing-public/$CHROMEDRIVER_VERSION/linux64/chromedriver-linux64.zip" -O /tmp/chromedriver.zip \
    && unzip -q /tmp/chromedriver.zip -d /tmp/ \
    && mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && chmod +x /usr/local/bin/chromedriver \
    && rm -rf /tmp/chromedriver* \
    && chromedriver --version

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias primero (para cache de Docker)
COPY requirements.txt .

# Actualizar pip e instalar dependencias Python
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

# Crear directorios necesarios
RUN mkdir -p /app/downloads \
    && chown -R qauser:qauser /app

# Cambiar al usuario no-root
USER qauser

# Script de entrada para configurar entorno
COPY --chown=qauser:qauser docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Exponer puerto para posibles servicios web futuros
EXPOSE 8080

# Comando por defecto
ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]
CMD ["python", "test_runner.py"]

# ===============================================================================
# HEALTHCHECK para verificar que el contenedor está funcionando
# ===============================================================================
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import selenium; print('OK')" || exit 1
