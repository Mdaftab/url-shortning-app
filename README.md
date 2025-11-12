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

## Technology Stack

- **Python 3.13+**
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **SQLite**: Lightweight database
- **Pydantic**: Data validation using Python type annotations
- **Uvicorn**: ASGI server

## Project Structure

```
test-project/
├── main.py              # FastAPI application and endpoints
├── database.py          # Database models and setup
├── schemas.py           # Pydantic schemas for request/response
├── utils.py             # Utility functions (validation, code generation)
├── test_app.py          # Test suite for the application
├── requirements.txt     # Python dependencies
├── requirement.txt      # Project requirements
├── README.md            # This file
├── .gitignore           # Git ignore file
├── Dockerfile           # Docker image configuration
├── docker-compose.yml   # Docker Compose configuration
├── .dockerignore        # Docker ignore file
├── static/              # Frontend static files
│   ├── index.html      # Main web interface
│   ├── style.css       # Stylesheet
│   └── script.js        # Frontend JavaScript
├── database/            # Database directory (created automatically)
│   └── urls.db          # SQLite database file
├── prometheus.yml       # Prometheus configuration
├── loki-config.yml      # Loki log aggregation configuration
├── promtail-config.yml  # Promtail log shipper configuration
├── grafana/             # Grafana configuration and dashboards
│   ├── provisioning/    # Auto-provisioned configs
│   │   ├── datasources/ # Datasource configurations
│   │   └── dashboards/  # Dashboard provisioning config
│   └── dashboards/      # Dashboard JSON files
│       ├── url-shortener-dashboard.json  # Main monitoring dashboard
│       └── url-created-overview.json     # URL creation overview
└── MONITORING.md        # Comprehensive monitoring guide
```

## Application Architecture & Request Flow

### URL Shortening Flow (POST /api/shorten)

```
┌─────────────┐
│   Client    │
│ (Browser/   │
│  API Call)  │
└──────┬──────┘
       │
       │ POST /api/shorten
       │ { "url": "https://example.com/very/long/url" }
       ▼
┌─────────────────────────────────────────────────────────┐
│                    FastAPI (main.py)                    │
│  ┌──────────────────────────────────────────────────┐  │
│  │  @app.post("/api/shorten")                       │  │
│  │  async def shorten_url(request, db)               │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
       │
       │ 1. Request Validation
       ▼
┌─────────────────────────────────────────────────────────┐
│              Pydantic Schema (schemas.py)              │
│  ┌──────────────────────────────────────────────────┐  │
│  │  URLShortenRequest                                │  │
│  │  - Validates request structure                    │  │
│  │  - Ensures 'url' field is present                 │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
       │
       │ 2. URL Validation & Normalization
       ▼
┌─────────────────────────────────────────────────────────┐
│              Utility Functions (utils.py)               │
│  ┌──────────────────────────────────────────────────┐  │
│  │  validate_url(url)                                │  │
│  │  ├─ Checks URL format using validators library   │  │
│  │  └─ Returns True/False                            │  │
│  │                                                    │  │
│  │  normalize_url(url)                               │  │
│  │  ├─ Adds https:// if protocol missing              │  │
│  │  └─ Returns normalized URL                       │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
       │
       │ 3. Check for Existing URL
       ▼
┌─────────────────────────────────────────────────────────┐
│         Database Layer (SQLAlchemy ORM)                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  db.query(URL)                                    │  │
│  │    .filter(URL.original_url == normalized_url)   │  │
│  │    .first()                                       │  │
│  └──────────────────────────────────────────────────┘  │
│                        │                                │
│                        ▼                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  SQLite Database (database/urls.db)               │  │
│  │  ┌────────────────────────────────────────────┐  │  │
│  │  │  Table: urls                                │  │  │
│  │  │  ├─ id (PRIMARY KEY)                       │  │  │
│  │  │  ├─ short_code (UNIQUE, INDEXED)           │  │  │
│  │  │  ├─ original_url                           │  │  │
│  │  │  └─ created_at                             │  │  │
│  │  └────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
       │
       ├─ If URL exists ──────────────┐
       │                              │
       │ 4a. Return existing short code│
       │                              │
       └─ If URL is new ─────────────┘
       │
       │ 4b. Generate Unique Short Code
       ▼
┌─────────────────────────────────────────────────────────┐
│              Utility Functions (utils.py)               │
│  ┌──────────────────────────────────────────────────┐  │
│  │  get_unique_short_code(db)                      │  │
│  │  ├─ generate_short_code()                       │  │
│  │  │  └─ Creates 6-char alphanumeric code         │  │
│  │  ├─ Check database for uniqueness               │  │
│  │  └─ Retry if collision (max 10 attempts)       │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
       │
       │ 5. Save to Database
       ▼
┌─────────────────────────────────────────────────────────┐
│         Database Layer (SQLAlchemy ORM)                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  db_url = URL(                                   │  │
│  │    short_code=short_code,                        │  │
│  │    original_url=normalized_url                   │  │
│  │  )                                               │  │
│  │  db.add(db_url)                                 │  │
│  │  db.commit()                                     │  │
│  └──────────────────────────────────────────────────┘  │
│                        │                                │
│                        ▼                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  SQLite Database                                 │  │
│  │  └─ INSERT INTO urls (...)                      │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
       │
       │ 6. Build Response
       ▼
┌─────────────────────────────────────────────────────────┐
│              Pydantic Schema (schemas.py)               │
│  ┌──────────────────────────────────────────────────┐  │
│  │  URLShortenResponse                              │  │
│  │  {                                                │  │
│  │    "short_url": "http://localhost:8000/abc123",  │  │
│  │    "original_url": "https://example.com/...",    │  │
│  │    "short_code": "abc123",                       │  │
│  │    "created_at": "2024-01-01T12:00:00"          │  │
│  │  }                                                │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
       │
       │ HTTP 201 Created
       ▼
┌─────────────┐
│   Client    │
│  Receives   │
│  Response   │
└─────────────┘
```

### URL Redirection Flow (GET /{shortCode})

```
┌─────────────┐
│   Client    │
│ (Browser)   │
└──────┬──────┘
       │
       │ GET /{shortCode}
       │ Example: GET /abc123
       ▼
┌─────────────────────────────────────────────────────────┐
│                    FastAPI (main.py)                    │
│  ┌──────────────────────────────────────────────────┐  │
│  │  @app.get("/{short_code}")                       │  │
│  │  async def redirect_url(short_code, db)          │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
       │
       │ 1. Lookup Short Code in Database
       ▼
┌─────────────────────────────────────────────────────────┐
│         Database Layer (SQLAlchemy ORM)                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  db.query(URL)                                    │  │
│  │    .filter(URL.short_code == short_code)          │  │
│  │    .first()                                       │  │
│  └──────────────────────────────────────────────────┘  │
│                        │                                │
│                        ▼                                │
│  ┌──────────────────────────────────────────────────┐  │
│  │  SQLite Database                                 │  │
│  │  └─ SELECT * FROM urls WHERE short_code = ?      │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
       │
       ├─ If found ───────────────────┐
       │                              │
       │ 2a. Get original_url         │
       │                              │
       └─ If not found ───────────────┘
       │
       │ 2b. Return 404 Error
       ▼
┌─────────────────────────────────────────────────────────┐
│              Error Response (schemas.py)               │
│  ┌──────────────────────────────────────────────────┐  │
│  │  ErrorResponse                                  │  │
│  │  { "detail": "Short code 'abc123' not found" }  │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
       │
       │ HTTP 404 Not Found
       ▼
┌─────────────┐
│   Client    │
│  Receives   │
│   Error     │
└─────────────┘

       OR (if found)

       │ 3. Redirect to Original URL
       ▼
┌─────────────────────────────────────────────────────────┐
│              FastAPI RedirectResponse                   │
│  ┌──────────────────────────────────────────────────┐  │
│  │  RedirectResponse(                               │  │
│  │    url=url_record.original_url,                  │  │
│  │    status_code=302                               │  │
│  │  )                                                │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
       │
       │ HTTP 302 Found
       │ Location: https://example.com/very/long/url
       ▼
┌─────────────┐
│   Client    │
│  Browser    │
│  Redirects  │
│  to Original│
│    URL      │
└─────────────┘
```

### Component Interaction Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Browser    │  │  cURL/HTTP   │  │  API Client   │        │
│  │  (Frontend)  │  │   Request    │  │   (Python/JS) │        │
│  └──────┬───────┘  └──────┬───────┘  └──────┬────────┘        │
└─────────┼──────────────────┼──────────────────┼────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      FASTAPI APPLICATION                        │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    main.py                               │  │
│  │  ┌────────────────────────────────────────────────────┐ │  │
│  │  │  Endpoints:                                         │ │  │
│  │  │  • GET  /              → Serve frontend            │ │  │
│  │  │  • POST /api/shorten   → Shorten URL               │ │  │
│  │  │  • GET  /{shortCode}   → Redirect                  │ │  │
│  │  │  • GET  /api/stats/{code} → Get stats              │ │  │
│  │  └────────────────────────────────────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
          │                    │                    │
          │                    │                    │
          ▼                    ▼                    ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  schemas.py      │  │  utils.py        │  │  database.py      │
│  ┌──────────────┐ │  │  ┌──────────────┐ │  │  ┌──────────────┐ │
│  │ Request      │ │  │  │ validate_url │ │  │  │ URL Model    │ │
│  │ Validation   │ │  │  │ normalize_   │ │  │  │ Session      │ │
│  │ Response     │ │  │  │   url        │ │  │  │ Management   │ │
│  │ Models       │ │  │  │ generate_    │ │  │  │ init_db()    │ │
│  └──────────────┘ │  │  │   short_code │ │  │  └──────────────┘ │
└──────────────────┘  │  └──────────────┘ │  └──────────────────┘
                      └──────────────────┘
                                        │
                                        ▼
                      ┌──────────────────────────────────┐
                      │      SQLite Database              │
                      │  ┌────────────────────────────┐  │
                      │  │  Table: urls                │  │
                      │  │  • id                      │  │
                      │  │  • short_code (INDEXED)     │  │
                      │  │  • original_url            │  │
                      │  │  • created_at              │  │
                      │  └────────────────────────────┘  │
                      └──────────────────────────────────┘
```

### Data Flow Summary

1. **Request Reception**: FastAPI receives HTTP request
2. **Schema Validation**: Pydantic validates request structure
3. **Business Logic**: 
   - URL validation and normalization (utils.py)
   - Duplicate checking (database query)
   - Short code generation (utils.py)
4. **Data Persistence**: SQLAlchemy ORM saves to SQLite
5. **Response Formation**: Pydantic models format response
6. **HTTP Response**: FastAPI returns JSON or redirect

## Installation

### Option 1: Docker (Recommended)

The easiest way to run the application is using Docker.

#### Prerequisites

- Docker and Docker Compose installed

#### Quick Start with Docker

1. **Clone or navigate to the project directory:**
   ```bash
   cd test-project
   ```

2. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

   This will:
   - Build the Docker image
   - Start the container
   - Make the application available at `http://localhost:8000`

3. **Run in detached mode (background):**
   ```bash
   docker-compose up -d
   ```

4. **Stop the application:**
   ```bash
   docker-compose down
   ```

#### Using Docker directly

1. **Build the Docker image:**
   ```bash
   docker build -t url-shortener .
   ```

2. **Run the container:**
   ```bash
   docker run -d -p 8000:8000 -v $(pwd)/database:/app/database --name url-shortener url-shortener
   ```

   The `-v` flag mounts the database directory to persist data.

### Option 2: Local Installation

#### Prerequisites

- Python 3.13 or higher
- pip (Python package manager)

#### Setup Steps

1. **Clone or navigate to the project directory:**
   ```bash
   cd test-project
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment:**
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

### Start the Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The `--reload` flag enables auto-reload on code changes (useful for development).

Alternatively, you can run directly:
```bash
python main.py
```

The server will start on `http://localhost:8000`

### Access the Application

Once the server is running, you can access:

- **Web Interface**: http://localhost:8000 (Main frontend for URL shortening)
- **API Documentation (Swagger UI)**: http://localhost:8000/docs
- **API Documentation (ReDoc)**: http://localhost:8000/redoc

## API Endpoints

### 1. Root Endpoint

**GET** `/`

Returns API information and available endpoints.

**Response:**
```json
{
  "message": "URL Shortening Service API",
  "version": "1.0.0",
  "endpoints": {
    "shorten": "POST /api/shorten",
    "redirect": "GET /{shortCode}",
    "docs": "GET /docs"
  }
}
```

### 2. Shorten URL

**POST** `/api/shorten`

Creates a short URL from a long URL.

**Request Body:**
```json
{
  "url": "https://www.example.com/very/long/url/path"
}
```

**Response (201 Created):**
```json
{
  "short_url": "http://localhost:8000/k4Zyw4",
  "original_url": "https://www.example.com/very/long/url/path",
  "short_code": "k4Zyw4",
  "created_at": "2024-01-01T12:00:00"
}
```

**Error Responses:**
- `400 Bad Request`: Invalid URL format
- `500 Internal Server Error`: Server error

### 3. Redirect to Original URL

**GET** `/{shortCode}`

Redirects to the original URL using the short code.

**Example:**
```
GET http://localhost:8000/k4Zyw4
```

**Response:**
- `302 Found`: Redirects to the original URL
- `404 Not Found`: Short code doesn't exist

### 4. Get URL Statistics

**GET** `/api/stats/{shortCode}`

Returns information about a shortened URL.

**Response (200 OK):**
```json
{
  "short_url": "http://localhost:8000/k4Zyw4",
  "original_url": "https://www.example.com/very/long/url/path",
  "short_code": "k4Zyw4",
  "created_at": "2024-01-01T12:00:00"
}
```

**Error Response:**
- `404 Not Found`: Short code doesn't exist

## Web Interface

The application includes a beautiful, responsive web interface that makes URL shortening easy and intuitive.

### Features

- **Simple Form**: Just paste your long URL and click "Shorten URL"
- **Instant Results**: Get your short URL immediately
- **Copy to Clipboard**: One-click copy functionality
- **Test Links**: Direct link to test your shortened URL
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile devices
- **Error Handling**: Clear error messages for invalid URLs

### How to Use

1. Open your browser and navigate to `http://localhost:8000`
2. Paste your long URL in the input field
3. Click "Shorten URL"
4. Copy the generated short URL and share it!

The web interface automatically handles:
- URL validation
- Duplicate URL detection (returns existing short code)
- Error display
- Success feedback

## Usage Examples

### Using the Web Interface

Simply visit `http://localhost:8000` in your browser and use the intuitive form to shorten URLs.

### Using cURL

**Shorten a URL:**
```bash
curl -X POST "http://localhost:8000/api/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.example.com/very/long/url"}'
```

**Access shortened URL (redirects automatically):**
```bash
curl -L "http://localhost:8000/k4Zyw4"
```

**Get URL statistics:**
```bash
curl "http://localhost:8000/api/stats/k4Zyw4"
```

### Using Python requests

```python
import requests

# Shorten a URL
response = requests.post(
    "http://localhost:8000/api/shorten",
    json={"url": "https://www.example.com/very/long/url"}
)
data = response.json()
print(f"Short URL: {data['short_url']}")

# Access the shortened URL
short_code = data['short_code']
redirect_response = requests.get(
    f"http://localhost:8000/{short_code}",
    allow_redirects=False
)
print(f"Redirects to: {redirect_response.headers['Location']}")
```

### Using JavaScript (fetch)

```javascript
// Shorten a URL
fetch('http://localhost:8000/api/shorten', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    url: 'https://www.example.com/very/long/url'
  })
})
.then(response => response.json())
.then(data => {
  console.log('Short URL:', data.short_url);
  // Redirect to shortened URL
  window.location.href = data.short_url;
});
```

## Testing

The project includes a comprehensive test suite. Run tests with:

```bash
# Make sure the server is running first
uvicorn main:app --host 0.0.0.0 --port 8000 &

# Run tests
python test_app.py
```

The test suite covers:
- ✅ Root endpoint
- ✅ URL shortening
- ✅ URL redirection
- ✅ Invalid URL handling
- ✅ Non-existent short code handling
- ✅ Duplicate URL handling
- ✅ Statistics endpoint

## How It Works

1. **URL Validation**: When a URL is submitted, it's validated to ensure it's a proper URL format. If no protocol is provided, `https://` is automatically prepended.

2. **Short Code Generation**: A unique 6-character alphanumeric code is generated using cryptographically secure random generation.

3. **Database Storage**: The mapping between the short code and original URL is stored in a SQLite database.

4. **Duplicate Handling**: If the same URL is shortened multiple times, the existing short code is returned instead of creating a duplicate.

5. **Redirection**: When a short URL is accessed, the server looks up the original URL in the database and returns an HTTP 302 redirect.

## Database Schema

The SQLite database contains a single table:

```sql
CREATE TABLE urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    short_code TEXT UNIQUE NOT NULL,
    original_url TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## Configuration

### Changing the Port

To run on a different port, modify `main.py`:

```python
uvicorn.run(app, host="0.0.0.0", port=YOUR_PORT)
```

Or use the command line:
```bash
uvicorn main:app --host 0.0.0.0 --port YOUR_PORT
```

### Changing Short Code Length

Modify the `generate_short_code` function in `utils.py`:

```python
def generate_short_code(length: int = 8) -> str:  # Change default length
    ...
```

## Error Handling

The API provides clear error messages:

- **400 Bad Request**: Invalid URL format
- **404 Not Found**: Short code doesn't exist
- **500 Internal Server Error**: Server/database errors

## Security Considerations

- URLs are validated before storage
- Short codes are generated using cryptographically secure random generation
- SQL injection protection via SQLAlchemy ORM
- Input validation using Pydantic schemas

## Future Enhancements

Potential improvements:
- [ ] Custom short code support
- [ ] URL expiration dates
- [ ] Click tracking and analytics
- [ ] Rate limiting
- [ ] User authentication
- [ ] Bulk URL shortening
- [ ] QR code generation
- [ ] API key authentication

## Monitoring & Observability

The application includes a complete monitoring stack with Prometheus, Grafana, and Loki.

### Quick Start

Start all services including monitoring:
```bash
docker-compose up -d
```

Access monitoring tools:
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090
- **Loki**: http://localhost:3100

### Available Dashboards

1. **URL Shortener Monitoring** - Main dashboard with:
   - HTTP request metrics
   - Request duration (p95)
   - URL shorten/redirect counts
   - HTTP status codes
   - Application logs

2. **URL Created Overview** - Gauge showing total URLs created

### Metrics Endpoint

The application exposes Prometheus metrics at:
```
http://localhost:8000/metrics
```

### For SREs: Detailed Monitoring Guide

See [MONITORING.md](MONITORING.md) for:
- Complete monitoring architecture
- How to add custom metrics
- How to create custom dashboards
- Configuration file explanations
- Troubleshooting guide
- Best practices

## Docker Configuration

### Environment Variables

You can customize the application using environment variables:

- `BASE_URL`: Base URL for generated short URLs (default: `http://localhost:8000`)
  ```bash
  docker run -e BASE_URL=http://yourdomain.com -p 8000:8000 url-shortener
  ```

### Docker Compose Environment

Edit `docker-compose.yml` to change environment variables:

```yaml
environment:
  - BASE_URL=http://yourdomain.com
```

### Persistent Data

The database is stored in the `./database` directory and is mounted as a volume in Docker, ensuring your data persists even when containers are recreated.

### Docker Commands

```bash
# View logs
docker-compose logs -f

# Restart the service
docker-compose restart

# Rebuild after code changes
docker-compose up --build

# Stop and remove containers
docker-compose down

# Stop and remove containers with volumes (⚠️ deletes database)
docker-compose down -v
```

## Troubleshooting

### Port Already in Use

If you get an "address already in use" error:
```bash
# Find process using port 8000
lsof -ti:8000

# Kill the process
kill -9 $(lsof -ti:8000)
```

### Docker Issues

**Container won't start:**
```bash
# Check logs
docker-compose logs

# Rebuild the image
docker-compose build --no-cache
```

**Port conflict in Docker:**
Edit `docker-compose.yml` to use a different port:
```yaml
ports:
  - "8080:8000"  # Use port 8080 on host
```

**Database permissions:**
```bash
# Ensure database directory is writable
chmod -R 755 database/
```

### Database Issues

If you encounter database errors, you can delete the database file and restart:
```bash
rm -rf database/urls.db
# Restart the server - it will recreate the database
```

### Import Errors

Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Static Files Not Loading

If the web interface doesn't load:
- Ensure the `static/` directory exists with `index.html`, `style.css`, and `script.js`
- Check that FastAPI is properly mounting the static files directory
- Verify file permissions

## License

This project is open source and available for educational purposes.

## Author

Created as a URL shortening service implementation.

## Support

For issues or questions, please check the API documentation at `/docs` when the server is running.

