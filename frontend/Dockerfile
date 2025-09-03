# Build stage
FROM node:20-alpine AS build
WORKDIR /app
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
RUN npm ci || npm install
COPY . .
RUN npm run build

# Runtime stage (serve with vite preview)
FROM node:20-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
COPY --from=build /app .
EXPOSE 5173
CMD ["npm", "run", "preview"]

# Development stage (Vite dev server with HMR)
FROM node:20-alpine AS dev
WORKDIR /app
ENV NODE_ENV=development
COPY package.json package-lock.json* pnpm-lock.yaml* yarn.lock* ./
RUN npm ci || npm install
# Copy the rest of the source; will be overlaid by bind mount in docker-compose during dev
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0", "--port", "5173"]
