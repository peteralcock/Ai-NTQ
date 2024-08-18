import requests
from bs4 import BeautifulSoup
import pdfkit
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import json
from tempfile import NamedTemporaryFile
import argparse
from openai import OpenAI

# Initialize the OpenAI client
client = OpenAI(api_key="YOUR_OPENAI_API_KEY")
def parse_listing(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    title = soup.select_one('span#titletextonly').text
    price = soup.select_one('span.price').text if soup.select_one('span.price') else 'N/A'
    description = soup.select_one('section#postingbody').text

    # Take a screenshot using Selenium
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))
    driver.get(url)
    screenshot = driver.get_screenshot_as_png()
    driver.quit()

    # Convert the screenshot to PDF
    with NamedTemporaryFile(delete=False, suffix=".png") as temp_png:
        temp_png.write(screenshot)
        temp_png.flush()
        temp_pdf = NamedTemporaryFile(delete=False, suffix=".pdf")
        pdfkit.from_file(temp_png.name, temp_pdf.name)

    # Read the PDF content
    with open(temp_pdf.name, 'rb') as pdf_file:
        pdf_content = pdf_file.read()

    # Clean up temporary files
    temp_png.close()
    temp_pdf.close()

    # Send the information to the OpenAI API
    analyze_with_openai(title, price, description)

def analyze_with_openai(title, price, description):
    # Create the chat completion
    completion = client.chat.completions.create(
        model="gpt-4o-mini",  # Replace with the correct model ID if necessary
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": f"Estimate the market value of the following antique item based on its description:\n\n{description}"
            }
        ]
    )

    # Extract and print the message content from the response
    print(f"Title: {title}")
    print(f"Price: {price}")
    estimated_value = completion.choices[0].message.content.strip()

    print(estimated_value)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Craigslist Antiques Scraper and Market Value Estimator')
    parser.add_argument('url', type=str, help='The URL of the Craigslist antique listing to scrape')
    parser.add_argument('--api-key', type=str, required=True, help='Your OpenAI API key')

    args = parser.parse_args()

    # Set the API key for the OpenAI client
    client.api_key = args.api_key

    # Start the process
    parse_listing(args.url)

