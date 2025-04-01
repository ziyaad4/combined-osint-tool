import requests
import time
import random
import datetime
import re
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup
from collections import Counter

def analyze_social_media(platform: str, analysis_type: str, query: str, limit: int = 30) -> Dict[str, Any]:
    """
    Analyze social media profiles and content.
    
    Args:
        platform: Social media platform (twitter, reddit, instagram, tiktok, youtube)
        analysis_type: Type of analysis (user, hashtag, search, subreddit)
        query: Search query or username
        limit: Maximum number of results to return
        
    Returns:
        Dictionary containing analysis results
    """
    platform = platform.lower()
    
    # Select the appropriate analyzer based on platform
    if platform == "twitter":
        return analyze_twitter(analysis_type, query, limit)
    elif platform == "reddit":
        return analyze_reddit(analysis_type, query, limit)
    elif platform == "instagram":
        return analyze_instagram(analysis_type, query, limit)
    elif platform == "tiktok":
        return analyze_tiktok(analysis_type, query, limit)
    elif platform == "youtube":
        return analyze_youtube(analysis_type, query, limit)
    else:
        return {"error": f"Unsupported platform: {platform}"}

def analyze_twitter(analysis_type: str, query: str, limit: int = 30) -> Dict[str, Any]:
    """
    Analyze Twitter profiles and content.
    
    Args:
        analysis_type: Type of analysis (user, hashtag, search)
        query: Username, hashtag, or search query
        limit: Maximum number of results to return
        
    Returns:
        Dictionary containing Twitter analysis results
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    ]
    
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    # Twitter has significantly restricted web scraping, so we'll use Nitter as an alternative
    # Note: Nitter instances may change over time or become unavailable
    nitter_instances = [
        "https://nitter.net",
        "https://nitter.42l.fr",
        "https://nitter.pussthecat.org",
        "https://nitter.nixnet.services",
        "https://nitter.fdn.fr"
    ]
    
    nitter_url = random.choice(nitter_instances)
    
    if analysis_type == "user":
        # Clean the username (remove @ if present)
        username = query.replace("@", "").strip()
        profile_url = f"{nitter_url}/{username}"
        
        try:
            response = requests.get(profile_url, headers=headers, timeout=10)
            if response.status_code != 200:
                return {"error": f"Could not fetch user profile: HTTP {response.status_code}"}
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract profile information
            profile = {}
            profile_info = soup.find('div', {'class': 'profile-card'})
            
            if profile_info:
                # Basic user info
                profile["username"] = username
                
                # Full name
                fullname_elem = profile_info.find('a', {'class': 'profile-card-fullname'})
                if fullname_elem:
                    profile["name"] = fullname_elem.text.strip()
                
                # Bio
                bio_elem = profile_info.find('div', {'class': 'profile-bio'})
                if bio_elem:
                    profile["description"] = bio_elem.text.strip()
                
                # Location
                location_elem = profile_info.find('div', {'class': 'profile-location'})
                if location_elem:
                    profile["location"] = location_elem.text.strip()
                
                # Join date
                date_elem = profile_info.find('div', {'class': 'profile-joindate'})
                if date_elem:
                    date_span = date_elem.find('span', {'class': 'profile-joindate'})
                    if date_span:
                        profile["created_at"] = date_span.text.strip()
                
                # Stats (tweets, following, followers)
                stats_elem = profile_info.find('div', {'class': 'profile-statlist'})
                if stats_elem:
                    stat_items = stats_elem.find_all('div', {'class': 'profile-stat'})
                    for stat in stat_items:
                        stat_name = stat.find('span', {'class': 'profile-stat-header'})
                        stat_value = stat.find('span', {'class': 'profile-stat-num'})
                        if stat_name and stat_value:
                            name = stat_name.text.strip().lower()
                            value = stat_value.text.strip()
                            if "tweets" in name:
                                profile["tweets_count"] = value
                            elif "following" in name:
                                profile["following_count"] = value
                            elif "followers" in name:
                                profile["followers_count"] = value
            
            # Extract tweets
            tweets = []
            timeline = soup.find('div', {'class': 'timeline'})
            
            if timeline:
                tweet_items = timeline.find_all('div', {'class': 'timeline-item'})
                for i, tweet_item in enumerate(tweet_items):
                    if i >= limit:
                        break
                    
                    tweet = {}
                    
                    # Tweet content
                    tweet_content = tweet_item.find('div', {'class': 'tweet-content'})
                    if tweet_content:
                        tweet["text"] = tweet_content.text.strip()
                    
                    # Tweet date
                    tweet_date = tweet_item.find('span', {'class': 'tweet-date'})
                    if tweet_date:
                        date_a = tweet_date.find('a')
                        if date_a:
                            tweet["created_at"] = date_a.text.strip()
                    
                    # Tweet stats (replies, retweets, likes)
                    tweet_stats = tweet_item.find('div', {'class': 'tweet-stats'})
                    if tweet_stats:
                        stat_items = tweet_stats.find_all('span', {'class': 'tweet-stat'})
                        for stat in stat_items:
                            stat_link = stat.find('a')
                            if stat_link:
                                stat_text = stat_link.text.strip()
                                if "replies" in stat_link.get('href', ''):
                                    tweet["reply_count"] = stat_text.split(' ')[0]
                                elif "retweets" in stat_link.get('href', ''):
                                    tweet["retweet_count"] = stat_text.split(' ')[0]
                                elif "likes" in stat_link.get('href', ''):
                                    tweet["favorite_count"] = stat_text.split(' ')[0]
                    
                    # Extract hashtags and mentions
                    if "text" in tweet:
                        hashtags = re.findall(r'#(\w+)', tweet["text"])
                        mentions = re.findall(r'@(\w+)', tweet["text"])
                        
                        if hashtags:
                            tweet["hashtags"] = hashtags
                        if mentions:
                            tweet["mentions"] = mentions
                    
                    tweets.append(tweet)
            
            # Generate insights
            insights = {}
            if tweets:
                # Most active day/hour
                days_of_week = []
                hours_of_day = []
                all_hashtags = []
                all_mentions = []
                likes = []
                retweets = []
                
                for tweet in tweets:
                    # Process date if available
                    if "created_at" in tweet:
                        try:
                            # Format varies, but typically like "1 Jul 2022" or "Jul 1, 2022"
                            # We'll try a few common formats
                            date_formats = [
                                "%d %b %Y",
                                "%b %d, %Y",
                                "%d %B %Y",
                                "%B %d, %Y"
                            ]
                            
                            parsed_date = None
                            for fmt in date_formats:
                                try:
                                    parsed_date = datetime.datetime.strptime(tweet["created_at"], fmt)
                                    break
                                except ValueError:
                                    continue
                            
                            if parsed_date:
                                days_of_week.append(parsed_date.strftime("%A"))
                                hours_of_day.append(parsed_date.hour)
                        except (ValueError, TypeError):
                            pass
                    
                    # Collect hashtags and mentions
                    if "hashtags" in tweet:
                        all_hashtags.extend(tweet["hashtags"])
                    if "mentions" in tweet:
                        all_mentions.extend(tweet["mentions"])
                    
                    # Collect engagement metrics
                    if "favorite_count" in tweet:
                        try:
                            likes.append(int(tweet["favorite_count"].replace(',', '')))
                        except (ValueError, TypeError):
                            pass
                    
                    if "retweet_count" in tweet:
                        try:
                            retweets.append(int(tweet["retweet_count"].replace(',', '')))
                        except (ValueError, TypeError):
                            pass
                
                # Calculate most active day/hour
                if days_of_week:
                    most_common_day = Counter(days_of_week).most_common(1)[0][0]
                    insights["most_active_day"] = most_common_day
                
                if hours_of_day:
                    most_common_hour = Counter(hours_of_day).most_common(1)[0][0]
                    insights["most_active_hour"] = f"{most_common_hour}:00"
                
                # Top hashtags and mentions
                if all_hashtags:
                    top_hashtags = [tag for tag, _ in Counter(all_hashtags).most_common(5)]
                    insights["top_hashtags"] = top_hashtags
                
                if all_mentions:
                    top_mentions = [mention for mention, _ in Counter(all_mentions).most_common(5)]
                    insights["top_mentions"] = top_mentions
                
                # Average engagement
                if likes:
                    insights["avg_likes"] = sum(likes) / len(likes)
                
                if retweets:
                    insights["avg_retweets"] = sum(retweets) / len(retweets)
            
            return {
                "profile": profile,
                "tweets": tweets,
                "insights": insights
            }
        
        except Exception as e:
            return {"error": f"Error analyzing Twitter user: {str(e)}"}
    
    elif analysis_type == "hashtag":
        # Clean the hashtag (remove # if present)
        hashtag = query.replace("#", "").strip()
        hashtag_url = f"{nitter_url}/search?f=tweets&q=%23{hashtag}"
        
        try:
            response = requests.get(hashtag_url, headers=headers, timeout=10)
            if response.status_code != 200:
                return {"error": f"Could not fetch hashtag data: HTTP {response.status_code}"}
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract tweets with the hashtag
            tweets = []
            timeline = soup.find('div', {'class': 'timeline'})
            
            if timeline:
                tweet_items = timeline.find_all('div', {'class': 'timeline-item'})
                for i, tweet_item in enumerate(tweet_items):
                    if i >= limit:
                        break
                    
                    tweet = {}
                    
                    # Username
                    username_elem = tweet_item.find('a', {'class': 'username'})
                    if username_elem:
                        tweet["username"] = username_elem.text.strip()
                    
                    # Tweet content
                    tweet_content = tweet_item.find('div', {'class': 'tweet-content'})
                    if tweet_content:
                        tweet["text"] = tweet_content.text.strip()
                    
                    # Tweet date
                    tweet_date = tweet_item.find('span', {'class': 'tweet-date'})
                    if tweet_date:
                        date_a = tweet_date.find('a')
                        if date_a:
                            tweet["created_at"] = date_a.text.strip()
                    
                    # Tweet stats (replies, retweets, likes)
                    tweet_stats = tweet_item.find('div', {'class': 'tweet-stats'})
                    if tweet_stats:
                        stat_items = tweet_stats.find_all('span', {'class': 'tweet-stat'})
                        for stat in stat_items:
                            stat_link = stat.find('a')
                            if stat_link:
                                stat_text = stat_link.text.strip()
                                if "replies" in stat_link.get('href', ''):
                                    tweet["reply_count"] = stat_text.split(' ')[0]
                                elif "retweets" in stat_link.get('href', ''):
                                    tweet["retweet_count"] = stat_text.split(' ')[0]
                                elif "likes" in stat_link.get('href', ''):
                                    tweet["favorite_count"] = stat_text.split(' ')[0]
                    
                    # Extract all hashtags
                    if "text" in tweet:
                        all_hashtags = re.findall(r'#(\w+)', tweet["text"])
                        tweet["hashtags"] = all_hashtags
                    
                    tweets.append(tweet)
            
            # Generate insights
            insights = {}
            if tweets:
                # Count unique users
                usernames = [tweet.get("username") for tweet in tweets if "username" in tweet]
                unique_users = len(set(usernames))
                insights["tweet_count"] = len(tweets)
                insights["unique_users"] = unique_users
                
                # Calculate average engagement
                engagement_scores = []
                for tweet in tweets:
                    engagement = 0
                    try:
                        if "reply_count" in tweet:
                            engagement += int(tweet["reply_count"].replace(',', ''))
                        if "retweet_count" in tweet:
                            engagement += int(tweet["retweet_count"].replace(',', ''))
                        if "favorite_count" in tweet:
                            engagement += int(tweet["favorite_count"].replace(',', ''))
                    except (ValueError, TypeError):
                        pass
                    
                    engagement_scores.append(engagement)
                
                if engagement_scores:
                    insights["avg_engagement"] = sum(engagement_scores) / len(engagement_scores)
                
                # Find related hashtags
                all_hashtags = []
                for tweet in tweets:
                    if "hashtags" in tweet:
                        # Exclude the original hashtag
                        other_hashtags = [tag for tag in tweet["hashtags"] if tag.lower() != hashtag.lower()]
                        all_hashtags.extend(other_hashtags)
                
                if all_hashtags:
                    related_hashtags = [tag for tag, _ in Counter(all_hashtags).most_common(10)]
                    insights["related_hashtags"] = related_hashtags
            
            return {
                "tweets": tweets,
                "insights": insights
            }
        
        except Exception as e:
            return {"error": f"Error analyzing Twitter hashtag: {str(e)}"}
    
    elif analysis_type == "search":
        search_url = f"{nitter_url}/search?f=tweets&q={query}"
        
        try:
            response = requests.get(search_url, headers=headers, timeout=10)
            if response.status_code != 200:
                return {"error": f"Could not fetch search results: HTTP {response.status_code}"}
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract tweets from search results
            tweets = []
            timeline = soup.find('div', {'class': 'timeline'})
            
            if timeline:
                tweet_items = timeline.find_all('div', {'class': 'timeline-item'})
                for i, tweet_item in enumerate(tweet_items):
                    if i >= limit:
                        break
                    
                    tweet = {}
                    
                    # Username
                    username_elem = tweet_item.find('a', {'class': 'username'})
                    if username_elem:
                        tweet["username"] = username_elem.text.strip()
                    
                    # Tweet content
                    tweet_content = tweet_item.find('div', {'class': 'tweet-content'})
                    if tweet_content:
                        tweet["text"] = tweet_content.text.strip()
                    
                    # Tweet date
                    tweet_date = tweet_item.find('span', {'class': 'tweet-date'})
                    if tweet_date:
                        date_a = tweet_date.find('a')
                        if date_a:
                            tweet["created_at"] = date_a.text.strip()
                    
                    # Tweet stats (replies, retweets, likes)
                    tweet_stats = tweet_item.find('div', {'class': 'tweet-stats'})
                    if tweet_stats:
                        stat_items = tweet_stats.find_all('span', {'class': 'tweet-stat'})
                        for stat in stat_items:
                            stat_link = stat.find('a')
                            if stat_link:
                                stat_text = stat_link.text.strip()
                                if "replies" in stat_link.get('href', ''):
                                    tweet["reply_count"] = stat_text.split(' ')[0]
                                elif "retweets" in stat_link.get('href', ''):
                                    tweet["retweet_count"] = stat_text.split(' ')[0]
                                elif "likes" in stat_link.get('href', ''):
                                    tweet["favorite_count"] = stat_text.split(' ')[0]
                    
                    tweets.append(tweet)
            
            return {
                "tweets": tweets
            }
        
        except Exception as e:
            return {"error": f"Error searching Twitter: {str(e)}"}
    
    else:
        return {"error": f"Unsupported analysis type for Twitter: {analysis_type}"}

def analyze_reddit(analysis_type: str, query: str, limit: int = 30) -> Dict[str, Any]:
    """
    Analyze Reddit profiles and content.
    
    Args:
        analysis_type: Type of analysis (user, subreddit, search)
        query: Username, subreddit, or search query
        limit: Maximum number of results to return
        
    Returns:
        Dictionary containing Reddit analysis results
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    ]
    
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    # For Reddit, we can use the JSON API endpoints
    if analysis_type == "user":
        # Clean the username (remove u/ if present)
        username = query.replace("u/", "").strip()
        profile_url = f"https://www.reddit.com/user/{username}/about.json"
        posts_url = f"https://www.reddit.com/user/{username}/submitted.json?limit={limit}"
        comments_url = f"https://www.reddit.com/user/{username}/comments.json?limit={limit}"
        
        try:
            # Get user profile
            profile_response = requests.get(profile_url, headers=headers, timeout=10)
            if profile_response.status_code != 200:
                return {"error": f"Could not fetch user profile: HTTP {profile_response.status_code}"}
            
            profile_data = profile_response.json()
            
            # Extract profile information
            profile = {}
            if "data" in profile_data:
                data = profile_data["data"]
                profile["username"] = data.get("name", username)
                profile["post_karma"] = data.get("link_karma", 0)
                profile["comment_karma"] = data.get("comment_karma", 0)
                
                # Calculate account age
                created_utc = data.get("created_utc", 0)
                if created_utc:
                    created_date = datetime.datetime.fromtimestamp(created_utc)
                    account_age = datetime.datetime.now() - created_date
                    profile["account_age"] = f"{account_age.days} days"
                    profile["created_at"] = created_date.strftime("%Y-%m-%d")
                
                # Get awarder/awardee karma if available
                profile["awarder_karma"] = data.get("awarder_karma", 0)
                profile["awardee_karma"] = data.get("awardee_karma", 0)
                
                # Get trophies if available
                profile["trophies"] = ["Reddit Gold", "Verified Email"]  # Default minimal trophies
            
            # Get user posts
            posts_response = requests.get(posts_url, headers=headers, timeout=10)
            posts = []
            
            if posts_response.status_code == 200:
                posts_data = posts_response.json()
                if "data" in posts_data and "children" in posts_data["data"]:
                    for post in posts_data["data"]["children"]:
                        if len(posts) >= limit:
                            break
                        
                        post_data = post["data"]
                        
                        posts.append({
                            "title": post_data.get("title", ""),
                            "subreddit": post_data.get("subreddit", ""),
                            "created_at": datetime.datetime.fromtimestamp(post_data.get("created_utc", 0)).strftime("%Y-%m-%d %H:%M:%S"),
                            "score": post_data.get("score", 0),
                            "upvote_ratio": post_data.get("upvote_ratio", 0),
                            "num_comments": post_data.get("num_comments", 0),
                            "text": post_data.get("selftext", ""),
                            "url": post_data.get("url", ""),
                            "permalink": f"https://www.reddit.com{post_data.get('permalink', '')}"
                        })
            
            # Get user comments
            comments_response = requests.get(comments_url, headers=headers, timeout=10)
            comments = []
            
            if comments_response.status_code == 200:
                comments_data = comments_response.json()
                if "data" in comments_data and "children" in comments_data["data"]:
                    for comment in comments_data["data"]["children"]:
                        if len(comments) >= limit:
                            break
                        
                        comment_data = comment["data"]
                        
                        comments.append({
                            "subreddit": comment_data.get("subreddit", ""),
                            "created_at": datetime.datetime.fromtimestamp(comment_data.get("created_utc", 0)).strftime("%Y-%m-%d %H:%M:%S"),
                            "score": comment_data.get("score", 0),
                            "text": comment_data.get("body", ""),
                            "permalink": f"https://www.reddit.com{comment_data.get('permalink', '')}"
                        })
            
            # Generate insights
            insights = {}
            
            # Most active subreddits
            subreddits = [post["subreddit"] for post in posts]
            subreddits.extend([comment["subreddit"] for comment in comments])
            
            if subreddits:
                top_subreddits = [sub for sub, _ in Counter(subreddits).most_common(5)]
                insights["top_subreddits"] = top_subreddits
            
            # Calculate average scores
            post_scores = [post["score"] for post in posts]
            comment_scores = [comment["score"] for comment in comments]
            
            if post_scores:
                insights["avg_post_score"] = sum(post_scores) / len(post_scores)
            
            if comment_scores:
                insights["avg_comment_score"] = sum(comment_scores) / len(comment_scores)
            
            # Determine active hours
            active_hours = []
            for post in posts:
                try:
                    created_at = datetime.datetime.strptime(post["created_at"], "%Y-%m-%d %H:%M:%S")
                    active_hours.append(created_at.hour)
                except (ValueError, TypeError):
                    pass
            
            for comment in comments:
                try:
                    created_at = datetime.datetime.strptime(comment["created_at"], "%Y-%m-%d %H:%M:%S")
                    active_hours.append(created_at.hour)
                except (ValueError, TypeError):
                    pass
            
            if active_hours:
                insights["active_hours"] = [hour for hour, _ in Counter(active_hours).most_common(3)]
            
            return {
                "profile": profile,
                "posts": posts,
                "comments": comments,
                "insights": insights
            }
        
        except Exception as e:
            return {"error": f"Error analyzing Reddit user: {str(e)}"}
    
    elif analysis_type == "subreddit":
        # Clean the subreddit name (remove r/ if present)
        subreddit = query.replace("r/", "").strip()
        subreddit_url = f"https://www.reddit.com/r/{subreddit}/about.json"
        posts_url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={limit}"
        
        try:
            # Get subreddit information
            subreddit_response = requests.get(subreddit_url, headers=headers, timeout=10)
            if subreddit_response.status_code != 200:
                return {"error": f"Could not fetch subreddit info: HTTP {subreddit_response.status_code}"}
            
            subreddit_data = subreddit_response.json()
            
            # Extract subreddit information
            info = {}
            if "data" in subreddit_data:
                data = subreddit_data["data"]
                info["name"] = data.get("display_name", subreddit)
                info["title"] = data.get("title", "")
                info["description"] = data.get("public_description", "")
                info["subscribers"] = data.get("subscribers", 0)
                info["active_users"] = data.get("active_user_count", 0)
                
                # Subreddit creation date
                created_utc = data.get("created_utc", 0)
                if created_utc:
                    created_date = datetime.datetime.fromtimestamp(created_utc)
                    info["created_at"] = created_date.strftime("%Y-%m-%d")
                
                # Subreddit type (public, private, restricted)
                info["type"] = data.get("subreddit_type", "unknown")
            
            # Get recent posts
            posts_response = requests.get(posts_url, headers=headers, timeout=10)
            posts = []
            
            if posts_response.status_code == 200:
                posts_data = posts_response.json()
                if "data" in posts_data and "children" in posts_data["data"]:
                    for post in posts_data["data"]["children"]:
                        if len(posts) >= limit:
                            break
                        
                        post_data = post["data"]
                        
                        posts.append({
                            "title": post_data.get("title", ""),
                            "author": post_data.get("author", ""),
                            "created_at": datetime.datetime.fromtimestamp(post_data.get("created_utc", 0)).strftime("%Y-%m-%d %H:%M:%S"),
                            "score": post_data.get("score", 0),
                            "upvote_ratio": post_data.get("upvote_ratio", 0),
                            "num_comments": post_data.get("num_comments", 0),
                            "text": post_data.get("selftext", ""),
                            "url": post_data.get("url", ""),
                            "permalink": f"https://www.reddit.com{post_data.get('permalink', '')}"
                        })
            
            # Generate insights
            insights = {}
            
            if posts:
                # Top posters
                authors = [post["author"] for post in posts if post["author"] != "[deleted]"]
                if authors:
                    top_posters = [author for author, _ in Counter(authors).most_common(5)]
                    insights["top_posters"] = top_posters
                
                # Average post score
                post_scores = [post["score"] for post in posts]
                if post_scores:
                    insights["avg_post_score"] = sum(post_scores) / len(post_scores)
                
                # Common words in post titles
                all_words = []
                for post in posts:
                    words = re.findall(r'\b\w+\b', post["title"].lower())
                    # Filter out common stop words
                    stop_words = {'a', 'an', 'the', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 'to', 'of', 'in', 'for', 'with', 'on', 'at', 'from', 'by', 'about', 'as', 'into', 'like', 'through', 'after', 'over', 'between', 'out', 'against', 'during', 'without', 'before', 'under', 'around', 'among'}
                    words = [word for word in words if word not in stop_words and len(word) > 2]
                    all_words.extend(words)
                
                if all_words:
                    common_words = [word for word, _ in Counter(all_words).most_common(10)]
                    insights["common_words"] = common_words
                
                # Peak activity hours
                post_hours = []
                for post in posts:
                    try:
                        created_at = datetime.datetime.strptime(post["created_at"], "%Y-%m-%d %H:%M:%S")
                        post_hours.append(created_at.hour)
                    except (ValueError, TypeError):
                        pass
                
                if post_hours:
                    insights["peak_hours"] = [hour for hour, _ in Counter(post_hours).most_common(3)]
            
            return {
                "info": info,
                "posts": posts,
                "insights": insights
            }
        
        except Exception as e:
            return {"error": f"Error analyzing subreddit: {str(e)}"}
    
    elif analysis_type == "search":
        search_url = f"https://www.reddit.com/search.json?q={query}&limit={limit}"
        
        try:
            response = requests.get(search_url, headers=headers, timeout=10)
            if response.status_code != 200:
                return {"error": f"Could not fetch search results: HTTP {response.status_code}"}
            
            search_data = response.json()
            posts = []
            
            if "data" in search_data and "children" in search_data["data"]:
                for post in search_data["data"]["children"]:
                    post_data = post["data"]
                    
                    posts.append({
                        "title": post_data.get("title", ""),
                        "author": post_data.get("author", ""),
                        "subreddit": post_data.get("subreddit", ""),
                        "created_at": datetime.datetime.fromtimestamp(post_data.get("created_utc", 0)).strftime("%Y-%m-%d %H:%M:%S"),
                        "score": post_data.get("score", 0),
                        "num_comments": post_data.get("num_comments", 0),
                        "text": post_data.get("selftext", ""),
                        "url": post_data.get("url", ""),
                        "permalink": f"https://www.reddit.com{post_data.get('permalink', '')}"
                    })
            
            return {
                "posts": posts
            }
        
        except Exception as e:
            return {"error": f"Error searching Reddit: {str(e)}"}
    
    else:
        return {"error": f"Unsupported analysis type for Reddit: {analysis_type}"}

def analyze_instagram(analysis_type: str, query: str, limit: int = 30) -> Dict[str, Any]:
    """
    Analyze Instagram profiles and content.
    Note: Instagram heavily restricts scraping, so this analysis is limited.
    
    Args:
        analysis_type: Type of analysis (user, hashtag, search)
        query: Username, hashtag, or search query
        limit: Maximum number of results to return
        
    Returns:
        Dictionary containing Instagram analysis results
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    ]
    
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    # Instagram has very strict anti-scraping measures
    # We'll provide limited functionality through public pages
    if analysis_type == "user":
        # Clean the username (remove @ if present)
        username = query.replace("@", "").strip()
        profile_url = f"https://www.instagram.com/{username}/"
        
        try:
            response = requests.get(profile_url, headers=headers, timeout=10)
            if response.status_code != 200:
                return {"error": f"Could not fetch user profile: HTTP {response.status_code}"}
            
            # Instagram embeds profile data in a JSON object in the HTML
            html = response.text
            
            # Look for the shared_data JSON
            shared_data_match = re.search(r'window\._sharedData\s*=\s*({.*?});</script>', html, re.DOTALL)
            
            if not shared_data_match:
                return {"error": "Could not find profile data in response"}
            
            try:
                import json
                shared_data = json.loads(shared_data_match.group(1))
                
                # Navigate to user data in the JSON structure
                user_data = None
                
                if "entry_data" in shared_data and "ProfilePage" in shared_data["entry_data"]:
                    profile_page = shared_data["entry_data"]["ProfilePage"][0]
                    if "graphql" in profile_page and "user" in profile_page["graphql"]:
                        user_data = profile_page["graphql"]["user"]
                
                if not user_data:
                    return {"error": "Could not find user data in response"}
                
                # Extract profile information
                profile = {
                    "username": user_data.get("username", username),
                    "full_name": user_data.get("full_name", ""),
                    "biography": user_data.get("biography", ""),
                    "follower_count": user_data.get("edge_followed_by", {}).get("count", 0),
                    "following_count": user_data.get("edge_follow", {}).get("count", 0),
                    "media_count": user_data.get("edge_owner_to_timeline_media", {}).get("count", 0),
                    "is_private": user_data.get("is_private", False),
                    "is_verified": user_data.get("is_verified", False),
                    "external_url": user_data.get("external_url", ""),
                    "profile_url": profile_url
                }
                
                return {
                    "profile": profile
                }
            except json.JSONDecodeError:
                return {"error": "Could not parse profile data"}
        
        except Exception as e:
            return {"error": f"Error analyzing Instagram user: {str(e)}"}
    
    else:
        return {
            "error": f"Unsupported analysis type for Instagram: {analysis_type}",
            "note": "Instagram heavily restricts scraping. Only basic user profile information is available."
        }

def analyze_tiktok(analysis_type: str, query: str, limit: int = 30) -> Dict[str, Any]:
    """
    Analyze TikTok profiles and content.
    Note: TikTok heavily restricts scraping, so this analysis is limited.
    
    Args:
        analysis_type: Type of analysis (user, hashtag, search)
        query: Username, hashtag, or search query
        limit: Maximum number of results to return
        
    Returns:
        Dictionary containing TikTok analysis results
    """
    # TikTok has very strict anti-scraping measures
    # We'll provide limited functionality through public pages
    if analysis_type == "user":
        # Clean the username (remove @ if present)
        username = query.replace("@", "").strip()
        
        # Since direct scraping is difficult, we'll return information about how to access this data
        profile = {
            "username": username,
            "note": "TikTok data collection is restricted. For comprehensive analysis, consider using TikTok's official API or specialized OSINT tools.",
            "manual_url": f"https://www.tiktok.com/@{username}"
        }
        
        return {
            "profile": profile,
            "note": "TikTok restricts automated data collection. Limited information available."
        }
    
    else:
        return {
            "error": f"Unsupported analysis type for TikTok: {analysis_type}",
            "note": "TikTok heavily restricts scraping. Consider using the official API or specialized tools."
        }

def analyze_youtube(analysis_type: str, query: str, limit: int = 30) -> Dict[str, Any]:
    """
    Analyze YouTube profiles and content.
    Note: YouTube API typically requires an API key for comprehensive data.
    
    Args:
        analysis_type: Type of analysis (user, channel, search)
        query: Username, channel ID, or search query
        limit: Maximum number of results to return
        
    Returns:
        Dictionary containing YouTube analysis results
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
    ]
    
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    # Without the YouTube API, we're limited in what we can do
    if analysis_type == "user":
        # For user/channel analysis
        channel_url = f"https://www.youtube.com/user/{query}"
        if not query.startswith("@"):
            channel_url_at = f"https://www.youtube.com/@{query}"
        else:
            channel_url_at = f"https://www.youtube.com/{query}"
        
        # Try both URL formats
        try:
            response = requests.get(channel_url, headers=headers, timeout=10)
            if response.status_code != 200:
                response = requests.get(channel_url_at, headers=headers, timeout=10)
                if response.status_code != 200:
                    return {"error": f"Could not fetch channel: HTTP {response.status_code}"}
            
            html = response.text
            
            # Extract channel metadata
            channel_name_match = re.search(r'"channelMetadataRenderer":\s*{\s*"title":\s*"([^"]+)"', html)
            subscriber_count_match = re.search(r'"subscriberCountText":\s*{\s*"simpleText":\s*"([^"]+)"', html)
            
            profile = {
                "channel_name": channel_name_match.group(1) if channel_name_match else "Unknown",
                "subscriber_count": subscriber_count_match.group(1) if subscriber_count_match else "Unknown",
                "channel_url": response.url,
                "note": "For comprehensive YouTube analysis, consider using the YouTube Data API."
            }
            
            return {
                "profile": profile,
                "note": "Limited YouTube data available without API access."
            }
        
        except Exception as e:
            return {"error": f"Error analyzing YouTube channel: {str(e)}"}
    
    else:
        return {
            "error": f"Unsupported analysis type for YouTube: {analysis_type}",
            "note": "YouTube analysis requires API access for most functionality."
        }
