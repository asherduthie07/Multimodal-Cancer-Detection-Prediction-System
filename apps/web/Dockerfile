FROM node:22.16-alpine
WORKDIR /app
COPY apps/web/package*.json ./
RUN npm ci
COPY apps/web ./
CMD ["npx", "ng", "serve", "--host", "0.0.0.0", "--proxy-config", "proxy.compose.conf.json"]
