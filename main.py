import os
import logging
from datetime import datetime, timezone
from typing import Dict, Any

import httpx
from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Catme",
    description="A RESTful API that returns profile information with dynamic cat facts",
    version="1.0.0"
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

PROFILE_INFO = {
    "email": os.getenv("PROFILE_EMAIL", "rifushigi@dev.com"),
    "name": os.getenv("PROFILE_NAME", "Rifushigi"),
    "stack": os.getenv("PROFILE_STACK", "Python/FastAPI")
}

CAT_URI = os.getenv("CAT_FACTS_API_URL", "https://catfact.ninja/fact")
API_TIMEOUT = os.getenv("API_TIMEOUT", 10)

async def fetch_cat_fact() -> str:
    """
    Fetch a random cat fact from the Cat Facts API.
    
    Returns:
        str: A random cat fact
        
    Raises:
        HTTPException: If the external API is unavailable or times out
    """
    try:
        async with httpx.AsyncClient(timeout=API_TIMEOUT) as client:
            logger.info(f"Fetching cat fact from {CAT_URI}")
            response = await client.get(CAT_URI)
            response.raise_for_status()

            data = response.json()
            cat_fact = data.get("fact", "")

            if not cat_fact:
                raise HTTPException(
                    status_code=502,
                    detail="Cat Facts API returned empty fact"
                )
            
            logger.info("Successfully fetched cat fact")
            return cat_fact
        
    except httpx.TimeoutException:
        logger.error("Cat Facts API request timed out")
        raise HTTPException(
            status_code=504,
            detail="Cat Facts API request timed out"
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"Cat Facts API returned error {e.response.status_code}")
        raise HTTPException(
            status_code=502,
            detail=f"Cat Facts API unavailable: {e.response.status_code}"
        )
    except Exception as e:
        logger.error(f"Unexpected error fetching cat fact: {str(e)}")
        raise HTTPException(
            status_code=502,
            detail="Failed to fetch cat fact from external API"
        )
    
@app.get("/me", response_model=Dict[str, any])
@limiter.limit("5/minute")
async def get_profile():
    """
    Get profile information along with a dynamic cat fact.
    
    Returns:
        dict: JSON response containing profile info and cat fact
    """
    try:
        timestamp = datetime.now(timezone.utc).isoformat

        cat_fact = await fetch_cat_fact()

        response_data = {
            "status": "success",
            "user": {
                "email": PROFILE_INFO["email"],
                "name": PROFILE_INFO["name"],
                "stack": PROFILE_INFO["stack"]
            },
            timestamp: timestamp,
            "fact": cat_fact
        }

        logger.info("Successfully generated profile response")
        return JSONResponse(
            content=response_data,
            media_type="application/json"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in get_profile: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )
    
@app.get("/health")
@limiter.limit("10/minute")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat}

if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")

    uvicorn.run("main:app", host=host, port=port, reload=True)