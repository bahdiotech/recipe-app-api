FROM nginx:1.23.0-alpine
LABEL maintainer='bardiotech-portfolio.netlify.app'

COPY ./nginx/* /etc/nginx/
COPY ./run.sh /run.sh
# COPY ./default.conf.tpl /etc/nginx/default.conf.tpl
# COPY ./uwsgi_params /etc/nginx/uwsgi_params
# COPY ./run.sh /run.sh

ENV LISTEN_PORT=8000
ENV APP_HOST=app
ENV APP_PORT=9000

RUN apk add --no-cache openssl bash
RUN chmod +x /run.sh

USER root

# RUN mkdir -p /vol/static && \
#     chmod 755 /vol/static && \
#     touch /etc/nginx/conf.d/default.conf && \
#     chown nginx:nginx /etc/nginx/conf.d/default.conf && \
#     chmod +x /run.sh

VOLUME /vol/static
VOLUME /vol/www

# USER nginx

CMD [ "/run.sh" ]