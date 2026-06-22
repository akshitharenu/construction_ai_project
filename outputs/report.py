import os
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from config import settings


def send_report_email(report_content: str, project_id: str, date: str) -> None:
    sg = sendgrid.SendGridAPIClient(api_key=settings.sendgrid_api_key)
    html = report_content.replace("\n", "<br>")
    mail = Mail(
        from_email=Email(settings.report_email_from),
        to_emails=To(settings.report_email_to),
        subject=f"Daily Site Report — {project_id} — {date}",
        html_content=Content("text/html", html),
    )
    response = sg.client.mail.send.post(request_body=mail.get())
    print(f"[REPORT] Email sent — status {response.status_code}")


def save_report_to_file(report_content: str, project_id: str, date: str) -> str:
    os.makedirs("reports", exist_ok=True)
    filename = f"reports/{project_id}_{date}.md"
    with open(filename, "w") as f:
        f.write(f"# Daily Report — {project_id} — {date}\n\n{report_content}")
    print(f"[REPORT] Saved to {filename}")
    return filename
