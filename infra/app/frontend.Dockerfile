# Front-end (Vue 3 + Vite). O build vira arquivos estaticos servidos pelo nginx,
# que tambem repassa /api para o back. O codigo vem de src/frontend, baixado pelo deploy.sh.

FROM node:20-alpine AS build
WORKDIR /build
COPY src/frontend/package*.json ./
RUN npm ci
COPY src/frontend/ .
# Mesmo endereco do site: o nginx encaminha /api para o back, entao nao precisa de CORS.
ENV VITE_API_URL=/api/v1
RUN npm run build

FROM nginx:1.27-alpine
COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /build/dist /usr/share/nginx/html
EXPOSE 80
