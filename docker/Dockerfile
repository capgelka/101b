FROM nginx

ADD src /usr/share/nginx/html
ADD config /etc/nginx/conf.d/default.conf
ADD htpasswd /etc/nginx/conf.d/htpasswd

RUN rm /usr/share/nginx/html/index.html