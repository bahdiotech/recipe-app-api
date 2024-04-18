#!/bin/sh

#waits for proxy to be available, then gets the first certificate.

set -e

until nc -z proxy 8-; do
    echo "Waiting for proxy to be available..."
    sleep 5s & wait ${!}
done

echo "Getting first certificate..."

certbot certonly \
   --webroot \
   --webroot-path "/vol/www/" \
   -d "$DOMAIN" \
   --email $EMAIL \
   --rsa-key-size 4096  \
   --agree-tos \
   --no-eff-email \
   --noninteractive \