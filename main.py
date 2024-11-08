from flask import Flask, request, Response, render_template_string
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = Flask(__name__)

search_form = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Proxy Search</title>
    <link rel="icon" type="image/png" href="favicon.png">
    <style>
        body {
            background-color: #C8A2C8; /* Lilac color */
            color: #4B0082; /* Indigo color for text */
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }

        h1 {
            font-size: 2em;
            margin-bottom: 20px;
        }

        .search-container {
            background-color: #E6E6FA; /* Light lilac color */
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            text-align: center;
        }

        input[type="text"] {
            width: 80%;
            padding: 10px;
            border: 1px solid #4B0082;
            border-radius: 5px;
            margin-bottom: 10px;
        }

        button {
            padding: 10px 20px;
            background-color: #4B0082;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }

        button:hover {
            background-color: #3A0068;
        }

        .back-button {
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="search-container">
        <h1>Cesium</h1>
        <form action="/proxy" method="get">
            <input type="text" id="url" name="url" placeholder="Enter URL (e.g., google.com)" required>
            <button type="submit">Search</button>
        </form>
    </div>
</body>
</html>
'''

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
