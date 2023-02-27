server {
    listen {{NGINX_PORT}};
    server_name "localhost";
    
    # Маршрутизируем статические файлы
    location /static/ {
        alias /www/static/;
    }
    # Маршрутизируем все остальные запросы на сервер Django
    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://web_django:{{DJANGO_PORT}};
    }
}