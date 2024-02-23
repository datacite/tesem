import httpx
from flask import current_app

CONFIRMATION_EMAIL_TEMPLATE = """
Dear {name},

Thank you for requesting the {datafile} file, your access link is now available.

This link is a one-time link and will be valid for {link_time} hours. 

You can download the file here: {url}

Please contact support@datacite.org with any questions or feedback about the file. 


DataCite
Am Welfengarten 1B
30167 Hannover
Germany
Email: support@datacite.org
"""


def send_email(to: str, subject: str, body: str) -> dict:
    response = httpx.post(
        f"{current_app.config['MAILGUN_ENDPOINT']}/messages",
        auth=("api", current_app.config["MAILGUN_API_KEY"]),
        data={
            "from": f"{current_app.config['EMAIL_FROM']} <{current_app.config['EMAIL_ADDRESS']}>",
            "to": to,
            "subject": subject,
            "text": body,
        },
    )
    response.raise_for_status()
    return response.json()


def send_confirmation_email(to: str, name: str, datafile: str, link_time: int, url: str) -> dict:
    return send_email(
        to=to,
        subject=f"Your access link for the {datafile} data file",
        body=CONFIRMATION_EMAIL_TEMPLATE.format(
            name=name,
            datafile=datafile,
            link_time=link_time,
            url=url,
        ),
    )
