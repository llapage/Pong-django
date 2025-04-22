FROM nginx:stable

RUN apt update -y && \
    apt upgrade -y && \
	apt install -y openssl

RUN mkdir -p /etc/nginx/ssl \
    mkdir -p /home/app/staticfiles

RUN openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/nginx.key \
    -out /etc/nginx/ssl/nginx.crt \
    -subj "/C=BE/ST=BXL/L=BXL/O=19/OU=student/CN=www.declerbo.42.fr"

COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80 443

CMD ["nginx", "-g", "daemon off;"]