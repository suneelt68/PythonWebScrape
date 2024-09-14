from flask import Flask, request, render_template_string
import firebase_admin
from firebase_admin import credentials, messaging
import cloudscraper
import re
from bs4 import BeautifulSoup

app = Flask(__name__)

# Initialize Firebase Admin SDK
cred = credentials.Certificate('config/firebase_key.json')
firebase_admin.initialize_app(cred)


def send_notification(title, body):
    # Define the message payload
    message = messaging.Message(
        notification=messaging.Notification(
            title="High Priority Notification",
            body="This is  a high-priority notification!",
        ),
        android=messaging.AndroidConfig(
            priority="high",  # Set the priority to high
            notification=messaging.AndroidNotification(
                sound="default",  # Set the sound to default
                click_action="FLUTTER_NOTIFICATION_CLICK",  # Optional action when clicked
            ),
        ),
        topic="theater_updates",  # Send to a topic, token, or condition
    )

    # Send the message
    response = messaging.send(message)
    print(f'Successfully  sent message: {response}')


@app.route("/", methods=["GET", "POST"])
def index():
    # Default message
    message = ""
    # send_notification("aaa", "bb b")

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
                message += "Yes, " + searched_theater + " theatre found!"
                send_notification("" + searched_theater + " Theatre Found ", "ehjgsjf")
                # send_notification(
                #     "" + searched_theater + " Theatre Found , " + searched_theater + " is available for the movie '{" + title + "}'.")
            else:
                message += "No " + searched_theater + " theatre NOT found."
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
    app.run(debug=False)
