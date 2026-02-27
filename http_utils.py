#!/usr/bin/env python3
"""
HTTP utilities with retry logic and error handling
"""

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
from typing import Optional
from app_config import (
    REQUEST_TIMEOUT, REQUEST_DELAY, MAX_RETRIES, 
    RETRY_BACKOFF, RETRY_STATUS_CODES
)


def create_session_with_retries() -> requests.Session:
    """
    Create a requests session with automatic retry logic
    
    Returns:
        Configured requests.Session with retry adapter
    """
    session = requests.Session()
    
    # Configure retry strategy
    # Use method_whitelist for older urllib3 versions, allowed_methods for newer
    try:
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=RETRY_BACKOFF,
            status_forcelist=RETRY_STATUS_CODES,
            allowed_methods=["HEAD", "GET", "OPTIONS"]  # Safe methods to retry
        )
    except TypeError:
        # Fallback for older urllib3 versions
        retry_strategy = Retry(
            total=MAX_RETRIES,
            backoff_factor=RETRY_BACKOFF,
            status_forcelist=RETRY_STATUS_CODES,
            method_whitelist=["HEAD", "GET", "OPTIONS"]  # Safe methods to retry
        )
    
    # Mount adapter with retry strategy
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session


def fetch_with_retry(session: requests.Session, url: str, 
                    headers: Optional[dict] = None,
                    delay: bool = True) -> Optional[requests.Response]:
    """
    Fetch URL with retry logic and error handling
    
    Args:
        session: Requests session to use
        url: URL to fetch
        headers: Optional headers to include
        delay: Whether to add delay before request
    
    Returns:
        Response object if successful, None if failed
    """
    if delay:
        time.sleep(REQUEST_DELAY)
    
    try:
        response = session.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()  # Raise exception for bad status codes
        return response
    except requests.exceptions.Timeout:
        print(f"   ⚠️  Timeout fetching {url}")
        return None
    except requests.exceptions.ConnectionError:
        print(f"   ⚠️  Connection error fetching {url}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"   ⚠️  HTTP error {e.response.status_code} fetching {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"   ⚠️  Error fetching {url}: {e}")
        return None
