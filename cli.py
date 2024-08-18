import requests
from bs4 import BeautifulSoup
import pdfkit
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import json
from tempfile import NamedTemporaryFile
import argparse

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
    analyze_with_openai(title, price, description, pdf_content)

def analyze_with_openai(title, price, description, pdf_content):
    api_url = 'https://api.openai.com/v1/completions'
    headers = {
        'Authorization': f'Bearer {args.api_key}',
        'Content-Type': 'application/json',
    }

    data = {
        "model": "text-davinci-003",
        "prompt": f"Analyze the following Craigslist antique description and the attached PDF screenshot of the listing to estimate its market value: \n\n{description}",
        "max_tokens": 50,
        "files": [
            {
                "filename": "listing.pdf",
                "content": pdf_content.decode('latin1'),  # Encoding to safely include in JSON
                "type": "application/pdf"
            }
        ]
    }

    response = requests.post(api_url, headers=headers, json=data)
    result = response.json()

    estimated_value = result['choices'][0]['text'].strip()
    print(f"Title: {title}")
    print(f"Price: {price}")
    print(f"Estimated Market Value: {estimated_value}\n")

def main():
    parser = argparse.ArgumentParser(description='Craigslist Antiques Scraper and Market Value Estimator')
    parser.add_argument('urls', nargs='+', help='The URLs of Craigslist antique listings to scrape (e.g., https://newyork.craigslist.org/mnh/atq/d/pair-of-antique-kpm-figurines/7769922452.html)')
    parser.add_argument('--api-key', type=str, required=True, help='Your OpenAI API key')

    global args
    args = parser.parse_args()

    # Process each URL passed in the command line
    for url in args.urls:
        parse_listing(url)

if __name__ == '__main__':
    main()
