#!/bin/sh

set -e

echo 'Checking for dhparams.pem'
if [ !  -f "/vol/proxy/ssl-dhparams.pem"]; then 
    echo "dhpatams.pem does not exist - creating it manually"
    openssl dhparam -out /vol/proxyssl-dhparams.pem 2048
fi 

# envsubst < /etc/nginx/default.conf.tpl > /etc/nginx/conf.d/default.conf
# nginx -g 'daemon off;'

# Avoid replacing these with envsubst

export host=\$host
export  request_uri=\$request_uri

echo 'Checking for fullchain.pem'
if [ !  -f "/etc/letsencrypt/live/${DOMAIN}/fullchain.pem"]; then
    echo "No SSL cert, enabling HTTP only..."
    envsubst < /etc/nginx/default.conf.tpl > /etc/nginx/conf.d/default.conf
else
    echo "SSL cert exists, enabling HTTPS..."
    envsubst < /etc/nginx/default-ssl.conf.tpl > /etc/nginx/conf.d/default.conf
fi

nginx -g 'daemon off;'