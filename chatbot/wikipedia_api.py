"""
Wikipedia API Integration
Provides answers from Wikipedia for educational queries
"""
import requests


def wikipedia_answer(query):
    """
    Get Wikipedia summary for a query
    
    Args:
        query: Search query
        
    Returns:
        Wikipedia summary text
    """
    if not query or not query.strip():
        return "Please provide a search query."
    
    # Clean and format query for Wikipedia
    title = query.strip().replace(" ", "_")
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    try:
        print(f"[WIKIPEDIA] Fetching: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        
        print(f"[WIKIPEDIA] Status code: {response.status_code}")
        
        if response.status_code == 404:
            # Page not found, try search
            print(f"[WIKIPEDIA] Page not found, trying search...")
            return wikipedia_search(query)
        
        if response.status_code != 200:
            print(f"[WIKIPEDIA] Error response: {response.text[:200]}")
            return wikipedia_search(query)
        
        data = response.json()
        
        # Get extract (summary)
        extract = data.get("extract", "")
        
        if not extract:
            print(f"[WIKIPEDIA] No extract found, trying search...")
            return wikipedia_search(query)
        
        print(f"[WIKIPEDIA] Success! Got {len(extract)} characters")
        return extract
        
    except requests.exceptions.Timeout:
        print(f"[WIKIPEDIA] Timeout error")
        return "Wikipedia request timed out. Please try again."
    except requests.exceptions.ConnectionError:
        print(f"[WIKIPEDIA] Connection error")
        return "Could not connect to Wikipedia. Please check your internet connection."
    except Exception as e:
        print(f"[WIKIPEDIA] Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return f"Sorry, I could not fetch information from Wikipedia. Error: {str(e)}"


def wikipedia_search(query):
    """
    Search Wikipedia and get summary of top result
    
    Args:
        query: Search query
        
    Returns:
        Summary of top search result
    """
    search_url = "https://en.wikipedia.org/w/api.php"
    
    params = {
        "action": "query",
        "format": "json",
        "list": "search",
        "srsearch": query,
        "srlimit": 1
    }
    
    try:
        print(f"[WIKIPEDIA SEARCH] Searching for: {query}")
        response = requests.get(search_url, params=params, timeout=10)
        
        print(f"[WIKIPEDIA SEARCH] Status: {response.status_code}")
        
        if response.status_code != 200:
            return f"Wikipedia search failed with status {response.status_code}"
        
        data = response.json()
        
        search_results = data.get("query", {}).get("search", [])
        
        if not search_results:
            print(f"[WIKIPEDIA SEARCH] No results found")
            return f"No Wikipedia articles found for '{query}'. Try a different search term."
        
        # Get the title of the top result
        top_result = search_results[0]["title"]
        print(f"[WIKIPEDIA SEARCH] Top result: {top_result}")
        
        # Now get the summary for this title (avoid infinite recursion)
        title = top_result.replace(" ", "_")
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            extract = data.get("extract", "")
            if extract:
                return extract
        
        return f"Found article '{top_result}' but could not retrieve summary."
        
    except requests.exceptions.Timeout:
        print(f"[WIKIPEDIA SEARCH] Timeout")
        return "Wikipedia search timed out. Please try again."
    except requests.exceptions.ConnectionError:
        print(f"[WIKIPEDIA SEARCH] Connection error")
        return "Could not connect to Wikipedia. Please check your internet connection."
    except Exception as e:
        print(f"[WIKIPEDIA SEARCH] Error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return f"Sorry, I could not search Wikipedia. Error: {str(e)}"


def get_wikipedia_content(topic, max_length=500):
    """
    Get Wikipedia content with length limit
    
    Args:
        topic: Topic to search
        max_length: Maximum characters to return
        
    Returns:
        Truncated Wikipedia content
    """
    content = wikipedia_answer(topic)
    
    if len(content) > max_length:
        # Truncate and add ellipsis
        content = content[:max_length].rsplit(' ', 1)[0] + "..."
    
    return content
