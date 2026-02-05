FROM ubuntu:22.04

# Avoid interactive prompts during apt install
ENV DEBIAN_FRONTEND=noninteractive

# Install nginx, openssl (for HTTPS), and curl (for healthcheck), then clean up to reduce image size
RUN apt-get update && \
    apt-get install -y --no-install-recommends nginx openssl curl && \
    rm -rf /var/lib/apt/lists/*

# Generate self-signed SSL certificate
RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/ssl/private/nginx.key \
    -out /etc/ssl/certs/nginx.crt \
    -subj "/CN=localhost"

COPY nginx.conf /etc/nginx/nginx.conf
COPY index.html /var/www/html/index.html

EXPOSE 8443 8081

CMD ["nginx", "-g", "daemon off;"]
