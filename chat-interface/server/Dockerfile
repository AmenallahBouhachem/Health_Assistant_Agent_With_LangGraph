# Use official Node.js image as a base
FROM node:18

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy the rest of the backend's source code into the container
COPY . .

# Expose port 5000 for the backend API
EXPOSE 4000

# Run the backend application
CMD ["node", "server.js"]
