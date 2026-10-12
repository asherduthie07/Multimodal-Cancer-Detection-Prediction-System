FROM node:22.16-alpine
WORKDIR /app
COPY apps/web/package*.json ./
RUN npm install
COPY apps/web ./
CMD ["npm", "start"]
