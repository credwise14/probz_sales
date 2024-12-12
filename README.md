# Lead Enrichment Tool

An open-source project designed to enhance your sales leads by leveraging LinkedIn data and AI-powered analysis. This tool helps businesses evaluate and qualify potential leads efficiently, making it a valuable asset for scaling sales efforts.

## Features
- LinkedIn Integration: Extracts detailed user profiles, posts, and company information.
- OpenAI-Powered Analysis: Uses GPT-based models to evaluate leads and provide actionable insights.
- Customizable Criteria: Tailor lead evaluation prompts to match your ideal customer persona (ICP).
- Data Output: Generates user and company ratings alongside recommendations for top tools that fit the business needs.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/lead-enrichment-tool.git
   cd lead-enrichment-tool
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment:
   - LinkedIn Credentials: Use a dedicated LinkedIn account to avoid rate limits.
   - OpenAI API Key: Obtain your API key from the [OpenAI platform](https://platform.openai.com/).

4. Modify the code as needed:
   - Update the placeholders in the `system_prompt` and `user_prompt` with your business details.

## Usage

1. Prepare a CSV file with columns for LinkedIn and Company LinkedIn links.
2. Update the `file_path` variable in the script to point to your CSV file.
3. Run the script:
   ```bash
   python lead_enrichment_tool.py
   ```

4. Output will include:
   - User and company ratings.
   - Recommendations for tools based on the analysis.

## Example Output

A JSON structure with the following format:
```json
{
  "user_rating": 8,
  "company_rating": 7,
  "top_tools": [
    {
      "tool_name": "CRM Optimizer",
      "description": "Improves lead tracking and conversion."
    },
    {
      "tool_name": "Data Insights Dashboard",
      "description": "Provides real-time analytics for sales performance."
    }
  ]
}
```

## Requirements

- Python 3.8+
- Libraries:
  - `linkedin-api`
  - `openai`
  - `requests`
  - `pandas`

For a full list of dependencies, see `requirements.txt`.

## Notes
- Ensure compliance with LinkedIn's terms of service when scraping data.
- Use a dedicated LinkedIn account to avoid interruptions.

## Contributions
Contributions are welcome! Please fork the repository, make your changes, and submit a pull request.