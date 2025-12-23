# MixMaster Pro - Frontend Dockerfile
# For backend, create a separate Railway service with root directory set to /backend

FROM node:20-alpine AS builder

WORKDIR /app

# Build argument for API URL (passed from Railway)
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Copy frontend files
COPY frontend/package*.json ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY frontend/ .

# Build with environment variable
RUN npm run build

# Production
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000

COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

# Copy public folder if it exists (use wildcard to make it optional)
COPY --from=builder /app/public* ./public/

EXPOSE 3000

CMD ["node", "server.js"]
