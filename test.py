# import cloudscraper
# import re
# from bs4 import BeautifulSoup
# from flask import Flask
#
# app = Flask(__name__)
#
# url = "https://in.bookmyshow.com/buytickets/saripodhaa-sanivaaram-vizag-visakhapatnam/movie-viza-ET00388631-MT/20240914"
#
# scraper = cloudscraper.create_scraper()
#
# # Custom headers to mimic a browser request
# headers = {
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
#     "Referer": "https://in.bookmyshow.com/",
#     "Accept-Language": "en-US,en;q=0.9"
# }
#
# # Send the request with headers
# response = scraper.get(url, headers=headers)
#
# if response.status_code == 200:
#     print("Request successful!")
#
#     # Parse the HTML content
#     soup = BeautifulSoup(response.content, "html.parser")
#
#     # Extract the title
#     title = soup.find("title").text
#     movie_NamesArray = soup.find_all("a", class_=re.compile("__venue-name", re.I))
#     theatre_names = []
#     for i in movie_NamesArray:
#         theatre_names.append(i.get_text().strip())
#     print("Title:", title)
#     for i in theatre_names:
#         if "inox" in i.lower():
#             print("yes")
#             break
#     print("Theatre:", theatre_names)
#
# else:
#     print("Request failed. Status code:", response.status_code)
#
#
# @app.route("/")
# def hello_world():
#     print(response.status_code)
#     return f'{response}'
#
#
# if __name__ == "__main__":
#     app.run(debug=False)


from flask import Flask, request, render_template_string
import cloudscraper
import re
from bs4 import BeautifulSoup

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def index():

    # Default message
    message = ""

    # Check if the form has been submitted
    if request.method == "POST":
        # Get the URL entered by the user
        url = request.form["url"]
        searched_theater = request.form["theater_name"]

        # Set up the scraper
        scraper = cloudscraper.create_scraper()

        # Custom headers to mimic a browser request
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Referer": "https://in.bookmyshow.com/",
            "Accept-Language": "en-US,en;q=0.9"
        }

        # Send the request with headers
        response = scraper.get(url, headers=headers)

        if response.status_code == 200:
            message = "Request successful!"

            # Parse the HTML content
            soup = BeautifulSoup(response.content, "html.parser")

            # Extract the title
            title = soup.find("title").text

            # Find all theatres
            movie_NamesArray = soup.find_all("a", class_=re.compile("__venue-name", re.I))
            theatre_names = [i.get_text().strip() for i in movie_NamesArray]

            # Check for 'inox' in theatre names
            searched_theater_found = any(searched_theater in name.lower() for name in theatre_names)

            # Format the output
            message += f"<br>Title: {title}<br>"
            message += f"Theatres: {', '.join(theatre_names)}<br>"
            if searched_theater_found:
                message += "Yes, "+searched_theater+" theatre found!"
            else:
                message += "No "+searched_theater+" theatre NOT found."
        else:
            message = f"Request failed. Status code: {response.status_code}"

    # Render the HTML form and result
    return render_template_string("""
    <html>
        <body>
            <h2>Enter Movie URL</h2>
            <form method="POST">
                <input type="text" name="url" placeholder="Enter URL" required>
                <br>
                <input type="text" name="theater_name" placeholder="Enter theater name" required>
                <input type="submit" value="Submit">
            </form>
            <hr>
            <p>{{ message|safe }}</p>
        </body>
    </html>
    """, message=message)


if __name__ == "__main__":
    app.run(debug=True)
