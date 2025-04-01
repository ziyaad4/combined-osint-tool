import dns.resolver
import dns.reversename
import dns.exception
import socket
import time
import ipaddress
from typing import Dict, List, Any, Optional

def dns_enumeration(domain: str, record_types: Optional[List[str]] = None) -> Dict[str, List[Dict[str, Any]]]:
    """
    Perform DNS enumeration on a domain to discover various DNS records.
    
    Args:
        domain: Domain name to enumerate
        record_types: List of DNS record types to query
        
    Returns:
        Dictionary with record types as keys and lists of records as values
    """
    if not record_types:
        record_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]
    
    results = {}
    resolver = dns.resolver.Resolver()
    resolver.timeout = 3
    resolver.lifetime = 3
    
    # Function to safely query DNS records
    def query_records(domain, record_type):
        records = []
        try:
            answers = resolver.resolve(domain, record_type)
            for rdata in answers:
                if record_type == "A":
                    records.append({
                        "value": rdata.address,
                        "ttl": answers.ttl
                    })
                    # Try reverse DNS lookup
                    try:
                        reverse_name = dns.reversename.from_address(rdata.address)
                        reverse_answers = resolver.resolve(reverse_name, "PTR")
                        for reverse_data in reverse_answers:
                            records[-1]["reverse_dns"] = str(reverse_data).rstrip(".")
                    except:
                        records[-1]["reverse_dns"] = "Not available"
                
                elif record_type == "AAAA":
                    records.append({
                        "value": rdata.address,
                        "ttl": answers.ttl
                    })
                
                elif record_type == "MX":
                    records.append({
                        "preference": rdata.preference,
                        "exchange": str(rdata.exchange).rstrip("."),
                        "ttl": answers.ttl
                    })
                    # Try to get the IP of the mail server
                    try:
                        mx_ip = resolver.resolve(str(rdata.exchange), "A")
                        records[-1]["ip"] = mx_ip[0].address
                    except:
                        records[-1]["ip"] = "Not available"
                
                elif record_type == "NS":
                    nameserver = str(rdata).rstrip(".")
                    records.append({
                        "nameserver": nameserver,
                        "ttl": answers.ttl
                    })
                    # Try to get the IP of the nameserver
                    try:
                        ns_ip = resolver.resolve(nameserver, "A")
                        records[-1]["ip"] = ns_ip[0].address
                    except:
                        records[-1]["ip"] = "Not available"
                
                elif record_type == "TXT":
                    records.append({
                        "value": str(rdata).strip('"'),
                        "ttl": answers.ttl
                    })
                
                elif record_type == "CNAME":
                    records.append({
                        "target": str(rdata).rstrip("."),
                        "ttl": answers.ttl
                    })
                
                elif record_type == "SOA":
                    records.append({
                        "mname": str(rdata.mname).rstrip("."),
                        "rname": str(rdata.rname).rstrip("."),
                        "serial": rdata.serial,
                        "refresh": rdata.refresh,
                        "retry": rdata.retry,
                        "expire": rdata.expire,
                        "minimum": rdata.minimum,
                        "ttl": answers.ttl
                    })
                    
        except dns.resolver.NXDOMAIN:
            pass
        except dns.resolver.NoAnswer:
            pass
        except dns.exception.Timeout:
            pass
        except Exception as e:
            records.append({
                "error": str(e)
            })
            
        return records
    
    # Process each record type
    for record_type in record_types:
        results[record_type] = query_records(domain, record_type)
    
    # Try zone transfer (usually blocked by most servers, but worth trying)
    if "NS" in results and results["NS"]:
        results["AXFR"] = []
        for ns_record in results["NS"]:
            nameserver = ns_record.get("nameserver")
            if nameserver:
                try:
                    xfr = dns.query.xfr(nameserver, domain, timeout=5)
                    zone = dns.zone.from_xfr(xfr)
                    for name, node in zone.nodes.items():
                        for rdataset in node.rdatasets:
                            for rdata in rdataset:
                                results["AXFR"].append({
                                    "name": str(name),
                                    "type": dns.rdatatype.to_text(rdataset.rdtype),
                                    "value": str(rdata)
                                })
                except:
                    # Zone transfers are almost always disabled
                    pass
    
    # If we found IP addresses, try to get additional information
    if "A" in results and results["A"]:
        results["Additional"] = []
        for a_record in results["A"]:
            ip = a_record.get("value")
            if ip:
                # Check if the IP is in a private range
                try:
                    if ipaddress.ip_address(ip).is_private:
                        results["Additional"].append({
                            "ip": ip,
                            "info": "Private IP address range"
                        })
                        continue
                except:
                    pass
                
                # Try to get hostname
                try:
                    hostname = socket.gethostbyaddr(ip)[0]
                    results["Additional"].append({
                        "ip": ip,
                        "hostname": hostname
                    })
                except:
                    pass
    
    # Check common subdomains
    common_subdomains = [
        "www", "mail", "ftp", "webmail", "admin", "blog", 
        "dev", "test", "staging", "api", "vpn", "ns1", "ns2",
        "smtp", "pop", "imap", "cloud", "mobile", "app",
        "support", "shop", "portal", "cdn", "secure"
    ]
    
    results["Subdomains"] = []
    for subdomain in common_subdomains:
        full_domain = f"{subdomain}.{domain}"
        try:
            answers = resolver.resolve(full_domain, "A")
            for rdata in answers:
                results["Subdomains"].append({
                    "subdomain": full_domain,
                    "ip": rdata.address,
                    "ttl": answers.ttl
                })
        except:
            pass
        
        # Don't overload the DNS server
        time.sleep(0.1)
    
    return results
