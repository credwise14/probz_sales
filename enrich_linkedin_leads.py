from linkedin_api import Linkedin
import csv
from openai import OpenAI
import requests
import json
import pandas as pd
import time
import math


# Authenticate using any Linkedin user account credentials
# email and pwd 
# If possible, create a new linkedin profile with some email
api = Linkedin('xyz@gmail.com', 'xyz')

#Enter your open ai key here
client = OpenAI(api_key="sk-ROExwu3ndqa4ZtPdwyDrT")

model_engine = "gpt-4o" 

system_prompt = """
You have to evaluate the lead based on their linkedin profile, their posts and their company information.

Qualify whether the business and the lead is right fit for {{Your company name}}. 
{{Enter a short description about your company here}}

RETURN JUST THE FINAL REQUESTED JSON OUTPUT
"""

def get_completion(prompt, model=model_engine):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]    
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0
    )
    response_message = response.choices[0].message.content
    return response_message


def get_user_date(public_id):
    # Extracting summary
    data = api.get_profile(public_id)
    summary = data.get('summary', '')

    # Extracting experience (title and description)
    experience = []
    for exp in data.get('experience', []):
        experience.append({
            'title': exp.get('title', ''),
            'description': exp.get('description', '')
        })

    # Extracting languages
    languages = [lang.get('name', '') for lang in data.get('languages', [])]

    # Extracting skills
    skills = [skill.get('name', '') for skill in data.get('skills', [])]

    # Creating a final dictionary for the required fields
    final_output = {
        'summary': summary,
        'experience': experience,
        'languages': languages,
        'skills': skills
    }
    return final_output


def extract_user_text(public_id, post_count):
    posts = api.get_profile_posts(public_id=public_id, post_count=post_count)
    user_texts = []
    
    for post in posts:
        if 'commentary' in post and 'text' in post['commentary']:
            user_text = post['commentary']['text']['text']
            user_texts.append(user_text)
    
    return user_texts

def get_company_info(public_id):
    # Extracting company name
    data = api.get_company(public_id)
    company_name = data.get('name', '')

    # Extracting tagline
    tagline = data.get('tagline', '')

    # Extracting description
    description = data.get('description', '')

    # Extracting location (with null checks for nested fields)
    location_data = data.get('headquarter', {})
    location = f"{location_data.get('line1', '')} {location_data.get('line2', '')}, " \
               f"{location_data.get('city', '')}, {location_data.get('geographicArea', '')} " \
               f"{location_data.get('postalCode', '')}, {location_data.get('country', '')}"

    # Extracting phone number
    phone = data.get('phone', {}).get('number', '')

    # Extracting website URL
    website = data.get('companyPageUrl', '')

    # Extracting industry (handles the possibility of missing 'companyIndustries' or no industries)
    industry_data = data.get('companyIndustries', [])
    industry = industry_data[0].get('localizedName', '') if industry_data else ''

    # Extracting staff count
    staff_count = data.get('staffCount', 0)

    # Extracting founded year
    founded_year = data.get('foundedOn', {}).get('year', '')

    # Creating a final dictionary with the extracted information
    final_output = {
        'company_name': company_name,
        'tagline': tagline,
        'description': description,
        'location': location,
        'phone': phone,
        'website': website,
        'industry': industry,
        'staff_count': staff_count,
        'founded_year': founded_year
    }

    return final_output


# co_data = api.get_company("globalbuilding")
# print(get_company_info(co_data))

user_prompt = """
Analyze the user's experiences, languages, and educational background to determine if they align with my target persona.

{{ Enter your ICP here like Sales managers with 5+ YOE etc}}

### Common Problems:
{{Enter the common problems your target user face}}

### Task:
Based on the provided user persona, rate this user on a scale from 1-10 on how well they fit as a potential target for my business.

### Inputs:
**User Profile:**  
{user_profile}  

**User Posts:**  
{user_posts}  

**Company Information:**  
{company_information}  

### Output the following json (Give max top 3 tools.):

{{
"user_rating": rating between 1-10
"company_rating": rating between 1-10
top_tools : [
{{"tool_name":"name of the tool to be built via Probz","description":"tool description and also how it can help the company"}}
]
}}
"""

def read_and_print_csv(file_path, out_path):
    try:
        cnt = 0
        df = pd.read_csv(file_path)
        data=[]
        for index,row in df.iterrows():
            data.append(row)

        for index,row in df.iterrows():
            try: 
                print("Currently processing : ", cnt)
                linkedin_link = row.get('LinkedIn Link', '')
                company_linkedin_link = row.get('Company LinkedIn Link', '')
                top_tools = row.get('top_tools', '')
                print(top_tools)
                if top_tools != '' and not math.isnan(top_tools):
                    continue
                # This is to ensure linkedin allow us to scrape the lead information
                time.sleep(120)

                # Extract public IDs
                linkedin_id = linkedin_link.split('/')[-1] if linkedin_link else 'N/A'
                company_linkedin_id = company_linkedin_link.split('/')[-1] if company_linkedin_link else 'N/A'

                if linkedin_id != 'N/A' and company_linkedin_id != 'N/A':
                    user = get_user_date(linkedin_id)
                    post = extract_user_text(linkedin_id, 10)
                    co = get_company_info(company_linkedin_id)

                    user_json = json.dumps(user, indent=4)
                    post_json = json.dumps(post, indent=4)
                    co_json = json.dumps(co, indent=4)

                    formatted_prompt = user_prompt.format(
                        user_profile=user_json,
                        user_posts=post_json,
                        company_information=co_json
                    )
                    # formatted_prompt = prompt

                    out = get_completion(formatted_prompt)
                    formatted_out = json.loads(out.replace('```json', '').replace('```', ''))
                    user_rating = formatted_out.get('user_rating', 0)
                    company_rating = formatted_out.get('company_rating', 0)
                    top_tools = formatted_out.get('top_tools', [])
                    top_tools_str = [f"{tool['tool_name']}: {tool['description']}" for tool in top_tools if isinstance(tool, dict) and 'tool_name' in tool and 'description' in tool]
                    updated_row=row.copy()
                    # Update the row with ratings and tools
                    updated_row['user_rating'] = user_rating
                    updated_row['company_rating'] = company_rating
                    updated_row['top_tools'] = ', '.join(top_tools_str)  # Convert list to string
                    data[index]=updated_row
                    ## write here
                    df2=pd.DataFrame(data)
                    df2.to_csv(out_path,index_label=False) 
            except Exception as e:
                print(f"An error occurred here: {e}")
        
        df2=pd.DataFrame(data)
        df2.to_csv(out_path,index_label=False) 
        print(f"Data has been updated and written back to the file: {out_path}")
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")



# Replace with your actual file path
file_path = "Path to the fle"
read_and_print_csv(file_path, file_path)
