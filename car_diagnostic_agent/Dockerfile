FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install uv
RUN pip install uv

# Install project dependencies
RUN uv sync

# Expose port
EXPOSE 10011

# Environment variable for Google API key
ENV GOOGLE_API_KEY=AIzaSyBk6Yy9SsWBTmhdH3mK6MG3gOxMsY0b63o

# Run the application
CMD ["uv", "run", "python", "-m", "app"]