# Scrap from cointelegraph RSS to WordPress Auto Poster

This Python script automates the process of fetching news articles from an RSS feed (e.g., Cointelegraph) and publishing them as posts on a WordPress site. It handles categories, tags, images, and content extraction, ensuring the published posts are well-formatted and free from advertisements or unrelated content.

## Features

- Fetch articles from an RSS feed.
- Extract article content, tags, and categories using BeautifulSoup.
- Create categories and tags dynamically if they don't already exist in WordPress.
- Upload featured images for posts.
- Publish posts with a specific schedule.
- Supports WordPress authentication via application passwords.
- Uses Selenium for headless browser automation.

## Requirements

- Python 3.7 or higher
- WordPress site with REST API enabled
- GeckoDriver for Selenium (Firefox)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ronypk999/python-auto-blog-scrapper-using-selenium.git
   cd python-auto-blog-scrapper-using-selenium
   ```

2. Install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Download GeckoDriver and ensure it's available in your system's PATH or provide the path in the script.

4. Set up a WordPress application password:
   - Go to your WordPress admin panel.
   - Navigate to **Users > Profile > Application Passwords**.
   - Generate an application password and copy it.

## Configuration

1. Update the script with the following variables:

   ```python
   wordpress_url = 'https://your-wordpress-site.com'  # Your WordPress site URL
   username = 'your-username'  # Your WordPress username
   password = 'your-application-password'  # WordPress application password
   driver_path = 'driver/geckodriver.exe'  # Path to GeckoDriver
   rss_url = 'https://cointelegraph.com/rss'  # RSS feed URL
   ```

## Usage

1. Run the script:
   ```bash
   python scp.py
   ```

2. The script will:
   - Fetch articles from the specified RSS feed.
   - Check if a post with the same title already exists on WordPress.
   - Extract content, categories, and tags from the article.
   - Upload featured images.
   - Publish the article to WordPress.

## Customization

- **Time Scheduling**: For making the post as scheduled do the following modification:
  ```python
  for serial, feed in enumerate(feed.entries, start=1): # start is number of hours gap it will add between each post
  #uncomment the date and change status to 'future'
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
  ```

- **Content Filtering**: Add or modify filters for unwanted content in the `post_content` section:
  ```python
  for p_tag in post_content.find_all('p'):
      if "Magazine" in p_tag.get_text():
          p_tag.decompose()
  ```

- **Browser Options**: Enable/disable headless mode in Selenium:
  ```python
  options.add_argument("--headless")
  ```

## Dependencies

- `feedparser`: Parse RSS feeds.
- `requests`: Make HTTP requests.
- `beautifulsoup4`: Extract content from HTML.
- `selenium`: Automate browser actions.
- `python-slugify`: Generate URL-friendly slugs.

Install them with:
```bash
pip install feedparser requests beautifulsoup4 selenium python-slugify
```

## Notes

- Ensure the WordPress REST API is enabled and accessible.
- Configure proper permissions for the application password in WordPress.
- GeckoDriver must match the installed Firefox version.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contribution

Feel free to submit issues or pull requests for improvements or bug fixes!
