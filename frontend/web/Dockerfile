# Build stage
FROM node:20-alpine AS frontend-builder

WORKDIR /app

# Accept build args for API URLs (needed at build time for Vite)
ARG VITE_CORE_ORBITS_URL
ARG VITE_ROUTING_URL
ARG VITE_GROUND_SCHEDULER_URL
ARG VITE_AI_AGENTS_URL

# Set them as environment variables for the build
ENV VITE_CORE_ORBITS_URL=${VITE_CORE_ORBITS_URL}
ENV VITE_ROUTING_URL=${VITE_ROUTING_URL}
ENV VITE_GROUND_SCHEDULER_URL=${VITE_GROUND_SCHEDULER_URL}
ENV VITE_AI_AGENTS_URL=${VITE_AI_AGENTS_URL}

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=frontend-builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
