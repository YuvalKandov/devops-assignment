# DevOps Intern Home Assignment

A containerized Nginx web server with automated testing and CI/CD pipeline.

## Project Overview

This project demonstrates:
- Custom Nginx Docker image built from Ubuntu 22.04
- Two server blocks: HTTPS with rate limiting, HTTP error response
- Self-signed SSL certificate for HTTPS
- Rate limiting for DDoS protection
- Automated testing with Python
- CI/CD pipeline with GitHub Actions

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Nginx Container                      │
│                                                         │
│  ┌─────────────────────────┐  ┌─────────────────────┐   │
│  │      Port 8443          │  │     Port 8081       │   │
│  │   HTTPS + HTML + SSL    │  │    HTTP 404 Error   │   │
│  │     Rate Limited        │  │                     │   │
│  └─────────────────────────┘  └─────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

### Server Blocks

| Port | Protocol | Response | Features |
|------|----------|----------|----------|
| 8443 | HTTPS | 200 OK + HTML | Self-signed SSL, Rate limiting (5 req/s) |
| 8081 | HTTP | 404 Not Found | Error response |

## Quick Start

### Prerequisites
- Docker
- Docker Compose

### Build and Run

```bash
# Build and run all containers (including tests)
docker compose up --build

# Run in detached mode (without tests)
docker compose up -d nginx

# Stop all containers
docker compose down
```

### Test Manually

```bash
# Test HTTPS success (ignore self-signed cert warning)
curl -k https://localhost:8443

# Test HTTP error
curl http://localhost:8081

# Test rate limiting (run multiple times quickly)
seq 20 | xargs -I {} curl -sk -o /dev/null -w "%{http_code}\n" https://localhost:8443
```

## Rate Limiting Configuration

Rate limiting is implemented using Nginx's `limit_req` module to protect against DDoS attacks.

### Current Settings

```nginx
limit_req_zone $binary_remote_addr zone=ratelimit:10m rate=5r/s;
limit_req zone=ratelimit burst=5 nodelay;
```

- **Rate**: 5 requests per second per IP address
- **Burst**: Allows 5 additional requests to be processed immediately
- **Memory**: 10MB shared zone (~160,000 unique IPs)
- **Response**: HTTP 429 Too Many Requests when exceeded

### Modifying Rate Limits

To change the rate limit threshold, edit `nginx/nginx.conf`:

```nginx
# Example: Increase to 10 requests/second with burst of 20
limit_req_zone $binary_remote_addr zone=ratelimit:10m rate=10r/s;
limit_req zone=ratelimit burst=20 nodelay;
```

Then rebuild the container:
```bash
docker compose build nginx
docker compose up -d nginx
```

## Testing

Tests are written in Python using only the standard library

### Test Cases

1. **HTTPS 200 Test**: Verifies port 8443 returns 200 OK with expected content
2. **HTTP 404 Test**: Verifies port 8081 returns 404 Not Found
3. **Rate Limiting Test**: Sends 30 concurrent requests, verifies some return 429

### Run Tests

```bash
# Run tests via Docker Compose
docker compose up --build tests

# Run tests locally (requires Python 3.11+)
NGINX_HOST=localhost python tests/test_nginx.py
```

## CI/CD Pipeline

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push and pull request to the `main` branch.

### Pipeline Steps

1. **Checkout**: Clone the repository
2. **Build and Test**: Run `docker compose up` with test container
3. **Create Artifact**: Generate `succeeded` or `fail` marker file
4. **Upload Artifact**: Store test results for download

### Viewing Results

After the workflow runs, check the Actions tab in GitHub for:
- Build logs
- Test output
- Downloadable artifacts (`test-result`)

## Project Structure

```
.
├── nginx/
│   ├── Dockerfile      # Nginx image based on Ubuntu
│   ├── nginx.conf      # Server configuration
│   └── index.html      # Default HTML page
├── tests/
│   ├── Dockerfile      # Python test image
│   └── test_nginx.py   # Test script
├── .github/
│   └── workflows/
│       └── ci.yml      # GitHub Actions workflow
├── docker-compose.yml  # Container orchestration
└── README.md           # This file
```

## Key Concepts Demonstrated

- **Docker**: Layer optimization, apt cleanup for smaller images
- **Nginx**: Multiple server blocks, SSL/TLS configuration, rate limiting
- **Container Orchestration**: Service dependencies, health checks
- **Testing**: Automated tests with proper assertions and exit codes
- **CI/CD**: GitHub Actions, artifacts, conditional logic
- **Security**: HTTPS encryption, rate limiting as DDoS mitigation
