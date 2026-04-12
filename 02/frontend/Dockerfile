FROM nginx:alpine

# Copiar archivos
COPY . /usr/share/nginx/html/

# Script para inyectar entorno en config.js antes de arrancar Nginx
RUN echo '#!/bin/sh' > /docker-entrypoint.d/40-envsubst-config.sh && \
    echo 'cat <<EOF > /usr/share/nginx/html/config.js' >> /docker-entrypoint.d/40-envsubst-config.sh && \
    echo 'window.APP_CONFIG = {' >> /docker-entrypoint.d/40-envsubst-config.sh && \
    echo '    API_URL: "${SERVER_URL:-http://localhost:5000}",' >> /docker-entrypoint.d/40-envsubst-config.sh && \
    echo '    API_TOKEN: "${API_TOKEN:-admin123}"' >> /docker-entrypoint.d/40-envsubst-config.sh && \
    echo '};' >> /docker-entrypoint.d/40-envsubst-config.sh && \
    echo 'EOF' >> /docker-entrypoint.d/40-envsubst-config.sh && \
    chmod +x /docker-entrypoint.d/40-envsubst-config.sh

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]