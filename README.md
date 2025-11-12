# URL Shortening Service API

A fast and efficient web-based URL shortening service built with Python and FastAPI. This service allows users to convert long URLs into short, manageable links that redirect to the original URLs.

## Features

- ✅ **Web Interface**: Beautiful, responsive frontend for easy URL shortening
- ✅ **URL Shortening**: Convert long URLs into short, unique codes
- ✅ **URL Redirection**: Automatically redirect short URLs to original URLs
- ✅ **URL Validation**: Validates URLs before shortening
- ✅ **Duplicate Handling**: Returns existing short URL for duplicate long URLs
- ✅ **Statistics**: Get information about shortened URLs
- ✅ **SQLite Database**: Lightweight, file-based storage
- ✅ **RESTful API**: Clean, well-documented API endpoints
- ✅ **Auto-generated Docs**: Interactive API documentation with Swagger UI
- ✅ **Docker Support**: Easy deployment with Docker and Docker Compose
- ✅ **Monitoring & Observability**: Prometheus, Grafana, and Loki for metrics and logs

## Quick Start

### With Docker (Recommended)

```bash
docker-compose up -d
```

Access the application:
- **Web Interface**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

### Local Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Project Structure

```
test-project/
├── app/                    # Application source code
│   ├── __init__.py
│   ├── main.py            # FastAPI application and endpoints
│   ├── database.py         # Database models and setup
│   ├── schemas.py          # Pydantic schemas for request/response
│   └── utils.py            # Utility functions (validation, code generation)
├── static/                 # Frontend static files
│   ├── index.html         # Main web interface
│   ├── style.css          # Stylesheet
│   └── script.js           # Frontend JavaScript
├── tests/                  # Test suite
│   └── test_app.py        # Integration tests
├── monitoring/             # Monitoring stack configuration
│   ├── prometheus.yml     # Prometheus configuration
│   ├── loki-config.yml    # Loki log aggregation configuration
│   ├── promtail-config.yml # Promtail log shipper configuration
│   └── grafana/           # Grafana configuration and dashboards
│       ├── provisioning/  # Auto-provisioned configs
│       │   ├── datasources/ # Datasource configurations
│       │   └── dashboards/  # Dashboard provisioning config
│       └── dashboards/     # Dashboard JSON files
├── database/               # Database directory (created automatically)
│   └── urls.db            # SQLite database file
├── docs/                   # Documentation
│   ├── README.md          # Detailed README (this file)
│   ├── MONITORING.md      # Comprehensive monitoring guide
│   ├── APPROACH.md        # Implementation approach
│   └── requirement.txt    # Project requirements
├── requirements.txt        # Python dependencies
├── Dockerfile             # Docker image configuration
├── docker-compose.yml     # Docker Compose configuration
└── .gitignore             # Git ignore file
```

## Documentation

- **[Full README](docs/README-DETAILED.md)**: Complete documentation with API details, architecture diagrams, and usage examples
- **[Monitoring Guide](docs/MONITORING.md)**: Comprehensive guide for Prometheus, Grafana, and Loki setup
- **[Implementation Approach](docs/APPROACH.md)**: Technical approach and design decisions

## Technology Stack

- **Python 3.13+**
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **SQLite**: Lightweight database
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server
- **Prometheus**: Metrics collection
- **Grafana**: Visualization and dashboards
- **Loki**: Log aggregation

## API Endpoints

- `GET /` - Web interface
- `POST /api/shorten` - Create short URL
- `GET /{shortCode}` - Redirect to original URL
- `GET /api/stats/{shortCode}` - Get URL statistics
- `GET /metrics` - Prometheus metrics endpoint
- `GET /docs` - Swagger UI documentation

## Monitoring

The application includes a complete monitoring stack:

- **Prometheus**: Collects metrics from `/metrics` endpoint
- **Grafana**: Pre-configured dashboards for visualization
- **Loki**: Aggregates application logs
- **Promtail**: Collects logs from Docker containers

See [MONITORING.md](docs/MONITORING.md) for detailed information.

## License

This project is open source and available for educational purposes.

