# Backend Dockerfile for Node.js service - Optimized multi-stage build

FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (production only)
RUN npm ci --omit=dev --ignore-scripts && \
    npm cache clean --force

# Production stage
FROM node:18-alpine

WORKDIR /app

# Copy only node_modules from builder
COPY --from=builder /app/node_modules ./node_modules

# Copy only necessary application files (exclude tests, docs, etc.)
COPY package.json ./
COPY app.js ./
COPY resume.js ./
COPY config/ ./config/
COPY services/ ./services/
COPY utils/ ./utils/
COPY middleware/ ./middleware/

# Create uploads directory
RUN mkdir -p uploads

# Create non-root user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 && \
    chown -R nodejs:nodejs /app

USER nodejs

# Expose port
EXPOSE 3001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
  CMD node -e "require('http').get('http://localhost:3001/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Start application
CMD ["node", "app.js"]