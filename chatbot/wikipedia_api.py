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
    # Clean and format query for Wikipedia
    title = query.strip().replace(" ", "_")
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
    
    headers = {
        "User-Agent": "KattralAI/1.0 (Educational Assistant)"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            # Try search API if direct lookup fails
            return wikipedia_search(query)
        
        data = response.json()
        
        # Get extract (summary)
        extract = data.get("extract", "")
        
        if not extract:
            return "No summary available for this topic."
        
        return extract
        
    except Exception as e:
        print(f"Wikipedia API error: {e}")
        return "Sorry, I could not fetch information from Wikipedia at this time."


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
        response = requests.get(search_url, params=params, timeout=10)
        data = response.json()
        
        search_results = data.get("query", {}).get("search", [])
        
        if not search_results:
            return "No Wikipedia articles found for this query."
        
        # Get the title of the top result
        top_result = search_results[0]["title"]
        
        # Now get the summary for this title
        return wikipedia_answer(top_result)
        
    except Exception as e:
        print(f"Wikipedia search error: {e}")
        return "Sorry, I could not search Wikipedia at this time."


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
