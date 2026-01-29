FROM python:3.12-slim

WORKDIR /app

# Copy all files
COPY . .

# Install package
RUN pip install --no-cache-dir .

# Set environment variables
ENV MCP_TRANSPORT=http
ENV MCP_PORT=8000

# Expose port
EXPOSE 8000

# Run server
CMD ["arch-mcp"]
