FROM node:18-alpine

WORKDIR /app

# Install http-server globally
RUN npm install -g http-server

# Copy all frontend files
COPY . .

# Expose port (Azure uses port 80)
EXPOSE 80

# Start http-server
CMD ["http-server", "-p", "80", "-c-1"]
