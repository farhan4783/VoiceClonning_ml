# Build stage
FROM node:18-alpine as build

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=build /app/dist /usr/share/nginx/html

# Copy custom nginx config if we had one, but strict default is okay for now
# We might need to add a catch-all route for SPA later if not using HashRouter
# For now, simple serving of built assets.

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
