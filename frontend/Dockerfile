FROM node:18-alpine AS builder
WORKDIR /app
RUN npm install -g http-server
COPY . .
EXPOSE 3000
CMD ["http-server", "-p", "3000", "-c-1"]
