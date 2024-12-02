from flask import Flask, request, jsonify, render_template
import requests
from bs4 import BeautifulSoup
import re
import lxml

app = Flask(__name__)

def extract_email(soup):
    email = soup.find(string=re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'))
    return email if email else "Not Available"

def extract_address(soup):
    keywords = ["Street", "Address", "No."]
    possible_addresses = soup.find_all(text=lambda text: any(keyword in text for keyword in keywords))

    if possible_addresses:
        addresses = []
        for addr in possible_addresses:
            context = [addr.strip().replace('\n', '')]
            next_tag = addr
            for _ in range(3):
                next_tag = next_tag.find_next(text=True)
                if next_tag:
                    context.append(next_tag.strip().replace('\n', ''))
            addresses.append(' '.join(context))
        return ', '.join(addresses)

    return "No address found"

def extract_phone_numbers(soup):
    phone_pattern = re.compile(r'\+?\d[\d\s()-]{8,}\d')
    text = soup.get_text()
    phone_numbers = phone_pattern.findall(text)

    cleaned_phone_numbers = []
    for phone in phone_numbers:
        phone = phone.replace('\n', ' ').strip()
        if len(re.sub(r'\D', '', phone)) > 6:
            cleaned_phone_numbers.append(phone)
    return cleaned_phone_numbers

def get_company_info(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'lxml')
        page_title = soup.title.string if soup.title else "No Title"

        company_info = {
            "Website Status": "Working",
            "Title": page_title,
            "Email": extract_email(soup),
            "Address": extract_address(soup),
            "Phone Numbers": extract_phone_numbers(soup)
        }
    else:
        company_info = {"Website Status": "Not Working"}

    return company_info

@app.route('/', methods=['GET', 'POST'])

def home():
    if request.method == 'POST':
        url = request.form.get('url')
        company_info = get_company_info(url)
        return render_template('index.html',
                                title=company_info['Title'],
                                email=company_info['Email'],
                                address=company_info['Address'],
                                phone_numbers=', '.join(company_info['Phone Numbers']))
                                
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)