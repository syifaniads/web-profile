FROM nginxinc/nginx-unprivileged:alpine

COPY --chown=101:101 index.html /usr/share/nginx/html/index.html
COPY --chown=101:101 css/ /usr/share/nginx/html/css/

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -q --spider http://127.0.0.1:8080/ || exit 1
