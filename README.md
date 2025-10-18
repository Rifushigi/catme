# Catme API

A simple RESTful API endpoint that returns profile information along with a dynamic cat fact fetched from an external API. Built with FastAPI and Python.

## Features

- **GET /me** endpoint returning profile information and dynamic cat facts
- Integration with Cat Facts API <https://catfact.ninja/fact>
- Proper error handling for external API failures
- CORS support for cross-origin requests
- Environment-based configuration
- Comprehensive logging
- Health check endpoint

## Requirements

- Python 3.8+
- pip (Python package manager)

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/Rifushigi/catme
   cd catme
   ```

2. **Create and activate a virtual environment:**

   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**

   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your profile information
   ```

   Update the following variables in `.env`:
   - `PROFILE_EMAIL`: Your email address
   - `PROFILE_NAME`: Your full name
   - `PROFILE_STACK`: Your backend technology stack (e.g., "Python/FastAPI")

## Running the Application

```bash
# Method 1: Using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Method 2: Using Python
python main.py
```

The API will be available at:

- **Main endpoint:** <http://localhost:8000/me>
- **Health check:** <http://localhost:8000/health>
- **API documentation:** <http://localhost:8000/docs> (Swagger UI)
- **Alternative docs:** <http://localhost:8000/redoc>

## API Documentation

### GET /me

Returns profile information along with a dynamic cat fact.

**Response Format:**

```json
{
  "status": "success",
  "user": {
    "email": "rifushigi@dev.com",
    "name": "Rifushigi",
    "stack": "Python/FastAPI"
  },
  "timestamp": "2025-10-18T12:34:56.789Z",
  "fact": "Random cat fact from the Cat Facts API"
}
```

**Response Fields:**

- `status`: Always "success" for successful requests
- `user.email`: User's email address (configured via environment variable)
- `user.name`: User's full name (configured via environment variable)
- `user.stack`: Backend technology stack (configured via environment variable)
- `timestamp`: Current UTC time in ISO 8601 format
- `fact`: Random cat fact fetched from Cat Facts API

**HTTP Status Codes:**

- `200 OK`: Successful response
- `502 Bad Gateway`: Cat Facts API is unavailable or returned an error
- `504 Gateway Timeout`: Cat Facts API request timed out
- `500 Internal Server Error`: Unexpected server error

### GET /health

Health check endpoint for monitoring.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2025-10-18T14:36:55.135910+00:00"
}
```

## Environment Variables

| Variable | Description | Default Value |
|----------|-------------|---------------|
| `PROFILE_EMAIL` | Your email address | `rifushigi@dev.com` |
| `PROFILE_NAME` | Your full name | `Rifushigi` |
| `PROFILE_STACK` | Your backend stack | `Python/FastAPI` |
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `ENVIRONMENT` | Environment mode | `development` |

## Error Handling

The API implements comprehensive error handling:

1. **External API Failures**: If the Cat Facts API is unavailable, the endpoint returns a 502 Bad Gateway error
2. **Timeout Handling**: Requests to the Cat Facts API timeout after 10 seconds
3. **Network Errors**: Network-related errors are caught and return appropriate HTTP status codes
4. **Logging**: All errors are logged for debugging purposes

## Testing

Run the test suite:

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
python -m pytest test_main.py -v
```

Test the API manually:

```bash
# Test the main endpoint
curl http://localhost:8000/me

# Test the health endpoint
curl http://localhost:8000/health
```

## Project Structure

```
catme/
├── main.py              # Main FastAPI application
├── requirements.txt     # Python dependencies
├── .env                 # Environment configuration
├── .env.example         # Environment template
├── .gitignore          # Git ignore rules
├── test_main.py        # Test suite
└── README.md           # This file
```

## Dependencies

- **FastAPI** – Modern, fast (high-performance) web framework for building APIs with Python
- **Uvicorn** – Lightning-fast ASGI server for running FastAPI applications
- **HTTPX** – Asynchronous HTTP client for making external API requests
- **python-dotenv** – Loads environment variables from a `.env` file for configuration management
- **python-multipart** – Enables form-data and file upload parsing in FastAPI
- **slowapi** – Rate limiting extension for FastAPI applications
- **pytest** – Testing framework for Python used to write and run unit tests

## License

This project is open source and available under the [MIT License](LICENSE).
