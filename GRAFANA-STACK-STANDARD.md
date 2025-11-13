# Grafana Stack Standardization Guide

This guide documents the exact approach, patterns, and structure used to add a complete Grafana monitoring stack (Prometheus, Grafana, Loki, Promtail) to any project. This standardization ensures consistent monitoring setup across all projects.

## Table of Contents

- [Overview & Prerequisites](#overview--prerequisites)
- [Step-by-Step Implementation Checklist](#step-by-step-implementation-checklist)
- [Code Patterns & Conventions](#code-patterns--conventions)
- [Configuration File Templates](#configuration-file-templates)
- [Docker Compose Patterns](#docker-compose-patterns)
- [File Organization Standards](#file-organization-standards)
- [Quick Reference Checklist](#quick-reference-checklist)

---

## Overview & Prerequisites

### Stack Components

The monitoring stack consists of four components:

1. **Prometheus** - Metrics collection and storage
2. **Grafana** - Visualization and dashboards
3. **Loki** - Log aggregation system
4. **Promtail** - Log shipper (collects logs from containers)

### Architecture Flow

```
Application
    │
    ├─── Metrics ────► Prometheus ────► Grafana (Dashboards)
    │
    └─── Logs ───────► Promtail ──────► Loki ──────► Grafana (Logs)
```

### Requirements

- Docker and Docker Compose installed
- Application running in Docker containers
- Application can expose a `/metrics` endpoint
- Application logs accessible via Docker logs

### Standard Directory Structure

All monitoring configurations must be placed in a `monitoring/` directory at the project root:

```
project-root/
├── monitoring/
│   ├── prometheus.yml
│   ├── loki-config.yml
│   ├── promtail-config.yml
│   └── grafana/
│       ├── provisioning/
│       │   ├── datasources/
│       │   │   └── prometheus.yml
│       │   └── dashboards/
│       │       └── dashboard.yml
│       └── dashboards/
│           └── (dashboard JSON files)
```

---

## Step-by-Step Implementation Checklist

### Step 1: Add Dependencies

Add Prometheus client library to your project's dependency file.

**Python (requirements.txt or pyproject.toml):**
```txt
prometheus-client>=0.19.0
```

**Node.js (package.json):**
```json
{
  "dependencies": {
    "prom-client": "^15.0.0"
  }
}
```

**Go (go.mod):**
```go
require github.com/prometheus/client_golang v1.19.0
```

### Step 2: Instrument Application Code

Add metrics instrumentation to your application. See [Code Patterns & Conventions](#code-patterns--conventions) section for framework-specific examples.

**Key Requirements:**
- Expose a `/metrics` endpoint
- Collect HTTP request metrics (total requests, duration, status codes)
- Add business-specific metrics as needed

### Step 3: Create Monitoring Directory Structure

Create the standard directory structure:

```bash
mkdir -p monitoring/grafana/{provisioning/{datasources,dashboards},dashboards}
```

### Step 4: Create Configuration Files

Create the following configuration files using the exact templates provided in [Configuration File Templates](#configuration-file-templates):

1. `monitoring/prometheus.yml`
2. `monitoring/loki-config.yml`
3. `monitoring/promtail-config.yml`
4. `monitoring/grafana/provisioning/datasources/prometheus.yml`
5. `monitoring/grafana/provisioning/dashboards/dashboard.yml`

**Important:** Replace `your-service-name` and `your-service-port` with your actual service name and port in `prometheus.yml`.

### Step 5: Update docker-compose.yml

Add the monitoring services to your `docker-compose.yml`. See [Docker Compose Patterns](#docker-compose-patterns) section for the exact service definitions.

**Key Points:**
- All services must be on the same `monitoring` network
- Your application service must have `logging: "true"` label
- Use service names (not localhost) for inter-service communication

### Step 6: Add Dashboards (Optional)

Create Grafana dashboard JSON files and place them in `monitoring/grafana/dashboards/`. They will be automatically loaded by Grafana.

### Step 7: Verify Setup

1. Start services: `docker-compose up -d`
2. Verify Prometheus: http://localhost:9090
3. Verify Grafana: http://localhost:3000 (admin/admin)
4. Check metrics endpoint: http://localhost:YOUR_PORT/metrics
5. Verify logs appear in Grafana

---

## Code Patterns & Conventions

### Metrics Instrumentation Pattern

The standard pattern includes:
- **HTTP Request Counter**: Total requests by method, endpoint, status
- **HTTP Request Duration Histogram**: Request duration by method, endpoint
- **Business Metrics**: Application-specific counters/gauges

### Naming Conventions

Follow Prometheus naming conventions:
- Use `_total` suffix for counters
- Use `_seconds`, `_bytes`, etc. for units
- Use lowercase with underscores
- Include metric type in name when helpful

**Examples:**
- `http_requests_total`
- `http_request_duration_seconds`
- `your_feature_requests_total`

### Framework-Specific Examples

#### Python/FastAPI

```python
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import time

# Define metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'endpoint']
)

# Middleware
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    endpoint = request.url.path
    # Simplify endpoint for metrics (remove variable parts)
    if endpoint.startswith("/api/stats/"):
        endpoint = "/api/stats/{code}"
    
    http_requests_total.labels(
        method=request.method,
        endpoint=endpoint,
        status=response.status_code
    ).inc()
    
    http_request_duration_seconds.labels(
        method=request.method,
        endpoint=endpoint
    ).observe(duration)
    
    return response

# Metrics endpoint
@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
```

#### Node.js/Express

```javascript
const promClient = require('prom-client');
const express = require('express');

// Create metrics registry
const register = new promClient.Registry();

// Define metrics
const httpRequestsTotal = new promClient.Counter({
  name: 'http_requests_total',
  help: 'Total HTTP requests',
  labelNames: ['method', 'endpoint', 'status'],
  registers: [register]
});

const httpRequestDuration = new promClient.Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request duration in seconds',
  labelNames: ['method', 'endpoint'],
  registers: [register]
});

// Middleware
app.use((req, res, next) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    const endpoint = req.route ? req.route.path : req.path;
    
    httpRequestsTotal.inc({
      method: req.method,
      endpoint: endpoint,
      status: res.statusCode
    });
    
    httpRequestDuration.observe({
      method: req.method,
      endpoint: endpoint
    }, duration);
  });
  
  next();
});

// Metrics endpoint
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});
```

#### Go/Gin

```go
package main

import (
    "github.com/gin-gonic/gin"
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promhttp"
    "time"
)

var (
    httpRequestsTotal = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "http_requests_total",
            Help: "Total HTTP requests",
        },
        []string{"method", "endpoint", "status"},
    )
    
    httpRequestDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name: "http_request_duration_seconds",
            Help: "HTTP request duration in seconds",
        },
        []string{"method", "endpoint"},
    )
)

func init() {
    prometheus.MustRegister(httpRequestsTotal)
    prometheus.MustRegister(httpRequestDuration)
}

func metricsMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        
        c.Next()
        
        duration := time.Since(start).Seconds()
        endpoint := c.FullPath()
        if endpoint == "" {
            endpoint = c.Request.URL.Path
        }
        
        httpRequestsTotal.WithLabelValues(
            c.Request.Method,
            endpoint,
            fmt.Sprintf("%d", c.Writer.Status()),
        ).Inc()
        
        httpRequestDuration.WithLabelValues(
            c.Request.Method,
            endpoint,
        ).Observe(duration)
    }
}

func main() {
    r := gin.Default()
    r.Use(metricsMiddleware())
    
    // Metrics endpoint
    r.GET("/metrics", gin.WrapH(promhttp.Handler()))
    
    // Your routes...
    r.Run()
}
```

### Business Metrics Pattern

Add application-specific metrics in your business logic:

```python
# Example: Track feature usage
feature_requests = Counter(
    'feature_requests_total',
    'Total feature requests',
    ['feature_name']
)

# In your endpoint
feature_requests.labels(feature_name='url_shorten').inc()
```

---

## Configuration File Templates

### 1. monitoring/prometheus.yml

**Exact Template:**

```yaml
# Prometheus Configuration
# This file tells Prometheus which services to scrape for metrics
# SRE Note: Add more scrape_configs entries to monitor additional services

global:
  # How often Prometheus scrapes metrics from targets
  # Lower = more frequent updates but more load
  scrape_interval: 15s
  
  # How often to evaluate alerting rules (if you add alerts later)
  evaluation_interval: 15s

# Scrape configurations define which services Prometheus should monitor
scrape_configs:
  # Job for your application
  - job_name: 'your-service-name'  # Name shown in Prometheus UI
    static_configs:
      # Target: service name from docker-compose.yml : port
      # Use service name (not localhost) because containers communicate via Docker network
      - targets: ['your-service-name:your-port']
    # The endpoint where metrics are exposed (defined in your application)
    metrics_path: '/metrics'
    
  # SRE: To add more services, copy the above block and modify:
  # - job_name: 'your-service-name'
  #   static_configs:
  #     - targets: ['your-service:port']
  #   metrics_path: '/metrics'  # or whatever endpoint your service uses
```

**Customization:**
- Replace `your-service-name` with your actual service name
- Replace `your-port` with your actual port
- Add more `scrape_configs` entries for additional services

### 2. monitoring/loki-config.yml

**Exact Template:**

```yaml
# Loki Configuration - Log Aggregation System
# Loki stores logs in a time-series format similar to Prometheus
# SRE Note: Adjust retention and storage settings based on your needs

# Authentication disabled for local development
# SRE: Enable auth in production using auth_enabled: true
auth_enabled: false

server:
  # HTTP API port (Grafana connects here)
  http_listen_port: 3100
  # gRPC port for internal communication
  grpc_listen_port: 9096

common:
  # Base path for Loki data storage
  path_prefix: /loki
  storage:
    filesystem:
      # Where log chunks are stored (persisted in Docker volume)
      chunks_directory: /loki/chunks
      # Where alerting rules are stored (if you add rules later)
      rules_directory: /loki/rules
  # Replication factor (1 = single instance, increase for HA)
  replication_factor: 1
  ring:
    instance_addr: 127.0.0.1
    # Key-value store for ring (inmemory = single instance)
    kvstore:
      store: inmemory

limits_config:
  # Disable structured metadata for compatibility with older schema
  allow_structured_metadata: false
  # Enable log volume visualization in Grafana (required for drilldown feature)
  volume_enabled: true
  # SRE: Add retention settings here:
  # max_query_length: 720h  # Maximum query range (30 days)
  # retention_period: 720h  # How long to keep logs

schema_config:
  # Schema defines how logs are indexed and stored
  configs:
    - from: 2020-10-24  # Start date for this schema
      # Storage backend: boltdb-shipper (simple file-based storage)
      # SRE: For production, consider tsdb or object storage (S3, GCS)
      store: boltdb-shipper
      object_store: filesystem
      schema: v11  # Schema version
      index:
        prefix: index_  # Prefix for index files
        period: 24h  # How often to create new index files
```

**Customization:**
- Adjust `retention_period` for log retention
- Change storage backend for production (S3, GCS, etc.)

### 3. monitoring/promtail-config.yml

**Exact Template:**

```yaml
# Promtail Configuration - Log Shipper
# Promtail collects logs from Docker containers and sends them to Loki
# SRE Note: This uses Docker service discovery to automatically find containers

server:
  # HTTP server port for Promtail metrics/health
  http_listen_port: 9080
  # gRPC port (0 = disabled)
  grpc_listen_port: 0

# Position file tracks where Promtail left off reading logs
# Prevents re-reading logs after restart
positions:
  filename: /tmp/positions.yaml

# Where to send logs (Loki push API endpoint)
clients:
  - url: http://loki:3100/loki/api/v1/push  # Service name from docker-compose.yml

# Scrape configurations define which logs to collect
scrape_configs:
  - job_name: docker
    # Docker service discovery - automatically finds containers
    docker_sd_configs:
      - host: unix:///var/run/docker.sock  # Docker socket (mounted in docker-compose.yml)
        refresh_interval: 5s  # How often to check for new containers
        # SRE: Only collect logs from containers with this label
        # Add "logging: true" label to services in docker-compose.yml to enable log collection
        filters:
          - name: label
            values: ["logging=true"]
    
    # Relabel configs add useful labels to logs for filtering/querying
    relabel_configs:
      # Extract container name (removes leading /)
      - source_labels: ['__meta_docker_container_name']
        regex: '/(.*)'
        target_label: 'container'  # Use this label in LogQL: {container="your-service"}
      
      # Add log stream (stdout/stderr)
      - source_labels: ['__meta_docker_container_log_stream']
        target_label: 'logstream'
      
      # Add container ID
      - source_labels: ['__meta_docker_container_id']
        target_label: 'container_id'
    
    # Pipeline stages process log lines before sending to Loki
    pipeline_stages:
      # Parse JSON log format from Docker
      - json:
          expressions:
            output: log      # The actual log message
            stream: stream   # stdout or stderr
            attrs: attrs     # Docker attributes
      
      # Extract tag from attributes
      - json:
          expressions:
            tag: attrs.tag
          source: attrs
      
      # Parse Docker tag format (optional, for additional metadata)
      - regex:
          expression: (?P<container_name>(?:[^|]*))\|(?P<image_name>(?:[^|]*))\|(?P<image_id>(?:[^|]*))\|(?P<container_id>(?:[^|]*))
          source: tag
      
      # Parse timestamp
      - timestamp:
          format: RFC3339Nano
          source: time
      
      # Add labels for filtering
      - labels:
          stream:      # stdout/stderr
          container:   # Container name
      
      # Output the log line
      - output:
          source: output
      
      # SRE: Add more pipeline stages here for:
      # - Log filtering (drop certain logs)
      # - Log parsing (extract structured data)
      # - Label extraction (add custom labels from log content)
```

**Customization:**
- Modify pipeline stages for custom log parsing
- Add filters to exclude certain logs

### 4. monitoring/grafana/provisioning/datasources/prometheus.yml

**Exact Template:**

```yaml
# Grafana Datasource Provisioning
# This file automatically configures datasources when Grafana starts
# SRE Note: Datasources appear automatically - no need to configure in UI

apiVersion: 1

datasources:
  # Prometheus datasource for metrics
  - name: Prometheus
    type: prometheus
    access: proxy  # Grafana proxies requests to Prometheus
    # Use service name from docker-compose.yml (not localhost)
    url: http://prometheus:9090
    isDefault: true  # Default datasource for new panels
    editable: true  # Allow editing in UI (set false to lock config)
  
  # Loki datasource for logs
  - name: Loki
    type: loki
    access: proxy
    url: http://loki:3100  # Service name from docker-compose.yml
    editable: true
    jsonData:
      maxLines: 1000  # Maximum log lines to fetch per query
      # SRE: Add more Loki-specific settings here:
      # derivedFields:  # Add links to other systems (e.g., trace IDs)
      #   - datasourceUid: "jaeger"
      #     matcherRegex: "traceID=(\\w+)"
      #     name: "TraceID"
      #     url: "$${__value.raw}"
  
  # SRE: To add more datasources (e.g., Elasticsearch, InfluxDB, etc.):
  # - name: YourDatasource
  #   type: your_type
  #   url: http://your-service:port
  #   access: proxy
```

**Customization:**
- Add more datasources as needed
- Configure derived fields for trace linking

### 5. monitoring/grafana/provisioning/dashboards/dashboard.yml

**Exact Template:**

```yaml
# Grafana Dashboard Provisioning
# This file tells Grafana where to find dashboard JSON files
# SRE Note: Dashboards in grafana/dashboards/ are automatically loaded

apiVersion: 1

providers:
  - name: 'default'  # Provider name (can have multiple providers)
    orgId: 1  # Organization ID (1 = default)
    folder: ''  # Folder name (empty = root, or specify folder name)
    type: file  # Load from filesystem
    disableDeletion: false  # Allow deleting dashboards from UI
    updateIntervalSeconds: 10  # How often to check for new/updated dashboards
    allowUiUpdates: true  # Allow editing dashboards in UI (set false to lock)
    options:
      # Path in container (mapped from grafana/dashboards/ in docker-compose.yml)
      path: /etc/grafana/provisioning/dashboards
      # Create folders based on directory structure
      foldersFromFilesStructure: true
      
  # SRE: To add more dashboard sources:
  # - name: 'custom-dashboards'
  #   orgId: 1
  #   folder: 'Custom'
  #   type: file
  #   options:
  #     path: /etc/grafana/custom-dashboards
```

**Customization:**
- Add more providers for different dashboard folders
- Configure folder structure

---

## Docker Compose Patterns

### Standard Service Definitions

Add these services to your `docker-compose.yml`:

```yaml
version: '3.8'

# ============================================================================
# DOCKER COMPOSE CONFIGURATION - YOUR APPLICATION WITH MONITORING
# ============================================================================
# This file defines all services for your application including
# the application itself and the complete monitoring stack (Prometheus, Grafana, Loki).
#
# SRE Notes:
# - All services are on the 'monitoring' network for inter-service communication
# - Volumes persist data across container restarts
# - Health checks ensure services are running correctly
# - Logging labels enable Promtail to discover and collect logs
# ============================================================================

services:
  # --------------------------------------------------------------------------
  # YOUR APPLICATION
  # --------------------------------------------------------------------------
  your-service:
    build: .  # or use image: your-image
    container_name: your-service
    ports:
      - "YOUR_PORT:YOUR_PORT"  # Expose your application port
    environment:
      - YOUR_ENV_VARS=values
    volumes:
      - ./your-data:/app/data  # Your application data
    restart: unless-stopped
    logging:
      driver: "json-file"  # Docker's JSON log driver
      options:
        max-size: "10m"  # Rotate logs when they reach 10MB
        max-file: "3"    # Keep 3 rotated log files
        labels: "service,environment"  # Add labels for log filtering
    healthcheck:
      # Health check: customize for your application
      test: ["CMD", "curl", "-f", "http://localhost:YOUR_PORT/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
    networks:
      - monitoring  # Connect to monitoring network
    labels:
      logging: "true"  # SRE: This label tells Promtail to collect logs from this container
      # Add more labels here for filtering: environment: "production", team: "platform"

  # --------------------------------------------------------------------------
  # PROMETHEUS - METRICS COLLECTION
  # --------------------------------------------------------------------------
  # Prometheus scrapes metrics from the application's /metrics endpoint
  # Stores time-series data for querying and alerting
  # SRE: Access Prometheus UI at http://localhost:9090
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    ports:
      - "9090:9090"  # Prometheus web UI and API
    volumes:
      # Mount Prometheus config file (defines what to scrape)
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
      # Persistent volume for metrics storage (survives container restarts)
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'  # Config file location
      - '--storage.tsdb.path=/prometheus'              # Where to store metrics
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
    restart: unless-stopped
    networks:
      - monitoring  # Can reach your-service:port to scrape metrics
    # SRE: To add more scrape targets, edit monitoring/prometheus.yml

  # --------------------------------------------------------------------------
  # LOKI - LOG AGGREGATION
  # --------------------------------------------------------------------------
  # Loki stores logs in a time-series format (similar to Prometheus for metrics)
  # Receives logs from Promtail and makes them queryable via LogQL
  # SRE: Access Loki API at http://localhost:3100 (usually accessed via Grafana)
  loki:
    image: grafana/loki:latest
    container_name: loki
    ports:
      - "3100:3100"  # Loki HTTP API port
    volumes:
      # Mount Loki configuration file
      - ./monitoring/loki-config.yml:/etc/loki/local-config.yaml
      # Persistent volume for log storage
      - loki_data:/loki
    command: 
      - -config.file=/etc/loki/local-config.yaml
      - -validation.allow-structured-metadata=false  # Compatibility flag
    restart: unless-stopped
    networks:
      - monitoring  # Receives logs from Promtail on this network
    # SRE: Log retention and storage settings in monitoring/loki-config.yml

  # --------------------------------------------------------------------------
  # PROMTAIL - LOG SHIPPER
  # --------------------------------------------------------------------------
  # Promtail collects logs from Docker containers and sends them to Loki
  # Uses Docker service discovery to automatically find containers with logging=true label
  # SRE: Promtail runs as a daemon, no direct access needed (logs go to Loki)
  promtail:
    image: grafana/promtail:latest
    container_name: promtail
    volumes:
      # Promtail configuration
      - ./monitoring/promtail-config.yml:/etc/promtail/config.yml
      # Docker log directory (read-only access to container logs)
      - /var/lib/docker/containers:/var/lib/docker/containers:ro
      # Docker socket for service discovery (finds containers automatically)
      - /var/run/docker.sock:/var/run/docker.sock
    command: -config.file=/etc/promtail/config.yml
    restart: unless-stopped
    depends_on:
      - loki  # Wait for Loki to be ready before starting
    networks:
      - monitoring  # Sends logs to loki:3100
    # SRE: To collect logs from more containers, add "logging: true" label to their service

  # --------------------------------------------------------------------------
  # GRAFANA - VISUALIZATION & DASHBOARDS
  # --------------------------------------------------------------------------
  # Grafana provides dashboards for visualizing metrics (from Prometheus) and logs (from Loki)
  # Auto-provisions datasources and dashboards on startup
  # SRE: Access Grafana at http://localhost:3000 (admin/admin)
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    ports:
      - "3000:3000"  # Grafana web UI
    environment:
      - GF_SECURITY_ADMIN_USER=admin      # Default admin username
      - GF_SECURITY_ADMIN_PASSWORD=admin  # SRE: CHANGE THIS IN PRODUCTION!
      - GF_USERS_ALLOW_SIGN_UP=false      # Disable user self-registration
    volumes:
      # Persistent volume for Grafana data (dashboards, users, etc.)
      - grafana_data:/var/lib/grafana
      # Auto-provisioned datasources (Prometheus, Loki)
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
      # Auto-loaded dashboards (JSON files)
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
    restart: unless-stopped
    depends_on:
      - prometheus  # Wait for Prometheus to be ready
      - loki        # Wait for Loki to be ready
    networks:
      - monitoring  # Can reach prometheus:9090 and loki:3100
    # SRE: To add new dashboards, place JSON files in monitoring/grafana/dashboards/
    # SRE: To add new datasources, edit monitoring/grafana/provisioning/datasources/

# ============================================================================
# VOLUMES - PERSISTENT DATA STORAGE
# ============================================================================
# Volumes persist data across container restarts and deletions
# SRE: Data is stored in Docker volumes (use 'docker volume ls' to see them)
volumes:
  prometheus_data:  # Prometheus metrics storage
  grafana_data:     # Grafana dashboards, users, settings
  loki_data:        # Loki log storage
  # SRE: To backup volumes: docker run --rm -v volume_name:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz /data
  # SRE: To remove volumes: docker-compose down -v (⚠️ deletes all data!)

# ============================================================================
# NETWORKS - SERVICE COMMUNICATION
# ============================================================================
# All services on the same network can communicate using service names
# SRE: Services can reach each other by name (e.g., prometheus:9090, loki:3100)
networks:
  monitoring:
    driver: bridge  # Standard Docker bridge network
    # SRE: To add external networks or custom config, add:
    # external: true
    # name: custom_network_name
```

### Key Points

1. **Service Names**: Use service names (not localhost) for inter-service communication
2. **Network**: All services must be on the `monitoring` network
3. **Logging Label**: Application services must have `logging: "true"` label
4. **Volumes**: Use named volumes for persistent data
5. **Health Checks**: Add health checks to all services

---

## File Organization Standards

### Directory Structure

```
project-root/
├── monitoring/                    # All monitoring configs here
│   ├── prometheus.yml           # Prometheus configuration
│   ├── loki-config.yml          # Loki configuration
│   ├── promtail-config.yml      # Promtail configuration
│   └── grafana/
│       ├── provisioning/
│       │   ├── datasources/
│       │   │   └── prometheus.yml  # Datasource provisioning
│       │   └── dashboards/
│       │       └── dashboard.yml   # Dashboard provisioning
│       └── dashboards/
│           └── *.json            # Dashboard JSON files
├── docker-compose.yml            # Includes monitoring services
└── (your application files)
```

### Naming Conventions

- **Directory**: Always use `monitoring/` (lowercase, singular)
- **Config Files**: Use descriptive names with hyphens (`prometheus.yml`, `loki-config.yml`)
- **Service Names**: Use kebab-case in docker-compose.yml
- **Metrics**: Use snake_case with units (`http_requests_total`, `request_duration_seconds`)

### File Locations

- **Prometheus Config**: `monitoring/prometheus.yml`
- **Loki Config**: `monitoring/loki-config.yml`
- **Promtail Config**: `monitoring/promtail-config.yml`
- **Grafana Provisioning**: `monitoring/grafana/provisioning/`
- **Dashboards**: `monitoring/grafana/dashboards/`

---

## Quick Reference Checklist

### Initial Setup

- [ ] Add Prometheus client library to dependencies
- [ ] Instrument application with metrics (HTTP + business metrics)
- [ ] Create `/metrics` endpoint
- [ ] Create `monitoring/` directory structure
- [ ] Create all 5 configuration files using templates
- [ ] Update `docker-compose.yml` with monitoring services
- [ ] Add `logging: "true"` label to application service
- [ ] Add application service to `monitoring` network
- [ ] Update `prometheus.yml` with your service name and port

### Verification

- [ ] Start services: `docker-compose up -d`
- [ ] Check Prometheus: http://localhost:9090/targets (should show your service as UP)
- [ ] Check metrics endpoint: http://localhost:YOUR_PORT/metrics (should return metrics)
- [ ] Check Grafana: http://localhost:3000 (login with admin/admin)
- [ ] Verify datasources in Grafana (Prometheus and Loki should appear)
- [ ] Check logs in Grafana (Explore → Loki → query: `{container="your-service"}`)

### Common Customizations

- [ ] Add more scrape targets in `prometheus.yml`
- [ ] Add business metrics to application code
- [ ] Create custom dashboards in `monitoring/grafana/dashboards/`
- [ ] Configure log retention in `loki-config.yml`
- [ ] Add more datasources in Grafana provisioning
- [ ] Customize health checks in docker-compose.yml

### Production Checklist

- [ ] Change Grafana default password
- [ ] Enable authentication in Loki
- [ ] Configure log retention policies
- [ ] Set up backup strategy for volumes
- [ ] Add resource limits to services
- [ ] Configure alerting rules (optional)
- [ ] Set up TLS/HTTPS (optional)
- [ ] Review and adjust scrape intervals

---

## Best Practices

1. **Consistency**: Always use the same directory structure (`monitoring/`)
2. **Comments**: Keep SRE-friendly comments in all config files
3. **Service Names**: Use service names (not localhost) in configs
4. **Labels**: Use consistent labeling for logs and metrics
5. **Version Control**: Commit all monitoring configs to version control
6. **Documentation**: Document any custom metrics or dashboards
7. **Testing**: Test monitoring setup in development before production

---

## Troubleshooting

### Metrics Not Appearing

1. Check Prometheus targets: http://localhost:9090/targets
2. Verify `/metrics` endpoint is accessible
3. Check service name and port in `prometheus.yml`
4. Ensure services are on the same network

### Logs Not Appearing

1. Verify `logging: "true"` label on application service
2. Check Promtail logs: `docker-compose logs promtail`
3. Verify Loki is running: `docker-compose ps loki`
4. Check LogQL query in Grafana: `{container="your-service"}`

### Grafana Not Loading Dashboards

1. Check dashboard provisioning config
2. Verify dashboard JSON files are valid
3. Check Grafana logs: `docker-compose logs grafana`
4. Ensure dashboard path is correct in docker-compose.yml

---

## Summary

This standardization guide ensures consistent monitoring setup across all projects. By following these patterns and using the exact templates provided, you can quickly add a production-ready Grafana monitoring stack to any project.

**Key Takeaways:**
- Use `monitoring/` directory for all configs
- Follow exact template structure
- Use service names (not localhost) for communication
- Add `logging: "true"` label to application services
- Keep SRE-friendly comments in all configs
- Test in development before production

---

**Last Updated**: Based on production-tested patterns from URL Shortening Service project.

