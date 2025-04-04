# Use official Node.js image as a base
FROM node:18

# Set the working directory in the container
WORKDIR /app

# Copy package.json and package-lock.json
COPY package.json package-lock.json ./

# Install dependencies
RUN npm install

# Copy the rest of the frontend source code into the container
COPY . .

# Build the React app for production
RUN npm run build

# Install a lightweight static server for production
RUN npm install -g serve

# Expose port 3000 for the React app
EXPOSE 3000

# Serve the React app
CMD ["serve", "-s", "dist"]
