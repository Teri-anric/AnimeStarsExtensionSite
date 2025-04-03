FROM nginx:latest

# Install Certbot
RUN apt-get update && apt-get install -y certbot python3-certbot-nginx

# Copy Nginx config
COPY default.conf /etc/nginx/conf.d/default.conf

# Create Certbot directories
RUN mkdir -p /var/www/certbot

# Add Certbot renewal script
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
