FROM node:18-alpine

WORKDIR /app

COPY chat-interface/package*.json ./
RUN npm install

COPY chat-interface/ .
RUN npm run build

EXPOSE 3000
CMD ["npm", "run", "dev", "--", "--host"]
