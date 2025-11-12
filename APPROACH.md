# URL Shortening Service - Implementation Approach

## Technology Stack Recommendation

### Option 1: Node.js + Express (Recommended for simplicity)
- **Runtime**: Node.js
- **Framework**: Express.js
- **Database**: SQLite (lightweight, file-based, no setup needed)
- **Language**: JavaScript/TypeScript

### Option 2: Python + Flask
- **Runtime**: Python 3.x
- **Framework**: Flask
- **Database**: SQLite
- **Language**: Python

### Option 3: Python + FastAPI
- **Runtime**: Python 3.x
- **Framework**: FastAPI (modern, async, auto-docs)
- **Database**: SQLite
- **Language**: Python

## Recommended Approach: Node.js + Express

### Why Node.js?
- Fast development
- Great for web APIs
- Large ecosystem
- Easy deployment

## Architecture Overview

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │
       │ HTTP Request
       ▼
┌─────────────────┐
│  Express Server │
│  (Port 5000)    │
└──────┬──────────┘
       │
       ├─── POST /api/shorten ───► Generate short code ───► Save to DB
       │
       └─── GET /{shortCode} ───► Lookup in DB ───► Redirect to original URL
                    │
                    ▼
            ┌───────────────┐
            │  SQLite DB    │
            │  (urls table) │
            └───────────────┘
```

## Implementation Steps

### 1. Project Setup
- Initialize Node.js project
- Install dependencies: express, sqlite3, nanoid (for short code generation)
- Create project structure

### 2. Database Schema
```sql
CREATE TABLE urls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    short_code TEXT UNIQUE NOT NULL,
    original_url TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 3. API Endpoints

#### POST /api/shorten
- **Request Body**: `{ "url": "https://example.com/very/long/url" }`
- **Response**: `{ "shortUrl": "http://localhost:5000/a1b2c3", "originalUrl": "...", "shortCode": "a1b2c3" }`
- **Validation**: Check if URL is valid format
- **Logic**: Generate unique short code, save to database

#### GET /{shortCode}
- **Response**: HTTP 302 Redirect to original URL
- **Error Handling**: 404 if short code doesn't exist

#### Optional: GET /api/stats/{shortCode}
- **Response**: Statistics about the short URL (creation date, etc.)

### 4. Short Code Generation Strategy

**Option A: Random Alphanumeric (Recommended)**
- Use library like `nanoid` or `shortid`
- Generate 6-8 character codes
- Check for uniqueness in database

**Option B: Base62 Encoding**
- Convert auto-incrementing ID to base62
- Shorter codes, guaranteed uniqueness

**Option C: Hash-based**
- Hash the original URL
- Use first 6-8 characters
- Handle collisions

### 5. URL Validation
- Check URL format using regex or URL constructor
- Ensure protocol (http/https) is present
- Validate URL is reachable (optional)

### 6. Error Handling
- Invalid URL format → 400 Bad Request
- Database errors → 500 Internal Server Error
- Short code not found → 404 Not Found
- Duplicate short code (retry generation)

## Project Structure

```
test-project/
├── requirement.txt
├── package.json
├── server.js (or app.js)
├── config/
│   └── database.js
├── routes/
│   └── urlRoutes.js
├── models/
│   └── urlModel.js
├── utils/
│   └── urlValidator.js
└── database/
    └── urls.db (SQLite file)
```

## Key Features to Implement

1. **URL Shortening**
   - Accept long URL
   - Generate unique short code
   - Store mapping
   - Return short URL

2. **URL Redirection**
   - Lookup short code
   - Redirect to original URL
   - Track access (optional)

3. **Validation**
   - URL format validation
   - Protocol validation
   - Duplicate handling

4. **Error Handling**
   - Graceful error responses
   - Proper HTTP status codes

## Testing Strategy

- Unit tests for URL validation
- Integration tests for API endpoints
- Test edge cases (invalid URLs, non-existent codes)

## Next Steps

1. Choose technology stack
2. Set up project structure
3. Implement database layer
4. Implement API endpoints
5. Add validation and error handling
6. Test the service

