import streamlit as st
import pandas as pd
import datetime
import os


# Import tool modullses
from utils.utils.username_checker import check_username
from utils.utils.dns_enum import dns_enumeration
from utils.utils.dark_web_search import search_dark_web
from utils.utils.ip_geolocation import get_ip_geolocation
from utils.utils.metadata_extractor import extract_metadata
from utils.utils.social_media_analyzer import analyze_social_media
from utils.utils.whois_lookup import whois_lookup
from utils.utils.logger import log_activity
from utils.utils.export import export_to_csv, export_to_json

# Set page configuration
st.set_page_config(
    page_title="OSINT Toolbox",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Create session state for history
if 'history' not in st.session_state:
    st.session_state.history = []

# Create directory for temporary file uploads if it doesn't exist
if not os.path.exists("temp_uploads"):
    os.makedirs("temp_uploads")

# Sidebar for app navigation and history
with st.sidebar:
    st.title("🔍 OSINT Toolbox")
    st.markdown("---")
    
    # Show search history
    with st.expander("Search History", expanded=False):
        if st.session_state.history:
            for item in st.session_state.history[-10:]:  # Show last 10 entries
                st.write(f"**{item['timestamp']}**: {item['tool']} - {item['query']}")
        else:
            st.write("No search history yet.")
    
    st.markdown("---")
    st.markdown("### About")
    st.markdown("""
    This OSINT Toolbox provides multiple tools for open-source intelligence gathering.
    Use the tabs above to navigate between different tools.
    """)
    
    st.markdown("---")
    st.markdown("**Note:** All tools are for legitimate research purposes only. Use responsibly and ethically.")

# Main app content
st.title("OSINT Toolbox")
st.markdown("Select a tool from the tabs below:")

# Create tabs for different tools
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "Username/Email Checker", 
    "DNS Enumeration", 
    "Dark Web Search",
    "IP Geolocation",
    "Metadata Extractor",
    "Social Media Analyzer",
    "WHOIS Lookup"
])

# Username/Email Checker
with tab1:
    st.header("Username & Email Checker")
    st.markdown("Check if a username or email exists across various platforms.")
    
    query_type = st.radio("Select type:", ["Username", "Email"], horizontal=True)
    query = st.text_input(f"Enter {query_type.lower()} to search:")
    
    platforms = st.multiselect(
        "Select platforms to check (or leave empty for all):",
        ["Twitter", "Instagram", "GitHub", "Reddit", "LinkedIn", "TikTok", "Pinterest", "Telegram", "Medium", "DeviantArt"],
        default=["Twitter", "Instagram", "GitHub", "Reddit"]
    )
    
    if st.button("Search", key="username_search"):
        if query:
            with st.spinner(f"Searching for {query_type.lower()} '{query}'..."):
                # Log the activity
                log_activity(tool="Username/Email Checker", query=query, st_session=st.session_state)
                
                # Perform the search
                results = check_username(query, query_type, platforms)
                
                # Display results
                if results:
                    st.success(f"Search completed for {query_type.lower()}: {query}")
                    
                    # Create DataFrame
                    df = pd.DataFrame(results)
                    st.dataframe(df, use_container_width=True)
                    
                    # Export options
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Export as CSV"):
                            csv_data = export_to_csv(df)
                            st.download_button(
                                label="Download CSV",
                                data=csv_data,
                                file_name=f"{query_type.lower()}_search_{query}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                    with col2:
                        if st.button("Export as JSON"):
                            json_data = export_to_json(results)
                            st.download_button(
                                label="Download JSON",
                                data=json_data,
                                file_name=f"{query_type.lower()}_search_{query}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json"
                            )
                else:
                    st.error("No results found or an error occurred.")
        else:
            st.warning(f"Please enter a {query_type.lower()} to search.")

# DNS Enumeration
with tab2:
    st.header("DNS Enumeration")
    st.markdown("Perform DNS enumeration on a domain to discover various DNS records.")
    
    domain = st.text_input("Enter domain name (e.g., example.com):")
    record_types = st.multiselect(
        "Select DNS record types to query:",
        ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA", "All"],
        default=["A", "MX", "NS", "TXT"]
    )
    
    if "All" in record_types:
        record_types = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]
    
    if st.button("Enumerate", key="dns_enum"):
        if domain:
            with st.spinner(f"Performing DNS enumeration on {domain}..."):
                # Log the activity
                log_activity(tool="DNS Enumeration", query=domain, st_session=st.session_state)
                
                # Perform DNS enumeration
                results = dns_enumeration(domain, record_types)
                
                # Display results
                if results:
                    st.success(f"DNS enumeration completed for: {domain}")
                    
                    # Display each record type in an expander
                    for record_type, records in results.items():
                        with st.expander(f"{record_type} Records", expanded=True):
                            if records:
                                df = pd.DataFrame(records)
                                st.dataframe(df, use_container_width=True)
                            else:
                                st.info(f"No {record_type} records found.")
                    
                    # Export options
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Export as CSV"):
                            # Create a flattened DataFrame for export
                            all_records = []
                            for record_type, records in results.items():
                                for record in records:
                                    record["record_type"] = record_type
                                    all_records.append(record)
                            
                            df_export = pd.DataFrame(all_records)
                            csv_data = export_to_csv(df_export)
                            st.download_button(
                                label="Download CSV",
                                data=csv_data,
                                file_name=f"dns_enum_{domain}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                    with col2:
                        if st.button("Export as JSON"):
                            json_data = export_to_json(results)
                            st.download_button(
                                label="Download JSON",
                                data=json_data,
                                file_name=f"dns_enum_{domain}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json"
                            )
                else:
                    st.error("No results found or an error occurred.")
        else:
            st.warning("Please enter a domain name.")

# Dark Web Search
with tab3:
    st.header("Dark Web Search")
    st.markdown("Search for information across various dark web search engines and onion repositories.")
    st.warning("Note: This tool only queries legal dark web search engines and indexes. It does not access illegal content directly.")
    
    search_query = st.text_input("Enter search query:")
    search_type = st.selectbox(
        "Search type:",
        ["General", "Data Breaches", "Forums", "Marketplaces", "Comprehensive"]
    )
    
    if st.button("Search", key="dark_web_search"):
        if search_query:
            with st.spinner(f"Searching dark web for: {search_query}"):
                # Log the activity
                log_activity(tool="Dark Web Search", query=search_query, st_session=st.session_state)
                
                # Perform dark web search
                results = search_dark_web(search_query, search_type)
                
                # Display results
                if results:
                    st.success(f"Search completed for: {search_query}")
                    
                    # Display results in tabs based on source
                    source_tabs = st.tabs(list(results.keys()))
                    
                    for i, source in enumerate(results.keys()):
                        with source_tabs[i]:
                            if results[source]:
                                df = pd.DataFrame(results[source])
                                st.dataframe(df, use_container_width=True)
                            else:
                                st.info(f"No results found from {source}.")
                    
                    # Export options
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Export as CSV"):
                            # Create a flattened DataFrame for export
                            all_results = []
                            for source, source_results in results.items():
                                for result in source_results:
                                    result["source"] = source
                                    all_results.append(result)
                            
                            df_export = pd.DataFrame(all_results)
                            csv_data = export_to_csv(df_export)
                            st.download_button(
                                label="Download CSV",
                                data=csv_data,
                                file_name=f"dark_web_search_{search_query}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                    with col2:
                        if st.button("Export as JSON"):
                            json_data = export_to_json(results)
                            st.download_button(
                                label="Download JSON",
                                data=json_data,
                                file_name=f"dark_web_search_{search_query}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json"
                            )
                else:
                    st.error("No results found or an error occurred.")
        else:
            st.warning("Please enter a search query.")

# IP Geolocation
with tab4:
    st.header("IP Geolocation")
    st.markdown("Track and analyze IP addresses to get geolocation information.")
    
    ip_address = st.text_input("Enter IP address:")
    
    if st.button("Locate", key="ip_locate"):
        if ip_address:
            with st.spinner(f"Retrieving geolocation data for IP: {ip_address}"):
                # Log the activity
                log_activity(tool="IP Geolocation", query=ip_address, st_session=st.session_state)
                
                # Get IP geolocation data
                result = get_ip_geolocation(ip_address)
                
                # Display results
                if result and "error" not in result:
                    st.success(f"Geolocation data retrieved for IP: {ip_address}")
                    
                    # Display general information
                    col1, col2 = st.columns(2)
                    with col1:
                        st.subheader("Location Information")
                        st.markdown(f"**Country:** {result.get('country', 'N/A')}")
                        st.markdown(f"**Region:** {result.get('region', 'N/A')}")
                        st.markdown(f"**City:** {result.get('city', 'N/A')}")
                        st.markdown(f"**ZIP:** {result.get('zip', 'N/A')}")
                        st.markdown(f"**Timezone:** {result.get('timezone', 'N/A')}")
                    
                    with col2:
                        st.subheader("Network Information")
                        st.markdown(f"**ISP:** {result.get('isp', 'N/A')}")
                        st.markdown(f"**Organization:** {result.get('org', 'N/A')}")
                        st.markdown(f"**AS Number:** {result.get('as', 'N/A')}")
                    
                    # Display map if coordinates are available
                    if 'lat' in result and 'lon' in result:
                        st.subheader("Map Location")
                        map_data = pd.DataFrame({
                            'lat': [result['lat']],
                            'lon': [result['lon']]
                        })
                        st.map(map_data)
                    
                    # Export options
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Export as CSV"):
                            df_export = pd.DataFrame([result])
                            csv_data = export_to_csv(df_export)
                            st.download_button(
                                label="Download CSV",
                                data=csv_data,
                                file_name=f"ip_geolocation_{ip_address}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                    with col2:
                        if st.button("Export as JSON"):
                            json_data = export_to_json(result)
                            st.download_button(
                                label="Download JSON",
                                data=json_data,
                                file_name=f"ip_geolocation_{ip_address}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json"
                            )
                else:
                    error_msg = result.get("error", "Failed to retrieve geolocation data.") if isinstance(result, dict) else "Failed to retrieve geolocation data."
                    st.error(error_msg)
        else:
            st.warning("Please enter an IP address.")

# Metadata Extractor
with tab5:
    st.header("Metadata Extractor")
    st.markdown("Extract metadata from various file types.")
    
    uploaded_file = st.file_uploader("Upload a file", type=["pdf", "jpg", "jpeg", "png", "docx", "xlsx", "pptx"])
    
    if uploaded_file is not None:
        # Save the file to a temporary location
        file_path = os.path.join("temp_uploads", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        st.success(f"File '{uploaded_file.name}' uploaded successfully!")
        
        if st.button("Extract Metadata", key="extract_metadata"):
            with st.spinner("Extracting metadata..."):
                # Log the activity
                log_activity(tool="Metadata Extractor", query=uploaded_file.name, st_session=st.session_state)
                
                # Extract metadata
                metadata = extract_metadata(file_path)
                
                # Display results
                if metadata:
                    st.success(f"Metadata extracted from: {uploaded_file.name}")
                    
                    # Display metadata in expandable sections
                    for category, items in metadata.items():
                        with st.expander(category, expanded=True):
                            if isinstance(items, dict):
                                for key, value in items.items():
                                    st.markdown(f"**{key}:** {value}")
                            elif isinstance(items, list):
                                for item in items:
                                    if isinstance(item, dict):
                                        for key, value in item.items():
                                            st.markdown(f"**{key}:** {value}")
                                        st.markdown("---")
                                    else:
                                        st.markdown(f"- {item}")
                            else:
                                st.markdown(f"{items}")
                    
                    # Export options
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Export as CSV"):
                            # Flatten the metadata for CSV export
                            flat_metadata = []
                            for category, items in metadata.items():
                                if isinstance(items, dict):
                                    for key, value in items.items():
                                        flat_metadata.append({
                                            "Category": category,
                                            "Property": key,
                                            "Value": value
                                        })
                                elif isinstance(items, list):
                                    for i, item in enumerate(items):
                                        if isinstance(item, dict):
                                            for key, value in item.items():
                                                flat_metadata.append({
                                                    "Category": category,
                                                    "Property": f"{i+1}_{key}",
                                                    "Value": value
                                                })
                                        else:
                                            flat_metadata.append({
                                                "Category": category,
                                                "Property": f"Item_{i+1}",
                                                "Value": item
                                            })
                                else:
                                    flat_metadata.append({
                                        "Category": category,
                                        "Property": "Value",
                                        "Value": items
                                    })
                            
                            df_export = pd.DataFrame(flat_metadata)
                            csv_data = export_to_csv(df_export)
                            st.download_button(
                                label="Download CSV",
                                data=csv_data,
                                file_name=f"metadata_{uploaded_file.name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                    with col2:
                        if st.button("Export as JSON"):
                            json_data = export_to_json(metadata)
                            st.download_button(
                                label="Download JSON",
                                data=json_data,
                                file_name=f"metadata_{uploaded_file.name}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json"
                            )
                else:
                    st.error("No metadata found or an error occurred.")
                
                # Clean up the temporary file
                try:
                    os.remove(file_path)
                except:
                    pass

# Social Media Analyzer
with tab6:
    st.header("Social Media Analyzer")
    st.markdown("Analyze public profiles and content on social media platforms.")
    
    platform = st.selectbox(
        "Select platform:",
        ["Twitter", "Reddit", "Instagram", "TikTok", "YouTube"]
    )
    
    st.markdown("---")
    
    if platform == "Twitter":
        analysis_type = st.radio("Select analysis type:", ["User Profile", "Hashtag Analysis", "Tweet Search"], horizontal=True)
        
        if analysis_type == "User Profile":
            username = st.text_input("Enter Twitter username (without @):")
            max_tweets = st.slider("Maximum number of tweets to analyze:", 10, 100, 30)
            
            if st.button("Analyze", key="twitter_user_analyze"):
                if username:
                    with st.spinner(f"Analyzing Twitter profile: @{username}"):
                        # Log the activity
                        log_activity(tool="Social Media Analyzer (Twitter User)", query=username, st_session=st.session_state)
                        
                        # Analyze Twitter profile
                        result = analyze_social_media(platform="twitter", analysis_type="user", query=username, limit=max_tweets)
                        
                        # Display results
                        if result and "error" not in result:
                            st.success(f"Analysis completed for Twitter user: @{username}")
                            
                            # Profile info
                            if "profile" in result:
                                profile = result["profile"]
                                st.subheader("Profile Information")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown(f"**Name:** {profile.get('name', 'N/A')}")
                                    st.markdown(f"**Username:** @{profile.get('username', 'N/A')}")
                                    st.markdown(f"**Location:** {profile.get('location', 'N/A')}")
                                    st.markdown(f"**Description:** {profile.get('description', 'N/A')}")
                                
                                with col2:
                                    st.markdown(f"**Followers:** {profile.get('followers_count', 'N/A')}")
                                    st.markdown(f"**Following:** {profile.get('following_count', 'N/A')}")
                                    st.markdown(f"**Tweets:** {profile.get('tweets_count', 'N/A')}")
                                    st.markdown(f"**Joined:** {profile.get('created_at', 'N/A')}")
                            
                            # Recent tweets
                            if "tweets" in result and result["tweets"]:
                                st.subheader(f"Recent Tweets ({len(result['tweets'])})")
                                
                                for tweet in result["tweets"]:
                                    with st.expander(f"{tweet.get('text', '')[:100]}...", expanded=False):
                                        st.markdown(f"**Tweet:** {tweet.get('text', 'N/A')}")
                                        st.markdown(f"**Date:** {tweet.get('created_at', 'N/A')}")
                                        st.markdown(f"**Retweets:** {tweet.get('retweet_count', 'N/A')}")
                                        st.markdown(f"**Likes:** {tweet.get('favorite_count', 'N/A')}")
                                        if tweet.get('hashtags'):
                                            st.markdown(f"**Hashtags:** {', '.join(tweet['hashtags'])}")
                                        if tweet.get('mentions'):
                                            st.markdown(f"**Mentions:** {', '.join(tweet['mentions'])}")
                            
                            # Statistics and insights
                            if "insights" in result:
                                st.subheader("Insights and Statistics")
                                insights = result["insights"]
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown(f"**Most active day:** {insights.get('most_active_day', 'N/A')}")
                                    st.markdown(f"**Most active hour:** {insights.get('most_active_hour', 'N/A')}")
                                    st.markdown(f"**Average likes per tweet:** {insights.get('avg_likes', 'N/A')}")
                                
                                with col2:
                                    st.markdown(f"**Average retweets per tweet:** {insights.get('avg_retweets', 'N/A')}")
                                    st.markdown(f"**Top hashtags:** {', '.join(insights.get('top_hashtags', ['N/A']))}")
                                    st.markdown(f"**Top mentions:** {', '.join(insights.get('top_mentions', ['N/A']))}")
                            
                            # Export options
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("Export as CSV"):
                                    # Create a DataFrame for the tweets
                                    df_tweets = pd.DataFrame(result.get("tweets", []))
                                    csv_data = export_to_csv(df_tweets)
                                    st.download_button(
                                        label="Download CSV",
                                        data=csv_data,
                                        file_name=f"twitter_user_{username}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                        mime="text/csv"
                                    )
                            with col2:
                                if st.button("Export as JSON"):
                                    json_data = export_to_json(result)
                                    st.download_button(
                                        label="Download JSON",
                                        data=json_data,
                                        file_name=f"twitter_user_{username}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                        mime="application/json"
                                    )
                        else:
                            error_msg = result.get("error", "Failed to analyze Twitter profile.") if isinstance(result, dict) else "Failed to analyze Twitter profile."
                            st.error(error_msg)
                else:
                    st.warning("Please enter a Twitter username.")
                    
        elif analysis_type == "Hashtag Analysis":
            hashtag = st.text_input("Enter hashtag (without #):")
            max_tweets = st.slider("Maximum number of tweets to analyze:", 10, 200, 50)
            
            if st.button("Analyze", key="twitter_hashtag_analyze"):
                if hashtag:
                    with st.spinner(f"Analyzing Twitter hashtag: #{hashtag}"):
                        # Log the activity
                        log_activity(tool="Social Media Analyzer (Twitter Hashtag)", query=hashtag, st_session=st.session_state)
                        
                        # Analyze Twitter hashtag
                        result = analyze_social_media(platform="twitter", analysis_type="hashtag", query=hashtag, limit=max_tweets)
                        
                        # Display results
                        if result and "error" not in result:
                            st.success(f"Analysis completed for Twitter hashtag: #{hashtag}")
                            
                            # Tweets with the hashtag
                            if "tweets" in result and result["tweets"]:
                                st.subheader(f"Tweets with #{hashtag} ({len(result['tweets'])})")
                                
                                tweets_df = pd.DataFrame(result["tweets"])
                                st.dataframe(tweets_df, use_container_width=True)
                                
                                st.subheader("Sample Tweets")
                                for i, tweet in enumerate(result["tweets"][:5]):  # Show first 5 tweets
                                    with st.expander(f"Tweet {i+1}: {tweet.get('text', '')[:100]}...", expanded=False):
                                        st.markdown(f"**Tweet:** {tweet.get('text', 'N/A')}")
                                        st.markdown(f"**User:** @{tweet.get('username', 'N/A')}")
                                        st.markdown(f"**Date:** {tweet.get('created_at', 'N/A')}")
                                        st.markdown(f"**Retweets:** {tweet.get('retweet_count', 'N/A')}")
                                        st.markdown(f"**Likes:** {tweet.get('favorite_count', 'N/A')}")
                            
                            # Insights
                            if "insights" in result:
                                st.subheader("Hashtag Insights")
                                insights = result["insights"]
                                
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Total Tweets Analyzed", insights.get("tweet_count", "N/A"))
                                with col2:
                                    st.metric("Unique Users", insights.get("unique_users", "N/A"))
                                with col3:
                                    st.metric("Average Engagement", insights.get("avg_engagement", "N/A"))
                                
                                st.subheader("Related Hashtags")
                                if insights.get("related_hashtags"):
                                    st.write(", ".join([f"#{tag}" for tag in insights["related_hashtags"]]))
                                else:
                                    st.write("No related hashtags found.")
                            
                            # Export options
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("Export as CSV"):
                                    # Create a DataFrame for the tweets
                                    df_tweets = pd.DataFrame(result.get("tweets", []))
                                    csv_data = export_to_csv(df_tweets)
                                    st.download_button(
                                        label="Download CSV",
                                        data=csv_data,
                                        file_name=f"twitter_hashtag_{hashtag}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                        mime="text/csv"
                                    )
                            with col2:
                                if st.button("Export as JSON"):
                                    json_data = export_to_json(result)
                                    st.download_button(
                                        label="Download JSON",
                                        data=json_data,
                                        file_name=f"twitter_hashtag_{hashtag}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                        mime="application/json"
                                    )
                        else:
                            error_msg = result.get("error", "Failed to analyze Twitter hashtag.") if isinstance(result, dict) else "Failed to analyze Twitter hashtag."
                            st.error(error_msg)
                else:
                    st.warning("Please enter a hashtag.")
                    
        elif analysis_type == "Tweet Search":
            query = st.text_input("Enter search query:")
            max_tweets = st.slider("Maximum number of tweets to retrieve:", 10, 200, 50)
            
            if st.button("Search", key="twitter_search_analyze"):
                if query:
                    with st.spinner(f"Searching Twitter for: {query}"):
                        # Log the activity
                        log_activity(tool="Social Media Analyzer (Twitter Search)", query=query, st_session=st.session_state)
                        
                        # Search Twitter
                        result = analyze_social_media(platform="twitter", analysis_type="search", query=query, limit=max_tweets)
                        
                        # Display results
                        if result and "error" not in result:
                            st.success(f"Search completed for query: {query}")
                            
                            # Show search results
                            if "tweets" in result and result["tweets"]:
                                st.subheader(f"Search Results ({len(result['tweets'])} tweets)")
                                
                                tweets_df = pd.DataFrame(result["tweets"])
                                st.dataframe(tweets_df, use_container_width=True)
                                
                                st.subheader("Sample Tweets")
                                for i, tweet in enumerate(result["tweets"][:5]):  # Show first 5 tweets
                                    with st.expander(f"Tweet {i+1}: {tweet.get('text', '')[:100]}...", expanded=False):
                                        st.markdown(f"**Tweet:** {tweet.get('text', 'N/A')}")
                                        st.markdown(f"**User:** @{tweet.get('username', 'N/A')}")
                                        st.markdown(f"**Date:** {tweet.get('created_at', 'N/A')}")
                                        st.markdown(f"**Retweets:** {tweet.get('retweet_count', 'N/A')}")
                                        st.markdown(f"**Likes:** {tweet.get('favorite_count', 'N/A')}")
                            
                            # Export options
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("Export as CSV"):
                                    # Create a DataFrame for the tweets
                                    df_tweets = pd.DataFrame(result.get("tweets", []))
                                    csv_data = export_to_csv(df_tweets)
                                    st.download_button(
                                        label="Download CSV",
                                        data=csv_data,
                                        file_name=f"twitter_search_{query.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                        mime="text/csv"
                                    )
                            with col2:
                                if st.button("Export as JSON"):
                                    json_data = export_to_json(result)
                                    st.download_button(
                                        label="Download JSON",
                                        data=json_data,
                                        file_name=f"twitter_search_{query.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                        mime="application/json"
                                    )
                        else:
                            error_msg = result.get("error", "Failed to search Twitter.") if isinstance(result, dict) else "Failed to search Twitter."
                            st.error(error_msg)
                else:
                    st.warning("Please enter a search query.")
    
    elif platform == "Reddit":
        analysis_type = st.radio("Select analysis type:", ["User Profile", "Subreddit Analysis", "Search"], horizontal=True)
        
        if analysis_type == "User Profile":
            username = st.text_input("Enter Reddit username (without u/):")
            max_posts = st.slider("Maximum number of posts/comments to analyze:", 10, 100, 30)
            
            if st.button("Analyze", key="reddit_user_analyze"):
                if username:
                    with st.spinner(f"Analyzing Reddit profile: u/{username}"):
                        # Log the activity
                        log_activity(tool="Social Media Analyzer (Reddit User)", query=username, st_session=st.session_state)
                        
                        # Analyze Reddit profile
                        result = analyze_social_media(platform="reddit", analysis_type="user", query=username, limit=max_posts)
                        
                        # Display results
                        if result and "error" not in result:
                            st.success(f"Analysis completed for Reddit user: u/{username}")
                            
                            # Display user info
                            if "profile" in result:
                                profile = result["profile"]
                                st.subheader("User Information")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown(f"**Username:** u/{profile.get('username', 'N/A')}")
                                    st.markdown(f"**Account Age:** {profile.get('account_age', 'N/A')}")
                                    st.markdown(f"**Karma (Post):** {profile.get('post_karma', 'N/A')}")
                                
                                with col2:
                                    st.markdown(f"**Karma (Comment):** {profile.get('comment_karma', 'N/A')}")
                                    st.markdown(f"**Trophies:** {', '.join(profile.get('trophies', ['None']))}")
                            
                            # Display posts and comments
                            if "posts" in result and result["posts"]:
                                st.subheader(f"Recent Posts ({len(result['posts'])})")
                                
                                posts_df = pd.DataFrame(result["posts"])
                                st.dataframe(posts_df, use_container_width=True)
                                
                                for i, post in enumerate(result["posts"][:5]):  # Show first 5 posts
                                    with st.expander(f"Post {i+1}: {post.get('title', '')[:100]}...", expanded=False):
                                        st.markdown(f"**Title:** {post.get('title', 'N/A')}")
                                        st.markdown(f"**Subreddit:** r/{post.get('subreddit', 'N/A')}")
                                        st.markdown(f"**Date:** {post.get('created_at', 'N/A')}")
                                        st.markdown(f"**Score:** {post.get('score', 'N/A')}")
                                        st.markdown(f"**Content:** {post.get('text', 'N/A')[:500]}...")
                            
                            if "comments" in result and result["comments"]:
                                st.subheader(f"Recent Comments ({len(result['comments'])})")
                                
                                comments_df = pd.DataFrame(result["comments"])
                                st.dataframe(comments_df, use_container_width=True)
                            
                            # Display insights
                            if "insights" in result:
                                insights = result["insights"]
                                st.subheader("User Insights")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown(f"**Most active subreddits:** {', '.join(['r/' + sub for sub in insights.get('top_subreddits', ['N/A'])])}")
                                    st.markdown(f"**Average post score:** {insights.get('avg_post_score', 'N/A')}")
                                
                                with col2:
                                    st.markdown(f"**Average comment score:** {insights.get('avg_comment_score', 'N/A')}")
                                    st.markdown(f"**Most active hours:** {', '.join([str(hour) for hour in insights.get('active_hours', ['N/A'])])}")
                            
                            # Export options
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("Export as CSV"):
                                    # Combine posts and comments into a single DataFrame
                                    posts_df = pd.DataFrame(result.get("posts", []))
                                    if not posts_df.empty:
                                        posts_df["type"] = "post"
                                    
                                    comments_df = pd.DataFrame(result.get("comments", []))
                                    if not comments_df.empty:
                                        comments_df["type"] = "comment"
                                    
                                    df_export = pd.concat([posts_df, comments_df], ignore_index=True)
                                    csv_data = export_to_csv(df_export)
                                    st.download_button(
                                        label="Download CSV",
                                        data=csv_data,
                                        file_name=f"reddit_user_{username}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                        mime="text/csv"
                                    )
                            with col2:
                                if st.button("Export as JSON"):
                                    json_data = export_to_json(result)
                                    st.download_button(
                                        label="Download JSON",
                                        data=json_data,
                                        file_name=f"reddit_user_{username}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                        mime="application/json"
                                    )
                        else:
                            error_msg = result.get("error", "Failed to analyze Reddit profile.") if isinstance(result, dict) else "Failed to analyze Reddit profile."
                            st.error(error_msg)
                else:
                    st.warning("Please enter a Reddit username.")
                    
        elif analysis_type == "Subreddit Analysis":
            subreddit = st.text_input("Enter subreddit name (without r/):")
            max_posts = st.slider("Maximum number of posts to analyze:", 10, 100, 30)
            
            if st.button("Analyze", key="reddit_subreddit_analyze"):
                if subreddit:
                    with st.spinner(f"Analyzing subreddit: r/{subreddit}"):
                        # Log the activity
                        log_activity(tool="Social Media Analyzer (Reddit Subreddit)", query=subreddit, st_session=st.session_state)
                        
                        # Analyze subreddit
                        result = analyze_social_media(platform="reddit", analysis_type="subreddit", query=subreddit, limit=max_posts)
                        
                        # Display results
                        if result and "error" not in result:
                            st.success(f"Analysis completed for subreddit: r/{subreddit}")
                            
                            # Display subreddit info
                            if "info" in result:
                                info = result["info"]
                                st.subheader("Subreddit Information")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown(f"**Name:** r/{info.get('name', 'N/A')}")
                                    st.markdown(f"**Subscribers:** {info.get('subscribers', 'N/A')}")
                                    st.markdown(f"**Created:** {info.get('created_at', 'N/A')}")
                                
                                with col2:
                                    st.markdown(f"**Type:** {info.get('type', 'N/A')}")
                                    st.markdown(f"**Description:** {info.get('description', 'N/A')[:200]}...")
                            
                            # Display posts
                            if "posts" in result and result["posts"]:
                                st.subheader(f"Recent Posts ({len(result['posts'])})")
                                
                                posts_df = pd.DataFrame(result["posts"])
                                st.dataframe(posts_df, use_container_width=True)
                                
                                for i, post in enumerate(result["posts"][:5]):  # Show first 5 posts
                                    with st.expander(f"Post {i+1}: {post.get('title', '')[:100]}...", expanded=False):
                                        st.markdown(f"**Title:** {post.get('title', 'N/A')}")
                                        st.markdown(f"**Author:** u/{post.get('author', 'N/A')}")
                                        st.markdown(f"**Date:** {post.get('created_at', 'N/A')}")
                                        st.markdown(f"**Score:** {post.get('score', 'N/A')}")
                                        st.markdown(f"**Content:** {post.get('text', 'N/A')[:500]}...")
                            
                            # Display insights
                            if "insights" in result:
                                insights = result["insights"]
                                st.subheader("Subreddit Insights")
                                
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown(f"**Top posters:** {', '.join(['u/' + user for user in insights.get('top_posters', ['N/A'])])}")
                                    st.markdown(f"**Common words:** {', '.join(insights.get('common_words', ['N/A']))}")
                                
                                with col2:
                                    st.markdown(f"**Average post score:** {insights.get('avg_post_score', 'N/A')}")
                                    st.markdown(f"**Peak activity hours:** {', '.join([str(hour) for hour in insights.get('peak_hours', ['N/A'])])}")
                            
                            # Export options
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("Export as CSV"):
                                    # Create a DataFrame for posts
                                    df_export = pd.DataFrame(result.get("posts", []))
                                    csv_data = export_to_csv(df_export)
                                    st.download_button(
                                        label="Download CSV",
                                        data=csv_data,
                                        file_name=f"reddit_subreddit_{subreddit}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                        mime="text/csv"
                                    )
                            with col2:
                                if st.button("Export as JSON"):
                                    json_data = export_to_json(result)
                                    st.download_button(
                                        label="Download JSON",
                                        data=json_data,
                                        file_name=f"reddit_subreddit_{subreddit}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                        mime="application/json"
                                    )
                        else:
                            error_msg = result.get("error", "Failed to analyze subreddit.") if isinstance(result, dict) else "Failed to analyze subreddit."
                            st.error(error_msg)
                else:
                    st.warning("Please enter a subreddit name.")
        
        elif analysis_type == "Search":
            query = st.text_input("Enter search query:")
            max_results = st.slider("Maximum number of results:", 10, 100, 30)
            
            if st.button("Search", key="reddit_search_analyze"):
                if query:
                    with st.spinner(f"Searching Reddit for: {query}"):
                        # Log the activity
                        log_activity(tool="Social Media Analyzer (Reddit Search)", query=query, st_session=st.session_state)
                        
                        # Search Reddit
                        result = analyze_social_media(platform="reddit", analysis_type="search", query=query, limit=max_results)
                        
                        # Display results
                        if result and "error" not in result:
                            st.success(f"Search completed for query: {query}")
                            
                            # Display search results
                            if "posts" in result and result["posts"]:
                                st.subheader(f"Search Results ({len(result['posts'])} posts)")
                                
                                posts_df = pd.DataFrame(result["posts"])
                                st.dataframe(posts_df, use_container_width=True)
                                
                                for i, post in enumerate(result["posts"][:5]):  # Show first 5 posts
                                    with st.expander(f"Post {i+1}: {post.get('title', '')[:100]}...", expanded=False):
                                        st.markdown(f"**Title:** {post.get('title', 'N/A')}")
                                        st.markdown(f"**Subreddit:** r/{post.get('subreddit', 'N/A')}")
                                        st.markdown(f"**Author:** u/{post.get('author', 'N/A')}")
                                        st.markdown(f"**Date:** {post.get('created_at', 'N/A')}")
                                        st.markdown(f"**Score:** {post.get('score', 'N/A')}")
                                        st.markdown(f"**Content:** {post.get('text', 'N/A')[:500]}...")
                            
                            # Export options
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("Export as CSV"):
                                    # Create a DataFrame for search results
                                    df_export = pd.DataFrame(result.get("posts", []))
                                    csv_data = export_to_csv(df_export)
                                    st.download_button(
                                        label="Download CSV",
                                        data=csv_data,
                                        file_name=f"reddit_search_{query.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                        mime="text/csv"
                                    )
                            with col2:
                                if st.button("Export as JSON"):
                                    json_data = export_to_json(result)
                                    st.download_button(
                                        label="Download JSON",
                                        data=json_data,
                                        file_name=f"reddit_search_{query.replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                        mime="application/json"
                                    )
                        else:
                            error_msg = result.get("error", "Failed to search Reddit.") if isinstance(result, dict) else "Failed to search Reddit."
                            st.error(error_msg)
                else:
                    st.warning("Please enter a search query.")
    
    # Add similar structures for other platforms (Instagram, TikTok, YouTube)
    # For the sake of brevity, I'll only include placeholders for these platforms
    
    elif platform == "Instagram":
        st.info("Instagram analysis is limited due to API restrictions. Basic profile information only.")
        username = st.text_input("Enter Instagram username (without @):")
        
        if st.button("Analyze", key="instagram_analyze"):
            if username:
                with st.spinner(f"Analyzing Instagram profile: @{username}"):
                    # Log the activity
                    log_activity(tool="Social Media Analyzer (Instagram)", query=username, st_session=st.session_state)
                    
                    # Analyze Instagram profile
                    result = analyze_social_media(platform="instagram", analysis_type="user", query=username)
                    
                    if result and "error" not in result:
                        st.success(f"Analysis completed for Instagram user: @{username}")
                        
                        # Display profile info
                        if "profile" in result:
                            profile = result["profile"]
                            st.subheader("Profile Information")
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"**Full Name:** {profile.get('full_name', 'N/A')}")
                                st.markdown(f"**Username:** @{profile.get('username', 'N/A')}")
                                st.markdown(f"**Bio:** {profile.get('biography', 'N/A')}")
                            
                            with col2:
                                st.markdown(f"**Posts:** {profile.get('media_count', 'N/A')}")
                                st.markdown(f"**Followers:** {profile.get('follower_count', 'N/A')}")
                                st.markdown(f"**Following:** {profile.get('following_count', 'N/A')}")
                        
                        # Export options
                        if st.button("Export as JSON"):
                            json_data = export_to_json(result)
                            st.download_button(
                                label="Download JSON",
                                data=json_data,
                                file_name=f"instagram_user_{username}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json"
                            )
                    else:
                        error_msg = result.get("error", "Failed to analyze Instagram profile.") if isinstance(result, dict) else "Failed to analyze Instagram profile."
                        st.error(error_msg)
            else:
                st.warning("Please enter an Instagram username.")
    
    elif platform in ["TikTok", "YouTube"]:
        st.info(f"{platform} analysis functionality is currently limited. Basic information only.")
        username = st.text_input(f"Enter {platform} username:")
        
        if st.button("Analyze", key=f"{platform.lower()}_analyze"):
            if username:
                with st.spinner(f"Analyzing {platform} profile: {username}"):
                    # Log the activity
                    log_activity(tool=f"Social Media Analyzer ({platform})", query=username, st_session=st.session_state)
                    
                    # Analyze profile
                    result = analyze_social_media(platform=platform.lower(), analysis_type="user", query=username)
                    
                    if result and "error" not in result:
                        st.success(f"Analysis completed for {platform} user: {username}")
                        
                        # Display basic profile info
                        if "profile" in result:
                            profile = result["profile"]
                            st.subheader("Profile Information")
                            
                            for key, value in profile.items():
                                st.markdown(f"**{key.replace('_', ' ').title()}:** {value}")
                        
                        # Export options
                        if st.button("Export as JSON"):
                            json_data = export_to_json(result)
                            st.download_button(
                                label="Download JSON",
                                data=json_data,
                                file_name=f"{platform.lower()}_user_{username}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json"
                            )
                    else:
                        error_msg = result.get("error", f"Failed to analyze {platform} profile.") if isinstance(result, dict) else f"Failed to analyze {platform} profile."
                        st.error(error_msg)
            else:
                st.warning(f"Please enter a {platform} username.")

# WHOIS Lookup
with tab7:
    st.header("WHOIS Lookup")
    st.markdown("Look up domain registration information using WHOIS.")
    
    domain = st.text_input("Enter domain name (e.g., example.com):", key="whois_domain")
    
    if st.button("Lookup", key="whois_lookup"):
        if domain:
            with st.spinner(f"Performing WHOIS lookup for {domain}..."):
                # Log the activity
                log_activity(tool="WHOIS Lookup", query=domain, st_session=st.session_state)
                
                # Perform WHOIS lookup
                result = whois_lookup(domain)
                
                # Display results
                if result and "error" not in result:
                    st.success(f"WHOIS information retrieved for: {domain}")
                    
                    # Display domain information
                    st.subheader("Domain Information")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Domain Name:** {result.get('domain_name', 'N/A')}")
                        st.markdown(f"**Registrar:** {result.get('registrar', 'N/A')}")
                        st.markdown(f"**WHOIS Server:** {result.get('whois_server', 'N/A')}")
                        st.markdown(f"**Referral URL:** {result.get('referral_url', 'N/A')}")
                    
                    with col2:
                        st.markdown(f"**Updated Date:** {result.get('updated_date', 'N/A')}")
                        st.markdown(f"**Creation Date:** {result.get('creation_date', 'N/A')}")
                        st.markdown(f"**Expiration Date:** {result.get('expiration_date', 'N/A')}")
                        st.markdown(f"**Status:** {', '.join(result.get('status', ['N/A']))}")
                    
                    # Display registrant information
                    if "registrant" in result:
                        registrant = result["registrant"]
                        with st.expander("Registrant Information", expanded=True):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.markdown(f"**Name:** {registrant.get('name', 'N/A')}")
                                st.markdown(f"**Organization:** {registrant.get('organization', 'N/A')}")
                                st.markdown(f"**Street:** {registrant.get('street', 'N/A')}")
                                st.markdown(f"**City:** {registrant.get('city', 'N/A')}")
                            
                            with col2:
                                st.markdown(f"**State/Province:** {registrant.get('state', 'N/A')}")
                                st.markdown(f"**Postal Code:** {registrant.get('postal_code', 'N/A')}")
                                st.markdown(f"**Country:** {registrant.get('country', 'N/A')}")
                                st.markdown(f"**Email:** {registrant.get('email', 'N/A')}")
                    
                    # Display admin and tech contacts if available
                    for contact_type in ["admin", "tech"]:
                        if contact_type in result:
                            contact = result[contact_type]
                            with st.expander(f"{contact_type.title()} Contact Information"):
                                col1, col2 = st.columns(2)
                                with col1:
                                    st.markdown(f"**Name:** {contact.get('name', 'N/A')}")
                                    st.markdown(f"**Organization:** {contact.get('organization', 'N/A')}")
                                    st.markdown(f"**Email:** {contact.get('email', 'N/A')}")
                                
                                with col2:
                                    st.markdown(f"**Phone:** {contact.get('phone', 'N/A')}")
                                    st.markdown(f"**Fax:** {contact.get('fax', 'N/A')}")
                    
                    # Display name servers
                    if "name_servers" in result and result["name_servers"]:
                        st.subheader("Name Servers")
                        for ns in result["name_servers"]:
                            st.markdown(f"- {ns}")
                    
                    # Display raw WHOIS data
                    with st.expander("Raw WHOIS Data", expanded=False):
                        if "raw" in result:
                            st.text(result["raw"])
                        else:
                            st.info("Raw WHOIS data not available.")
                    
                    # Export options
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Export as CSV"):
                            # Flatten the WHOIS data for CSV export
                            flat_whois = {}
                            for key, value in result.items():
                                if isinstance(value, dict):
                                    for subkey, subvalue in value.items():
                                        flat_whois[f"{key}_{subkey}"] = subvalue
                                elif isinstance(value, list):
                                    flat_whois[key] = ", ".join(str(item) for item in value)
                                else:
                                    flat_whois[key] = value
                            
                            # Remove 'raw' field if it exists
                            if "raw" in flat_whois:
                                del flat_whois["raw"]
                            
                            df_export = pd.DataFrame([flat_whois])
                            csv_data = export_to_csv(df_export)
                            st.download_button(
                                label="Download CSV",
                                data=csv_data,
                                file_name=f"whois_{domain}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                mime="text/csv"
                            )
                    with col2:
                        if st.button("Export as JSON"):
                            # Remove 'raw' field from JSON export to reduce size
                            export_result = {key: value for key, value in result.items() if key != "raw"}
                            json_data = export_to_json(export_result)
                            st.download_button(
                                label="Download JSON",
                                data=json_data,
                                file_name=f"whois_{domain}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                                mime="application/json"
                            )
                else:
                    error_msg = result.get("error", "Failed to retrieve WHOIS information.") if isinstance(result, dict) else "Failed to retrieve WHOIS information."
                    st.error(error_msg)
        else:
            st.warning("Please enter a domain name.")

# Footer
st.markdown("---")
st.markdown("### 🔍 OSINT Toolbox | Created for security research and legitimate purposes only")
st.markdown("⚠️ Disclaimer: Use responsibly and ethically. Do not use for illegal activities.")
