server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN}
    
    location /static {
        alias /vol/static;
    }

    location / .well-known/acme-challenge/ {
        root /vol/www/;
        
    }

    location / {
        return 301 https//$host$request_url;
    }
} 

server {
    listen 443 ssl http2;
    server_name ${DOMAIN} www.${DOMAIN};

    ssl_certificate /etc/letsencrypt/live/${DOMAUN}/fullchain.pem
    ssl_certificate_key /etc/letsencrypt/live/${DOMAUN}/privkey.pem;

    include /etc/nginx/options-ssl-nginx.conf;

    ssl_dhparam /vol/proxy/ssl-dhparams.pem;

    add_header strict-transport-security "max-age=31536000; includeSubDomains" always;

    location /static {
        alias /vol/static;
    }

    location / {
           uwsgi_pass  ${APP_HOST}:${APP_PORT};
            include     /etc/nginx/uwsgi_params;
            client_max_body_size 10M;
    }
}