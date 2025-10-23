FROM node:20-alpine

# Create app directory
WORKDIR /app

# Copy package manifests first for better cache utilization
COPY package.json package-lock.json* yarn.lock* ./

# Install dependencies (prefer yarn if lockfile exists)
RUN if [ -f yarn.lock ]; then \
      yarn install --frozen-lockfile --production=false; \
    elif [ -f package-lock.json ]; then \
      npm ci; \
    else \
      npm install; \
    fi

# Copy source
COPY . .

# Build the production bundle
RUN npm run build

# Install a lightweight static server
RUN npm install -g serve

EXPOSE 5173

# Serve the production build
CMD ["serve", "-s", "dist", "-l", "5173"]
FROM node:18-slim
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . /app
CMD ["npm", "run", "dev"]
