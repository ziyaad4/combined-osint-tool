import requests
import pandas as pd
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Union, Optional

class UsernameChecker:
    """Class to check username/email across different platforms"""
    
    def __init__(self):
        # Platform URLs - these are the URLs we'll check for usernames
        self.platforms = {
            "Twitter": {
                "url": "https://twitter.com/{username}",
                "error_msg": ["page doesn't exist"],
                "username_only": True
            },
            "Instagram": {
                "url": "https://www.instagram.com/{username}/",
                "error_msg": ["page not found", "page isn't available"],
                "username_only": True
            },
            "GitHub": {
                "url": "https://github.com/{username}",
                "error_msg": ["not found", "404"],
                "username_only": True
            },
            "Reddit": {
                "url": "https://www.reddit.com/user/{username}",
                "error_msg": ["page not found", "Sorry, nobody on Reddit"],
                "username_only": True
            },
            "LinkedIn": {
                "url": "https://www.linkedin.com/in/{username}",
                "error_msg": ["page not found", "this page doesn't exist"],
                "username_only": True
            },
            "TikTok": {
                "url": "https://www.tiktok.com/@{username}",
                "error_msg": ["couldn't find this account"],
                "username_only": True
            },
            "Pinterest": {
                "url": "https://www.pinterest.com/{username}/",
                "error_msg": ["user not found", "404"],
                "username_only": True
            },
            "Telegram": {
                "url": "https://t.me/{username}",
                "error_msg": ["Sorry, this user doesn't seem to exist"],
                "username_only": True
            },
            "Medium": {
                "url": "https://medium.com/@{username}",
                "error_msg": ["page not found", "404"],
                "username_only": True
            },
            "DeviantArt": {
                "url": "https://www.deviantart.com/{username}",
                "error_msg": ["page not found", "is not a deviantart"],
                "username_only": True
            }
            # Email platforms cannot be easily checked with this method
            # they would require API access or authentication
        }
        
        # Common headers to avoid being blocked
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache"
        }
        
        # Service for email verification
        self.email_verification_url = "https://api.hunter.io/v2/email-verifier"
        
    def check_platform(self, platform: str, username: str) -> Dict[str, Union[str, bool]]:
        """Check if username exists on a specific platform
        
        Args:
            platform: The platform to check (e.g., "Twitter")
            username: The username to check
            
        Returns:
            Dict containing platform, URL, and existence status
        """
        result = {
            "platform": platform,
            "url": self.platforms[platform]["url"].format(username=username),
            "exists": False,
            "status_code": None,
            "error": None
        }
        
        try:
            # Add a small random delay to avoid rate limiting
            time.sleep(random.uniform(0.5, 1.5))
            
            # Set up request
            headers = self.headers.copy()
            headers["Referer"] = f"https://www.google.com/search?q={platform}"
            
            response = requests.get(
                result["url"], 
                headers=headers,
                timeout=5,
                allow_redirects=True
            )
            
            result["status_code"] = response.status_code
            
            # Check if user exists based on status code and error messages
            if response.status_code == 200:
                error_found = False
                for error_msg in self.platforms[platform]["error_msg"]:
                    if error_msg.lower() in response.text.lower():
                        error_found = True
                        break
                
                result["exists"] = not error_found
            else:
                result["exists"] = False
                
        except Exception as e:
            result["error"] = str(e)
            result["exists"] = False
            
        return result
    
    def check_email(self, email: str) -> Dict[str, Union[str, bool]]:
        """Check if an email address is valid and potentially exists
        
        Args:
            email: The email to verify
            
        Returns:
            Dict containing verification results
        """
        # Basic email format validation
        if "@" not in email or "." not in email.split("@")[1]:
            return {
                "email": email,
                "valid_format": False,
                "deliverable": False,
                "result": "Invalid email format"
            }
        
        # Extract domain for MX record check
        domain = email.split("@")[1]
        
        result = {
            "email": email,
            "valid_format": True,
            "domain": domain,
            "deliverable": None,
            "message": None,
            "result": None
        }
        
        try:
            # This is a basic implementation
            # In a real app, you'd use a proper email verification service API
            # or check MX records and perform SMTP validation
            
            import socket
            from dns import resolver
            
            # Check if domain exists (DNS resolution)
            try:
                socket.gethostbyname(domain)
                result["domain_exists"] = True
            except socket.gaierror:
                result["domain_exists"] = False
                result["deliverable"] = False
                result["result"] = "Domain does not exist"
                return result
            
            # Check for MX records
            try:
                mx_records = resolver.resolve(domain, 'MX')
                if mx_records:
                    result["has_mx_records"] = True
                    result["deliverable"] = True
                    result["result"] = "Email domain has valid MX records"
                else:
                    result["has_mx_records"] = False
                    result["deliverable"] = False
                    result["result"] = "Domain exists but has no mail exchanger"
            except (resolver.NoAnswer, resolver.NXDOMAIN, resolver.NoNameservers):
                result["has_mx_records"] = False
                result["deliverable"] = False
                result["result"] = "Domain exists but has no mail exchanger"
                
        except Exception as e:
            result["error"] = str(e)
            result["result"] = "Verification error"
            
        return result

def check_username(query: str, query_type: str = "Username", platforms: Optional[List[str]] = None) -> List[Dict]:
    """Check if a username or email exists across different platforms
    
    Args:
        query: The username or email to check
        query_type: Type of query ("Username" or "Email")
        platforms: List of platforms to check, or None for all platforms
        
    Returns:
        List of dictionaries with results
    """
    checker = UsernameChecker()
    results = []
    
    # For email checks
    if query_type.lower() == "email":
        # Perform email validation
        email_result = checker.check_email(query)
        results.append({
            "platform": "Email Validation",
            "url": f"mailto:{query}",
            "exists": email_result.get("deliverable", False),
            "details": email_result.get("result", "Unknown")
        })
        
        # We can't easily check most platforms for email existence without API keys
        # So we'll just return the email validation result
        return results
    
    # For username checks
    available_platforms = list(checker.platforms.keys())
    
    # Filter platforms based on input
    if platforms and len(platforms) > 0:
        check_platforms = [p for p in platforms if p in available_platforms]
    else:
        check_platforms = available_platforms
    
    # Use ThreadPoolExecutor for parallel checks
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_platform = {
            executor.submit(checker.check_platform, platform, query): platform
            for platform in check_platforms if checker.platforms[platform].get("username_only", False)
        }
        
        for future in as_completed(future_to_platform):
            platform = future_to_platform[future]
            try:
                result = future.result()
                results.append({
                    "platform": result["platform"],
                    "url": result["url"],
                    "exists": result["exists"],
                    "status_code": result["status_code"],
                    "error": result["error"]
                })
            except Exception as exc:
                results.append({
                    "platform": platform,
                    "url": checker.platforms[platform]["url"].format(username=query),
                    "exists": False,
                    "status_code": None,
                    "error": str(exc)
                })
    
    # Sort results by existence (True first)
    results = sorted(results, key=lambda x: (not x["exists"], x["platform"]))
    
    return results
