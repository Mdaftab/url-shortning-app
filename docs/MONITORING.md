# Monitoring & Observability Guide

This document explains how the URL Shortening Service is instrumented for monitoring using Prometheus, Grafana, and Loki. This guide is designed for SREs who are new to Grafana and want to understand and extend the monitoring stack.

## Table of Contents

- [Overview](#overview)
- [Monitoring Stack Components](#monitoring-stack-components)
- [Application Instrumentation](#application-instrumentation)
- [Configuration Files](#configuration-files)
- [Adding Custom Metrics](#adding-custom-metrics)
- [Adding Custom Dashboards](#adding-custom-dashboards)
- [Troubleshooting](#troubleshooting)

## Overview

The application uses a complete observability stack:

- **Prometheus**: Metrics collection and storage
- **Grafana**: Visualization and dashboards
- **Loki**: Log aggregation
- **Promtail**: Log shipper (collects logs from containers)

### Architecture Flow

```
Application (FastAPI)
    │
    ├─── Metrics ────► Prometheus ────► Grafana (Dashboards)
    │
    └─── Logs ───────► Promtail ──────► Loki ──────► Grafana (Logs)
```

## Monitoring Stack Components

### 1. Prometheus

**Purpose**: Collects and stores time-series metrics from the application.

**Port**: 9090

**Access**: http://localhost:9090

**Key Features**:
- Scrapes metrics from `/metrics` endpoint every 15 seconds
- Stores metrics in time-series database
- Provides query language (PromQL) for metrics analysis

**Configuration**: `prometheus.yml`

### 2. Grafana

**Purpose**: Visualization platform for metrics and logs.

**Port**: 3000

**Access**: http://localhost:3000

**Default Credentials**:
- Username: `admin`
- Password: `admin`

**Key Features**:
- Pre-configured dashboards
- Auto-provisioned datasources (Prometheus & Loki)
- Custom dashboards in `grafana/dashboards/`

**Configuration**:
- Datasources: `grafana/provisioning/datasources/prometheus.yml`
- Dashboards: `grafana/provisioning/dashboards/dashboard.yml`

### 3. Loki

**Purpose**: Log aggregation system (like Prometheus, but for logs).

**Port**: 3100

**Access**: http://localhost:3100

**Key Features**:
- Stores logs in a time-series format
- Efficient log storage and querying
- LogQL query language (similar to PromQL)

**Configuration**: `loki-config.yml`

### 4. Promtail

**Purpose**: Log shipper that collects logs from Docker containers and sends them to Loki.

**Key Features**:
- Automatically discovers Docker containers
- Collects logs from containers with `logging=true` label
- Parses and labels logs for better querying

**Configuration**: `promtail-config.yml`

## Application Instrumentation

### Metrics Endpoint

The application exposes a `/metrics` endpoint that Prometheus scrapes.

**Location**: `main.py`

**Metrics Collected**:

1. **HTTP Request Metrics**:
   - `http_requests_total`: Total HTTP requests (by method, endpoint, status)
   - `http_request_duration_seconds`: Request duration histogram

2. **Business Metrics**:
   - `url_shorten_requests_total`: Total URL shortening requests
   - `url_redirect_requests_total`: Total URL redirect requests

### How Metrics Are Collected

```python
# Middleware automatically tracks all HTTP requests
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    # Records request count and duration
    # Labels: method, endpoint, status_code
```

### Metrics Endpoint

Access metrics directly: http://localhost:8000/metrics

Example output:
```
http_requests_total{method="POST",endpoint="/api/shorten",status="201"} 42.0
url_shorten_requests_total 42.0
```

## Configuration Files

### prometheus.yml

**Location**: `prometheus.yml`

**Key Settings**:

```yaml
global:
  scrape_interval: 15s  # How often to scrape metrics (adjust based on needs)
  evaluation_interval: 15s  # How often to evaluate alerting rules

scrape_configs:
  - job_name: 'url-shortener'  # Name of the job (appears in Prometheus)
    static_configs:
      - targets: ['url-shortener:8000']  # Service name:port (Docker network)
    metrics_path: '/metrics'  # Endpoint to scrape
```

**To Add More Services**:
1. Add a new `scrape_configs` entry
2. Set the target to your service name and port
3. Restart Prometheus: `docker-compose restart prometheus`

### loki-config.yml

**Location**: `loki-config.yml`

**Key Settings**:

```yaml
limits_config:
  allow_structured_metadata: false  # Disable for compatibility
  volume_enabled: true  # Enable log volume visualization in Grafana

schema_config:
  configs:
    - from: 2020-10-24
      store: boltdb-shipper  # Storage backend
      schema: v11  # Schema version
```

**Storage**: Logs are stored in Docker volume `loki_data`

**To Adjust Retention**:
- Add `limits_config.max_query_length: 721h` for 30 days retention
- Modify `schema_config` period for index retention

### promtail-config.yml

**Location**: `promtail-config.yml`

**Key Settings**:

```yaml
scrape_configs:
  - job_name: docker
    docker_sd_configs:
      - host: unix:///var/run/docker.sock  # Docker socket
        filters:
          - name: label
            values: ["logging=true"]  # Only collect from containers with this label
```

**Labels Added**:
- `container`: Container name
- `container_id`: Container ID
- `logstream`: stdout/stderr

**To Collect Logs from More Containers**:
1. Add `logging: "true"` label to your service in `docker-compose.yml`
2. Promtail will automatically discover and collect logs

### Grafana Provisioning

**Datasources**: `grafana/provisioning/datasources/prometheus.yml`

```yaml
datasources:
  - name: Prometheus
    type: prometheus
    url: http://prometheus:9090  # Service name in Docker network
    isDefault: true
  
  - name: Loki
    type: loki
    url: http://loki:3100
```

**Dashboards**: `grafana/provisioning/dashboards/dashboard.yml`

```yaml
providers:
  - name: 'default'
    type: file
    options:
      path: /etc/grafana/provisioning/dashboards  # Maps to grafana/dashboards/
```

**To Add a New Dashboard**:
1. Export dashboard JSON from Grafana UI
2. Save to `grafana/dashboards/your-dashboard.json`
3. Restart Grafana: `docker-compose restart grafana`

## Adding Custom Metrics

### Step 1: Add Metric in Application

Edit `main.py`:

```python
from prometheus_client import Counter, Histogram, Gauge

# Define your metric
custom_metric = Counter(
    'custom_metric_total',
    'Description of your metric',
    ['label1', 'label2']  # Optional labels
)

# Use in your code
custom_metric.labels(label1='value1', label2='value2').inc()
```

### Step 2: Metric Types

- **Counter**: Always increasing (e.g., total requests)
- **Gauge**: Can go up or down (e.g., current connections)
- **Histogram**: Distribution of values (e.g., request duration)

### Step 3: Query in Grafana

Use PromQL:
```
rate(custom_metric_total[5m])  # Rate over 5 minutes
sum(custom_metric_total)  # Total count
```

## Adding Custom Dashboards

### Method 1: Create in Grafana UI

1. Go to http://localhost:3000
2. Click "+" → "Create Dashboard"
3. Add panels with queries
4. Export: Dashboard Settings → JSON Model
5. Save to `grafana/dashboards/`

### Method 2: Create JSON Manually

1. Copy an existing dashboard JSON
2. Modify panels, queries, and layout
3. Save to `grafana/dashboards/`
4. Restart Grafana

### Dashboard Structure

```json
{
  "title": "Dashboard Name",
  "panels": [
    {
      "title": "Panel Title",
      "type": "graph",  // or "stat", "gauge", "logs", etc.
      "targets": [
        {
          "expr": "your_promql_query",
          "refId": "A"
        }
      ]
    }
  ]
}
```

## Query Languages

### PromQL (Prometheus Query Language)

**Common Queries**:

```promql
# Rate of requests per second
rate(http_requests_total[5m])

# Total requests
sum(http_requests_total)

# Requests by endpoint
sum(http_requests_total) by (endpoint)

# 95th percentile duration
histogram_quantile(0.95, http_request_duration_seconds_bucket)
```

### LogQL (Loki Query Language)

**Common Queries**:

```logql
# All logs from container
{container="url-shortener"}

# Logs containing text
{container="url-shortener"} |= "error"

# Count logs over time
count_over_time({container="url-shortener"}[1m])

# Rate of log lines
rate({container="url-shortener"}[5m])
```

## Troubleshooting

### Metrics Not Appearing

1. **Check metrics endpoint**:
   ```bash
   curl http://localhost:8000/metrics
   ```

2. **Check Prometheus targets**:
   - Go to http://localhost:9090/targets
   - Verify "url-shortener" is UP

3. **Check Prometheus logs**:
   ```bash
   docker-compose logs prometheus
   ```

### Logs Not Appearing

1. **Check container label**:
   ```yaml
   # In docker-compose.yml
   labels:
     logging: "true"
   ```

2. **Check Promtail logs**:
   ```bash
   docker-compose logs promtail
   ```

3. **Check Loki**:
   ```bash
   curl http://localhost:3100/ready
   ```

4. **Query Loki directly**:
   ```bash
   curl "http://localhost:3100/loki/api/v1/labels"
   ```

### Grafana Dashboard Not Loading

1. **Check dashboard file**:
   - Valid JSON format
   - Correct datasource references

2. **Check Grafana logs**:
   ```bash
   docker-compose logs grafana
   ```

3. **Verify provisioning**:
   - Check `grafana/provisioning/dashboards/dashboard.yml`
   - Ensure path is correct

### Performance Issues

1. **Reduce scrape interval** (if too frequent):
   ```yaml
   # prometheus.yml
   scrape_interval: 30s  # Increase from 15s
   ```

2. **Limit log retention**:
   ```yaml
   # loki-config.yml
   limits_config:
     max_query_length: 168h  # 7 days
   ```

3. **Filter logs in Promtail**:
   - Only collect important logs
   - Use pipeline stages to drop unnecessary logs

## Best Practices

1. **Labeling**: Use consistent labels across metrics
2. **Cardinality**: Avoid high-cardinality labels (e.g., user IDs)
3. **Retention**: Set appropriate retention periods
4. **Alerts**: Set up alerts for critical metrics
5. **Documentation**: Document custom metrics and dashboards

## Useful Resources

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Loki Documentation](https://grafana.com/docs/loki/)
- [PromQL Guide](https://prometheus.io/docs/prometheus/latest/querying/basics/)
- [LogQL Guide](https://grafana.com/docs/loki/latest/logql/)

## Next Steps

1. **Add Alerts**: Configure alerting rules in Prometheus
2. **Add More Dashboards**: Create dashboards for specific use cases
3. **Add More Metrics**: Instrument additional application features
4. **Set Up Alertmanager**: For alert notifications
5. **Add Tracing**: Consider adding OpenTelemetry for distributed tracing

