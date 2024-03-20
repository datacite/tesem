import httpx
from flask import current_app

CONFIRMATION_EMAIL_TEMPLATE = """
Dear {name},

Thank you for requesting the {datafile} file, your access link is now available.

This link will be valid for {link_time} hours. 

You can download the file here: {url}

For more information about the file and its contents, please see the landing page: {landing_page}

Please contact support@datacite.org with any questions or feedback about the file. 

--
DataCite – International Data Citation Initiative e.V.
Web: https://datacite.org/ | Blog: https://datacite.org/blog/ | X: https://twitter.com/datacite
LinkedIn: https://www.linkedin.com/company/datacite | Mastodon: https://openbiblio.social/@datacite 
Support Desk: support@datacite.org | Support Site: https://support.datacite.org/ | PID Forum: https://www.pidforum.org/ 
Postal address: DataCite -- Welfengarten 1B, 30167 Hannover, Germany
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


def send_confirmation_email(to: str, name: str, datafile: str, link_time: int, url: str, landing_page: str) -> dict:
    return send_email(
        to=to,
        subject=f"Your access link for the {datafile} data file",
        body=CONFIRMATION_EMAIL_TEMPLATE.format(
            name=name,
            datafile=datafile,
            link_time=link_time,
            url=url,
            landing_page=landing_page,
        ),
    )
