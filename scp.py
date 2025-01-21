import feedparser
import requests
from requests.auth import HTTPBasicAuth
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import time
import os
import datetime
from slugify import slugify
def get_or_create_category(category_name):
    global username, password, categories_api_url
    # Fetch categories and check if the category exists
    response = requests.get(categories_api_url, auth=HTTPBasicAuth(username, password), params={'search': category_name})
    
    if response.status_code == 200:
        categories = response.json()
        if categories:  # Category exists
            return categories[0]['id']  # Return the ID of the first matching category
        else:  # Category doesn't exist, so create it
            # Endpoint to create a new category
            create_category_data = {
                'name': category_name,
            }
            create_response = requests.post(categories_api_url, json=create_category_data, auth=HTTPBasicAuth(username, password))
            
            if create_response.status_code == 201:
                return create_response.json()['id']  # Return the newly created category's ID
            else:
                print(f"Error creating category: {create_response.status_code}")
                return None
    else:
        print(f"Error fetching categories: {response.status_code}")
        return None

# Function to check if a tag exists, and create if not
def get_or_create_tag(tag_name):
    global username,password,tags_api_url
    # Fetch tags and check if the tag exists
    response = requests.get(tags_api_url, auth=HTTPBasicAuth(username, password), params={'search': tag_name})
    
    if response.status_code == 200:
        tags = response.json()
        if tags:  # Tag exists
            return tags[0]['id']  # Return the ID of the first matching tag
        else:  # Tag doesn't exist, so create it
            # Endpoint to create a new tag
            create_tag_data = {
                'name': tag_name,
            }
            create_response = requests.post(tags_api_url, json=create_tag_data, auth=HTTPBasicAuth(username, password))
            
            if create_response.status_code == 201:
                return create_response.json()['id']  # Return the newly created tag's ID
            else:
                print(f"Error creating tag: {create_response.status_code}")
                return None
    else:
        print(f"Error fetching tags: {response.status_code}")
        return None
def upload_image(image_url):
    global driver
    # Step 1: Download the image from the external URL
    driver.get(image_url)
    image = driver.find_element(By.TAG_NAME, 'img')
     # File path to the image
    file_path = "image.png"
    image.screenshot(file_path)

    # Headers for the request
    headers = {
        'Content-Disposition': f'attachment; filename={file_path.split("/")[-1]}'  # Extract filename dynamically
    }

    # Step 4: Upload the image to WordPress
    with open(file_path, 'rb') as file_data:
        response = requests.post(
            media_api_url,
            headers=headers,
            files={'file': file_data},  # Pass the file object
            auth=HTTPBasicAuth(username, password)
        )


    os.remove(file_path)
    image_data = response.json()
    return image_data['id']

                            

# URL of the Cointelegraph RSS feed
rss_url = 'https://cointelegraph.com/rss'
# Set up the path to GeckoDriver
driver_path = "driver/geckodriver.exe"  # Update this to the actual path to your GeckoDriver
# Set up Firefox options
options = Options()
options.add_argument("--headless")  # Add argument to ensure headless mode
# Initialize the service and WebDriver
service = Service(driver_path)
driver = webdriver.Firefox(service=service, options=options)
# WordPress site URL and authentication details
wordpress_url = 'https://cryptonani.com'  # Replace with your site URL
username = ''  # Your WordPress username
password = ''  # WordPress application password

# WordPress API endpoint for creating posts
api_url = f'{wordpress_url}/wp-json/wp/v2/posts'
# WordPress API endpoint for fetching/creating tags
tags_api_url = f'{wordpress_url}/wp-json/wp/v2/tags'
# WordPress API endpoint for fetching/creating category
categories_api_url = f'{wordpress_url}/wp-json/wp/v2/categories'
# API endpoint for media upload
media_api_url = f'{wordpress_url}/wp-json/wp/v2/media'
# Fetch the RSS feed using requests
response = requests.get(rss_url, verify=True)

# Parse the RSS feed
feed = feedparser.parse(response.content)
# Get the current time
current_time = datetime.datetime.now()


for serial, feed in enumerate(feed.entries, start=1):
    title = feed.title
    slug = slugify(title)
    check_post_url = f'{api_url}?slug={slug}'
    response = requests.get(check_post_url, auth=HTTPBasicAuth(username, password))
    
    if response.status_code == 200 and len(response.json()) > 0:
        print(f"Post exists {title}")
        continue
    else:
        url = feed.link
        image_url = feed.media_content[0]['url']
        # Open the URL
        driver.get(url)

        # Allow the page to load
        time.sleep(5)

        # Get the page source and parse it using BeautifulSoup
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # Find the first article on the page
        first_article = soup.find('article')

        if first_article:
            # Data for the new post
            category_ids_str = []
            if 'tags' in feed and feed.tags:
                category_list = [item.term for item in feed.tags]
                category_ids = [get_or_create_category(category_name) for category_name in category_list]
                category_ids_str = ",".join(map(str, category_ids)) 
            tags_list = soup.find(class_='tags-list__list')
            tag_texts = [tag.find('a').text.strip() for tag in tags_list]
            tag_ids = [get_or_create_tag(tag_name) for tag_name in tag_texts]
            tag_ids_str = ",".join(map(str, tag_ids)) 
            post_lead = soup.find(class_='post__lead').get_text(strip=True)
            image_id = upload_image(image_url)
            post_content = soup.find(class_='post-content')
            
            for advertisement in post_content.find_all('advertisement'):
                advertisement.decompose()
            for div in post_content.find_all('div'):
                div.decompose()
            for form in post_content.find_all('form'):
                form.decompose()
                
            # Loop through each <p> tag 
            for p_tag in post_content.find_all('p'):
                # Check if the tag contains the word "Magazine"
                if "Magazine" in p_tag.get_text():
                    p_tag.decompose()  # Remove the specific <p> tag

                if "Related" in p_tag.get_text():
                    p_tag.decompose()  
            # Add 1 hour to the current time
            one_hour_later = current_time + datetime.timedelta(hours=serial)

            # Format the time in ISO 8601 format for the WordPress API
            formatted_time = one_hour_later.isoformat()        
            post_data = {
                'title': title,   # Title of the post
                'content': str(post_content),  # Content of the post
                'status': 'publish',  # Post status (future, publish, etc.)
                'tags':tag_ids_str,
                'excerpt': post_lead,
                'categories':category_ids_str,
                # 'date':formatted_time,
                'featured_media':image_id
            }
            # Send POST request to create the post
            response = requests.post(api_url, data=post_data, auth=HTTPBasicAuth(username, password))

            # Check if the post was created successfully
            if response.status_code == 201:
                print('Post created successfully!')
                print('Post URL:', response.json()['link'])
            else:
                print(f'Error: {response.status_code}')
                print(response.text)
        else:
            print("No <article> tag found on the page.")

driver.quit()

