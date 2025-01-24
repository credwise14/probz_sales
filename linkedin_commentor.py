import time
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import openai
from openai import OpenAI
import random
import hashlib
import os
import json



openai.api_key = 'Your open ai key'
client = OpenAI(api_key='Your open ai key')

# Selenium setup
options = Options()
options.add_argument("--start-maximized")
options.add_argument("--disable-notifications")
options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")


service = Service("/usr/local/bin/chromedriver")  # Replace with your ChromeDriver path
driver = webdriver.Chrome(service=service, options=options)

print("Connection established")

# Function to generate comments using OpenAI
def generate_comment(post_content):
    prompt = """
    
    You are tasked with generating professional LinkedIn comments to promote and engage with posts relevant to https://probz.ai, a no-code platform for building web apps, workflow automation tools using prompts.

    Guidelines:

    1. Relevance First: Before generating a comment, evaluate the relevance of the post. If the post is not directly related to no-code development, platform creation, or similar topics, return an empty comment. For example:
        a. Skip hiring announcements, personal milestones, or unrelated content.
        b. Engage only if the post aligns with the theme of no-code, automation, platform building, internal tools, dashboards, AI, agentic ai.
        c. If the post information is not in english, skip it.
        d. If someone is seeking a job or showing some certification, skip it.
    2. Avoid mentioning the name of the person who made the post.
    3. Ensure comments are professional, engaging, and tailored to the content of the post.
    4. If mentioning https://probz.ai, always include the full URL.
    5. Keep comments concise, engaging, and within 50 words.
    6. Make sure, the comment feels like it is written by a human

    Post information : {}

    Return the output in the following format : 
    {{
    "comment_text":"..."
    }}
    """

    com_prompt = prompt.format(post_content)

    response =  client.chat.completions.create(
                messages=[
                    {"role": "user", "content": com_prompt},
                ],
                model="gpt-4o",
                max_tokens=500,
                temperature=0.7
            )
    
    result = response.choices[0].message.content.strip().replace('```json','').replace('```','').strip()
    res = json.loads(result)
    return res.get("comment_text", "")

def remove_non_bmp_characters(text):
    return ''.join(c for c in text if ord(c) <= 0xFFFF)


# LinkedIn login
def login_to_linkedin():
    #driver.get("https://www.linkedin.com/search/results/content/?datePosted=%22past-24h%22&keywords=%22AI-Powered%20Development%22%20OR%20%22SaaS%20Platforms%22%20OR%20%22Build%20Apps%20Without%20Coding%22%20OR%20%22No-Code%20Workflows%22%20OR%20%22Rapid%20Prototyping%22%20OR%20%22Productivity%20Tools%22%20&origin=GLOBAL_SEARCH_HEADER&sid=q41&sortBy=%22date_posted%22")
    #driver.get("https://www.linkedin.com/search/results/content/?datePosted=%5B%22past-24h%22%5D&keywords=%22No-Code%20Platforms%22%20OR%20%22Web%20App%22%20OR%20%22No-Code%20Tools%22%20OR%20%22No-Code%20App%20Development%22%20OR%20%22Automation%20Tools%22%20OR%20%22Workflow%20Automation%22&origin=GLOBAL_SEARCH_HEADER&sid=%3AqT&sortBy=%5B%22date_posted%22%5D")
    # driver.get("https://www.linkedin.com/search/results/content/?datePosted=%22past-24h%22&keywords=%22%23nocode%22%20OR%20%22%23lowcode%22%20OR%20%22%23webdev%22&origin=GLOBAL_SEARCH_HEADER&sid=6ko&sortBy=%22date_posted%22")
    driver.get("https://www.linkedin.com/search/results/content/?authorJobTitle=%22founder%20OR%20CEO%20OR%20CTO%20OR%20COO%22&datePosted=%22past-24h%22&keywords=%22agentic%20workflow%22%20OR%20%22ai-agent%22%20OR%20%22nocode%22&origin=FACETED_SEARCH&sid=*vd&sortBy=%22date_posted%22")
    time.sleep(2)

    # Not needed if you are already logged in via your profile
    # email_input = driver.find_element(By.ID, "username")
    # email_input.send_keys(email)

    # password_input = driver.find_element(By.ID, "password")
    # password_input.send_keys(password)

    # password_input.send_keys(Keys.RETURN)
    # time.sleep(30)

def md5Hashing(input):
    text_bytes = input.encode('utf-8')
    md5_hash = hashlib.md5(text_bytes).hexdigest()
    return md5_hash


def load_processed_posts(filename):
    """Load the MD5 hashes of posts from a file into a set."""
    if not os.path.exists(filename):
        return set()
    with open(filename, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)

def save_processed_posts(filename, processed_posts):
    """Save the MD5 hashes of processed posts to a file."""
    with open(filename, "w", encoding="utf-8") as f:
        for pid in processed_posts:
            f.write(pid + "\n")

def comment_on_posts():
    PROCESSED_FILE = "processed_posts.txt"
    
    # 4. Load already processed posts to skip them
    processed_posts = load_processed_posts(PROCESSED_FILE)
    print(f"Loaded {len(processed_posts)} previously processed posts.")

    all_posts = []

    post_length = 50
    
    # 1. Keep scrolling until we collect ~100 unique, unprocessed posts
    while len(all_posts) < post_length:
        posts = driver.find_elements(By.XPATH, "//ul[@role='list']//li[contains(@class, 'artdeco-card')]")
        
        if not posts:
            print("No more posts found on page. Exiting.")
            break
        
        # Collect new posts that are not in processed_posts
        for post in posts:
            post_content = post.text.strip()
            short_content = post_content[:50]  # or however you want to identify
            md5_post_id = md5Hashing(short_content)
            
            # Skip if we already processed it or if it's in our current list
            if md5_post_id in processed_posts:
                continue
            if any(md5_post_id == p['md5'] for p in all_posts):
                continue
            
            all_posts.append({
                "element": post,
                "md5": md5_post_id,
                "content": post_content
            })
        
        if len(all_posts) < post_length:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)  # Adjust as needed
        else:
            break

    print(f"Collected {len(all_posts)} new posts. Beginning to comment.")
    
    # 2. Comment on each post one by one
    counter = 0
    for post_data in all_posts:
        post = post_data["element"]
        md5_post_id = post_data["md5"]
        post_content = post_data["content"]
        counter+=1
        
        try:
            random_number = random.randint(10, 60)
            print("Attempting to comment on a post... Wait time : ", random_number, " Counter is ", counter)
            
            cc = generate_comment(post_content)
            comment = remove_non_bmp_characters(cc)
            print("Generated comment:", comment)

            processed_posts.add(md5_post_id)

            if comment:
                # Locate the "Comment" button within the post
                comment_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        post.find_element(By.CSS_SELECTOR, "button[aria-label='Comment']")
                    )
                )
                comment_button.click()

                # Locate the comment box, type the comment
                comment_box = post.find_element(By.CSS_SELECTOR, "div.ql-editor[contenteditable='true']")
                comment_box.send_keys(comment)

                time.sleep(random_number)

                # Submit the comment
                submit_button = WebDriverWait(driver, random_number).until(
                    EC.element_to_be_clickable(
                        post.find_element(By.CSS_SELECTOR, "button.comments-comment-box__submit-button--cr")
                    )
                )
                submit_button.click()
                time.sleep(random_number)
            
            # Scroll post into view to avoid being stuck
            driver.execute_script("arguments[0].scrollIntoView(true);", post)
            time.sleep(10)

        except Exception as e:
            print(f"Error commenting on a post: {e}")
            # Scroll to the post anyway so we don't get stuck
            driver.execute_script("arguments[0].scrollIntoView(true);", post)
            time.sleep(10)

    # 3. After processing all, write the processed MD5s to the file
    save_processed_posts(PROCESSED_FILE, processed_posts)
    print(f"Done commenting. Processed posts saved to {PROCESSED_FILE}.")
    

if __name__ == "__main__":

    try:
        login_to_linkedin()
        #search_posts("Operations")
        comment_on_posts()
        #print(generate_comment("I am building an AI agent for linkedin."))
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()