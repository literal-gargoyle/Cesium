from flask import Flask, request, Response, render_template_string
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = Flask(__name__)

search_form = "index.html"

@app.route('/')
def home():
    return render_template_string(search_form)

@app.route('/proxy')
def proxy():
    url = request.args.get('url')
    if not url:
        return "No URL provided", 400

    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url  # Default to http if no scheme is provided

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Update all links and resources to go through the proxy
        for tag in soup.find_all(['a', 'img', 'link', 'script']):
            if tag.has_attr('href'):
                full_url = urljoin(url, tag['href'])
                tag['href'] = f"/proxy?url={full_url}"
            if tag.has_attr('src'):
                full_url = urljoin(url, tag['src'])
                tag['src'] = f"/proxy?url={full_url}"

        # Add the back button to return to the main page
        back_button_html = '<div class="back-button"><a href="/">Back to Search</a></div>'
        soup.body.append(BeautifulSoup(back_button_html, 'html.parser'))

        content = str(soup)

        excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
        headers = [(name, value) for (name, value) in response.raw.headers.items() if name.lower() not in excluded_headers]
        return Response(content, response.status_code, headers)
    except Exception as e:
        return f"An error occurred: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
