import requests
import socket
import ipaddress
from typing import Dict, Any, Optional

def is_valid_ip(ip: str) -> bool:
    """
    Check if the given string is a valid IP address.
    
    Args:
        ip: IP address to validate
        
    Returns:
        Boolean indicating whether the IP is valid
    """
    try:
        ipaddress.ip_address(ip)
        return True
    except ValueError:
        return False

def get_hostname(ip: str) -> Optional[str]:
    """
    Attempt to get the hostname for an IP address through reverse DNS lookup.
    
    Args:
        ip: IP address to lookup
        
    Returns:
        Hostname if found, None otherwise
    """
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except (socket.herror, socket.gaierror):
        return None

def get_ip_geolocation(ip: str) -> Dict[str, Any]:
    """
    Get geolocation data for an IP address.
    
    Args:
        ip: IP address to geolocate
        
    Returns:
        Dictionary containing geolocation information
    """
    # Validate IP address
    if not is_valid_ip(ip):
        try:
            # Try to resolve hostname to IP
            ip = socket.gethostbyname(ip)
        except socket.gaierror:
            return {"error": "Invalid IP address or hostname"}
    
    # Check if IP is in a private range
    try:
        ip_obj = ipaddress.ip_address(ip)
        if ip_obj.is_private:
            return {
                "ip": ip,
                "error": "This is a private IP address and cannot be geolocated",
                "is_private": True
            }
        elif ip_obj.is_loopback:
            return {
                "ip": ip,
                "error": "This is a loopback address and cannot be geolocated",
                "is_loopback": True
            }
        elif ip_obj.is_link_local:
            return {
                "ip": ip,
                "error": "This is a link-local address and cannot be geolocated",
                "is_link_local": True
            }
    except ValueError:
        return {"error": "Invalid IP address format"}
    
    # Try to get hostname
    hostname = get_hostname(ip)
    
    # Use ip-api.com for geolocation (free, no API key required for moderate usage)
    url = f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,region,regionName,city,zip,lat,lon,timezone,isp,org,as,query"
    
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        
        if data.get("status") == "success":
            result = {
                "ip": data.get("query", ip),
                "country": data.get("country"),
                "country_code": data.get("countryCode"),
                "region": data.get("regionName"),
                "city": data.get("city"),
                "zip": data.get("zip"),
                "lat": data.get("lat"),
                "lon": data.get("lon"),
                "timezone": data.get("timezone"),
                "isp": data.get("isp"),
                "org": data.get("org"),
                "as": data.get("as")
            }
            
            # Add hostname if available
            if hostname:
                result["hostname"] = hostname
                
            return result
        else:
            return {
                "ip": ip,
                "error": data.get("message", "Failed to retrieve geolocation data")
            }
    except Exception as e:
        return {
            "ip": ip,
            "error": f"Error retrieving geolocation data: {str(e)}"
        }

def get_additional_ip_info(ip: str) -> Dict[str, Any]:
    """
    Get additional information about an IP address, such as threat intelligence data.
    This is a placeholder function that would typically use a paid API service.
    
    Args:
        ip: IP address to check
        
    Returns:
        Dictionary containing threat intelligence data
    """
    # This would typically use a service like AbuseIPDB, VirusTotal, etc.
    # For now, we'll return a placeholder message
    return {
        "ip": ip,
        "note": "Additional IP threat intelligence would require API keys for services like AbuseIPDB, VirusTotal, etc."
    }
