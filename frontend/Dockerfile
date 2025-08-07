# React 개발 서버용 Dockerfile
FROM node:20

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

ENV NODE_OPTIONS=--openssl-legacy-provider

EXPOSE 3000

CMD ["npm", "start"]
