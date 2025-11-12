"""
FastAPI application for URL shortening service.
"""
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import Optional
import os
import time
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

from app.database import init_db, get_db, URL
from app.schemas import URLShortenRequest, URLShortenResponse, ErrorResponse
from app.utils import validate_url, normalize_url, get_unique_short_code

# Prometheus metrics
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

url_shorten_requests = Counter(
    'url_shorten_requests_total',
    'Total URL shortening requests'
)

url_redirect_requests = Counter(
    'url_redirect_requests_total',
    'Total URL redirect requests'
)

# Initialize FastAPI app
app = FastAPI(
    title="URL Shortening Service",
    description="A web-based URL shortening service that creates short URLs from long URLs",
    version="1.0.0"
)

# Mount static files directory
# Go up one level from app/ to project root, then to static/
static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on application startup."""
    init_db()


# Middleware for Prometheus metrics
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Middleware to collect Prometheus metrics."""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Extract endpoint (simplify for metrics)
    endpoint = request.url.path
    # Simplify endpoint for metrics (remove variable parts)
    if endpoint.startswith("/api/stats/"):
        endpoint = "/api/stats/{code}"
    elif len(endpoint) > 1 and endpoint[1:].replace("/", "").isalnum() and len(endpoint.split("/")) == 2:
        endpoint = "/{shortCode}"
    
    # Record metrics
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


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/")
async def root():
    """Serve the frontend HTML page."""
    # Static dir is already set above (project root/static)
    html_path = os.path.join(static_dir, "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path)
    # Fallback to API info if static files not found
    return {
        "message": "URL Shortening Service API",
        "version": "1.0.0",
        "endpoints": {
            "shorten": "POST /api/shorten",
            "redirect": "GET /{shortCode}",
            "docs": "GET /docs"
        }
    }


@app.post(
    "/api/shorten",
    response_model=URLShortenResponse,
    status_code=status.HTTP_201_CREATED,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid URL format"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def shorten_url(
    request: URLShortenRequest,
    db: Session = Depends(get_db)
):
    """
    Create a short URL from a long URL.
    
    - **url**: The long URL to shorten (must be a valid URL)
    
    Returns the short URL, original URL, and short code.
    """
    # Validate URL
    if not validate_url(request.url):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid URL format. Please provide a valid URL (e.g., https://example.com)"
        )
    
    # Normalize URL (ensure protocol)
    normalized_url = normalize_url(request.url)
    
    # Check if URL already exists in database
    existing_url = db.query(URL).filter(URL.original_url == normalized_url).first()
    if existing_url:
        # Return existing short URL
        # Get base URL from request or use default
        base_url = os.getenv("BASE_URL", "http://localhost:8000")
        short_url = f"{base_url}/{existing_url.short_code}"
        return URLShortenResponse(
            short_url=short_url,
            original_url=existing_url.original_url,
            short_code=existing_url.short_code,
            created_at=existing_url.created_at
        )
    
    # Generate unique short code
    try:
        short_code = get_unique_short_code(db)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate short code: {str(e)}"
        )
    
    # Create new URL record
    db_url = URL(
        short_code=short_code,
        original_url=normalized_url
    )
    
    try:
        db.add(db_url)
        db.commit()
        db.refresh(db_url)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save URL: {str(e)}"
        )
    
    # Build short URL
    # Get base URL from environment or use default
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    short_url = f"{base_url}/{short_code}"
    
    # Increment metrics
    url_shorten_requests.inc()
    
    return URLShortenResponse(
        short_url=short_url,
        original_url=db_url.original_url,
        short_code=db_url.short_code,
        created_at=db_url.created_at
    )


@app.get(
    "/{short_code}",
    responses={
        404: {"model": ErrorResponse, "description": "Short code not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def redirect_url(
    short_code: str,
    db: Session = Depends(get_db)
):
    """
    Redirect to the original URL using the short code.
    
    - **short_code**: The short code from the shortened URL
    
    Returns HTTP 302 redirect to the original URL.
    """
    # Lookup URL by short code
    url_record = db.query(URL).filter(URL.short_code == short_code).first()
    
    if not url_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short code '{short_code}' not found"
        )
    
    # Increment metrics
    url_redirect_requests.inc()
    
    # Redirect to original URL
    return RedirectResponse(url=url_record.original_url, status_code=status.HTTP_302_FOUND)


@app.get("/api/stats/{short_code}", response_model=URLShortenResponse)
async def get_url_stats(
    short_code: str,
    db: Session = Depends(get_db)
):
    """
    Get statistics about a short URL.
    
    - **short_code**: The short code to get statistics for
    
    Returns information about the short URL including creation date.
    """
    url_record = db.query(URL).filter(URL.short_code == short_code).first()
    
    if not url_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Short code '{short_code}' not found"
        )
    
    base_url = os.getenv("BASE_URL", "http://localhost:8000")
    short_url = f"{base_url}/{url_record.short_code}"
    
    return URLShortenResponse(
        short_url=short_url,
        original_url=url_record.original_url,
        short_code=url_record.short_code,
        created_at=url_record.created_at
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

