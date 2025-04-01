import requests
import time
import random
from bs4 import BeautifulSoup
from typing import Dict, List, Any, Optional

def search_dark_web(query: str, search_type: str = "General") -> Dict[str, List[Dict[str, Any]]]:
    """
    Search for information across various dark web search engines and indexes.
    Note: This only queries legal dark web search engines and archives, not
    directly accessing any illegal content.
    
    Args:
        query: Search query
        search_type: Type of search (General, Data Breaches, Forums, Marketplaces, Comprehensive)
        
    Returns:
        Dictionary with source names as keys and lists of results as values
    """
    results = {}
    
    # User agent rotation to avoid blocking
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    ]
    
    # Function to make requests with random user agent
    def make_request(url, params=None):
        headers = {
            "User-Agent": random.choice(user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.google.com/",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error making request to {url}: {e}")
            return None
    
    # 1. Search IntelX (Public access)
    if search_type in ["General", "Comprehensive", "Data Breaches"]:
        try:
            # IntelX uses a different interface for public access
            intelx_url = f"https://intelx.io/tools?q={query}"
            response = make_request(intelx_url)
            
            if response and response.status_code == 200:
                results["IntelX"] = []
                soup = BeautifulSoup(response.text, 'html.parser')
                results_container = soup.find('div', {'class': 'results-container'})
                
                if results_container:
                    result_items = results_container.find_all('div', {'class': 'result-item'})
                    
                    for item in result_items:
                        try:
                            title_elem = item.find('h4')
                            desc_elem = item.find('p', {'class': 'description'})
                            date_elem = item.find('span', {'class': 'date'})
                            
                            title = title_elem.text.strip() if title_elem else "Unknown"
                            description = desc_elem.text.strip() if desc_elem else "No description available"
                            date = date_elem.text.strip() if date_elem else "Unknown date"
                            
                            results["IntelX"].append({
                                "title": title,
                                "description": description,
                                "date": date,
                                "source": "IntelX"
                            })
                        except Exception as e:
                            continue
                
                # If no structured results found, provide a link to manual search
                if not results["IntelX"]:
                    results["IntelX"].append({
                        "title": "IntelX Search",
                        "description": f"Search query '{query}' on IntelX manually",
                        "url": intelx_url,
                        "source": "IntelX"
                    })
        except Exception as e:
            results["IntelX"] = [{
                "title": "Error",
                "description": f"Error searching IntelX: {str(e)}",
                "source": "IntelX"
            }]
        
        # Add random delay between requests
        time.sleep(random.uniform(1, 2))
    
    # 2. Search HaveIBeenPwned (for Data Breaches - this normally requires an API key)
    if search_type in ["Data Breaches", "Comprehensive"]:
        results["HaveIBeenPwned"] = [{
            "title": "Manual Check Required",
            "description": f"Check if '{query}' is in data breaches on HaveIBeenPwned",
            "url": f"https://haveibeenpwned.com/",
            "source": "HaveIBeenPwned",
            "note": "API access requires authentication. Please visit the website directly."
        }]
    
    # 3. Search Dehashed (simulated - would require API key in real implementation)
    if search_type in ["Data Breaches", "Comprehensive"]:
        results["Dehashed"] = [{
            "title": "Manual Check Required",
            "description": f"Search for '{query}' in data breach records on Dehashed",
            "url": f"https://www.dehashed.com/search?query={query}",
            "source": "Dehashed",
            "note": "API access requires authentication. Please visit the website directly."
        }]
    
    # 4. Search Ahmia (Clear web search engine for .onion sites)
    if search_type in ["General", "Comprehensive"]:
        try:
            ahmia_url = "https://ahmia.fi/search"
            params = {"q": query}
            response = make_request(ahmia_url, params)
            
            if response and response.status_code == 200:
                results["Ahmia"] = []
                soup = BeautifulSoup(response.text, 'html.parser')
                result_items = soup.find_all('li', {'class': 'result'})
                
                for item in result_items:
                    try:
                        title_elem = item.find('h4')
                        link_elem = item.find('a', {'class': 'onion-link'})
                        desc_elem = item.find('p', {'class': 'description'})
                        
                        title = title_elem.text.strip() if title_elem else "Unknown"
                        onion_link = link_elem['href'] if link_elem else "#"
                        description = desc_elem.text.strip() if desc_elem else "No description available"
                        
                        # Clean up the results
                        if "ahmia.fi/search/search/redirect" in onion_link:
                            onion_link = onion_link.split("?url=")[1] if "?url=" in onion_link else onion_link
                        
                        results["Ahmia"].append({
                            "title": title,
                            "url": onion_link,
                            "description": description,
                            "source": "Ahmia"
                        })
                    except Exception as e:
                        continue
                
                # If no results found, provide a link to manual search
                if not results["Ahmia"]:
                    results["Ahmia"].append({
                        "title": "Ahmia Search",
                        "description": f"Search query '{query}' on Ahmia manually",
                        "url": f"{ahmia_url}?q={query}",
                        "source": "Ahmia"
                    })
        except Exception as e:
            results["Ahmia"] = [{
                "title": "Error",
                "description": f"Error searching Ahmia: {str(e)}",
                "source": "Ahmia"
            }]
        
        time.sleep(random.uniform(1, 2))
    
    # 5. Search DarkSearch.io (would require API key in real implementation)
    if search_type in ["General", "Forums", "Marketplaces", "Comprehensive"]:
        results["DarkSearch"] = [{
            "title": "Manual Check Required",
            "description": f"Search for '{query}' on dark web through DarkSearch.io",
            "url": f"https://darksearch.io/",
            "source": "DarkSearch",
            "note": "API access requires authentication. Please visit the website directly."
        }]
    
    # 6. Check ExploitDB (for vulnerabilities and exploits)
    if search_type in ["General", "Comprehensive"]:
        try:
            exploit_db_url = "https://www.exploit-db.com/search"
            params = {"q": query}
            response = make_request(exploit_db_url, params)
            
            if response and response.status_code == 200:
                results["ExploitDB"] = []
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # ExploitDB uses a DataTable, so direct parsing might be limited
                # We'll extract what we can or provide a direct link
                table = soup.find('table', {'id': 'exploits-table'})
                
                if table:
                    rows = table.find('tbody').find_all('tr')
                    
                    for row in rows:
                        try:
                            cells = row.find_all('td')
                            if len(cells) >= 5:
                                exploit_id = cells[0].text.strip()
                                exploit_description = cells[2].text.strip()
                                date = cells[3].text.strip()
                                exploit_type = cells[5].text.strip()
                                
                                results["ExploitDB"].append({
                                    "id": exploit_id,
                                    "title": exploit_description,
                                    "date": date,
                                    "type": exploit_type,
                                    "url": f"https://www.exploit-db.com/exploits/{exploit_id}",
                                    "source": "ExploitDB"
                                })
                        except Exception as e:
                            continue
                
                # If no results found or could not parse, provide a link to manual search
                if not results.get("ExploitDB") or not results["ExploitDB"]:
                    results["ExploitDB"] = [{
                        "title": "ExploitDB Search",
                        "description": f"Search query '{query}' on ExploitDB manually",
                        "url": f"{exploit_db_url}?q={query}",
                        "source": "ExploitDB"
                    }]
        except Exception as e:
            results["ExploitDB"] = [{
                "title": "Error",
                "description": f"Error searching ExploitDB: {str(e)}",
                "source": "ExploitDB"
            }]
        
        time.sleep(random.uniform(1, 2))
    
    # 7. Check Pastebin (via Google dork since direct API requires key)
    if search_type in ["Data Breaches", "Comprehensive"]:
        pastebin_search_url = f"https://www.google.com/search?q=site:pastebin.com+{query}"
        results["Pastebin"] = [{
            "title": "Pastebin Google Search",
            "description": f"Search for '{query}' on Pastebin through Google",
            "url": pastebin_search_url,
            "source": "Pastebin",
            "note": "Direct API access requires authentication. This link uses Google to search Pastebin."
        }]
    
    # 8. ForumSearch (simulated for forums)
    if search_type in ["Forums", "Comprehensive"]:
        results["ForumSearch"] = [{
            "title": "Forum Search",
            "description": f"Search for '{query}' across dark web forums",
            "note": "Specialized forum searching would require API keys for dedicated OSINT services like Flashpoint, Recorded Future, etc.",
            "source": "ForumSearch"
        }]
    
    # 9. Marketplace search (simulated)
    if search_type in ["Marketplaces", "Comprehensive"]:
        results["MarketSearch"] = [{
            "title": "Market Search",
            "description": f"Search for '{query}' across dark web marketplaces",
            "note": "Specialized marketplace searching would require API keys for dedicated OSINT services like Sixgill, Flare Systems, etc.",
            "source": "MarketSearch"
        }]
    
    # If no results were found at all
    if not results:
        results["General"] = [{
            "title": "No Results",
            "description": f"No results found for '{query}' with search type '{search_type}'",
            "source": "General"
        }]
    
    return results
