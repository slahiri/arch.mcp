FROM python:3.12-slim

WORKDIR /app

# Copy all files
COPY . .

# Install package
RUN pip install --no-cache-dir .

# Set environment variables
ENV MCP_TRANSPORT=http

# Expose port (Railway sets PORT dynamically)
EXPOSE 8000

# Run server
CMD ["arch-mcp"]
