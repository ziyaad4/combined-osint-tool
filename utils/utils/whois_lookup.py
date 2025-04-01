import socket
import whois
import datetime
import ipaddress
import time
from typing import Dict, Any, Optional, Union, List

def is_valid_domain(domain: str) -> bool:
    """
    Check if a string is a valid domain name.
    
    Args:
        domain: Domain name to check
        
    Returns:
        Boolean indicating whether the domain is valid
    """
    # Simple validation - ensure domain has at least one dot and no spaces
    if ' ' in domain or '.' not in domain:
        return False
    
    # Check if it's an IP address
    try:
        ipaddress.ip_address(domain)
        return False  # It's an IP, not a domain
    except ValueError:
        pass
    
    # Check TLD validity
    tld = domain.split('.')[-1]
    common_tlds = {
        'com', 'net', 'org', 'edu', 'gov', 'mil', 'int', 'io', 'co', 'ai',
        'app', 'dev', 'info', 'biz', 'name', 'pro', 'blog', 'shop', 'site',
        'uk', 'us', 'ca', 'au', 'de', 'fr', 'jp', 'ru', 'ch', 'it', 'nl',
        'se', 'no', 'es', 'me', 'tv', 'xyz'
    }
    
    if tld.lower() not in common_tlds and len(tld) not in [2, 3]:
        # Not a common TLD or a country code (approximately)
        return False
    
    return True

def format_whois_date(date_value: Optional[Union[str, datetime.datetime, List]]) -> str:
    """
    Format WHOIS date values (handles various formats returned by python-whois).
    
    Args:
        date_value: Date value to format (can be string, datetime, or list of either)
        
    Returns:
        Formatted date string
    """
    if not date_value:
        return "Not available"
    
    if isinstance(date_value, list):
        if not date_value:
            return "Not available"
        # Use the first date in the list
        date_value = date_value[0]
    
    if isinstance(date_value, datetime.datetime):
        return date_value.strftime("%Y-%m-%d")
    
    if isinstance(date_value, str):
        # Try to parse common date formats
        date_formats = [
            "%Y-%m-%d",
            "%d-%m-%Y",
            "%Y.%m.%d",
            "%d.%m.%Y",
            "%Y/%m/%d",
            "%d/%m/%Y"
        ]
        
        for fmt in date_formats:
            try:
                parsed_date = datetime.datetime.strptime(date_value, fmt)
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        # If we couldn't parse it, return as is
        return date_value
    
    return str(date_value)

def extract_contact_info(whois_data: Dict[str, Any], field_prefix: str) -> Dict[str, Any]:
    """
    Extract contact information from WHOIS data for different contact types.
    
    Args:
        whois_data: WHOIS data dictionary
        field_prefix: Prefix for contact fields (e.g., "admin", "registrant", "tech")
        
    Returns:
        Dictionary containing contact information
    """
    contact_info = {}
    
    # Fields to extract
    fields = [
        "name",
        "organization",
        "street",
        "city",
        "state",
        "postal_code",
        "country",
        "phone",
        "fax",
        "email"
    ]
    
    # Extract fields with the given prefix
    for field in fields:
        full_field = f"{field_prefix}_{field}"
        if full_field in whois_data and whois_data[full_field]:
            contact_info[field] = whois_data[full_field]
    
    return contact_info

def whois_lookup(domain: str) -> Dict[str, Any]:
    """
    Perform a WHOIS lookup for a domain name.
    
    Args:
        domain: Domain name to lookup
        
    Returns:
        Dictionary containing WHOIS information
    """
    # Clean the domain input
    domain = domain.strip().lower()
    
    # Validate domain
    if not is_valid_domain(domain):
        return {"error": f"Invalid domain name: {domain}"}
    
    try:
        # Perform WHOIS lookup
        whois_data = whois.whois(domain)
        
        if not whois_data or not whois_data.domain_name:
            return {"error": f"No WHOIS data found for domain: {domain}"}
        
        # Store the raw WHOIS text
        raw_text = whois_data.text
        
        # Convert the WHOIS data to a dictionary
        result = {
            "domain_name": whois_data.domain_name,
            "registrar": whois_data.registrar,
            "whois_server": whois_data.whois_server,
            "referral_url": whois_data.referral_url,
            "updated_date": format_whois_date(whois_data.updated_date),
            "creation_date": format_whois_date(whois_data.creation_date),
            "expiration_date": format_whois_date(whois_data.expiration_date),
            "name_servers": whois_data.name_servers,
            "status": whois_data.status,
            "raw": raw_text
        }
        
        # Extract contact information
        registrant_info = extract_contact_info(whois_data, "registrant")
        if registrant_info:
            result["registrant"] = registrant_info
        
        admin_info = extract_contact_info(whois_data, "admin")
        if admin_info:
            result["admin"] = admin_info
        
        tech_info = extract_contact_info(whois_data, "tech")
        if tech_info:
            result["tech"] = tech_info
        
        # Try to get abuse contact if available
        if hasattr(whois_data, "abuse_contact_email") and whois_data.abuse_contact_email:
            result["abuse_contact"] = {
                "email": whois_data.abuse_contact_email,
                "phone": getattr(whois_data, "abuse_contact_phone", "Not available")
            }
        
        # Try to get DNSSEC information if available
        if hasattr(whois_data, "dnssec") and whois_data.dnssec:
            result["dnssec"] = whois_data.dnssec
        
        return result
    
    except whois.parser.PywhoisError as e:
        return {"error": f"WHOIS error: {str(e)}"}
    
    except Exception as e:
        return {"error": f"Error performing WHOIS lookup: {str(e)}"}

def whois_ip_lookup(ip: str) -> Dict[str, Any]:
    """
    Perform a WHOIS lookup for an IP address.
    
    Args:
        ip: IP address to lookup
        
    Returns:
        Dictionary containing WHOIS information for the IP
    """
    # Validate IP address
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        return {"error": f"Invalid IP address: {ip}"}
    
    try:
        # For IP WHOIS, we'd typically use a different library or service
        # As a workaround, we'll return a placeholder with ARIN WHOIS lookup URL
        return {
            "ip": ip,
            "note": "IP WHOIS lookups require different tools than domain WHOIS lookups.",
            "lookup_urls": [
                f"https://search.arin.net/rdap/?query={ip}",
                f"https://whois.arin.net/rest/ip/{ip}"
            ],
            "manual_lookup": "For accurate IP WHOIS data, use one of the lookup URLs provided."
        }
    
    except Exception as e:
        return {"error": f"Error performing IP WHOIS lookup: {str(e)}"}
