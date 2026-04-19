FROM node:22-alpine

WORKDIR /opt/client/

COPY package*.json ./
RUN npm install

COPY . .

# Expose port 3000 to match docker-compose
EXPOSE 3000

# Run vite with --host so it's accessible from outside container
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "3000"]
