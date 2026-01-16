"""
Email service for authentication flows using SendGrid.
"""
import os
from typing import Optional

# SendGrid imports (graceful fallback if not installed)
try:
    import sendgrid
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

# Environment configuration
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
FROM_EMAIL = os.getenv("FROM_EMAIL", "noreply@example.com")
FROM_NAME = os.getenv("FROM_NAME", "Executive Analytics")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:8501")


def _is_email_configured() -> bool:
    """Check if email service is properly configured."""
    return SENDGRID_AVAILABLE and bool(SENDGRID_API_KEY)


async def send_password_reset_email(to_email: str, reset_token: str) -> bool:
    """
    Send password reset email via SendGrid.

    Args:
        to_email: Recipient email address
        reset_token: Password reset token

    Returns:
        True if email sent successfully, False otherwise
    """
    if not _is_email_configured():
        print(f"[Email Service] SendGrid not configured. Reset token for {to_email}: {reset_token}")
        return False

    reset_url = f"{FRONTEND_URL}/reset-password?token={reset_token}"

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #2563eb; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 30px; background: #f9fafb; }}
            .button {{
                display: inline-block;
                background: #2563eb;
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Password Reset Request</h1>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>We received a request to reset your password for your Executive Analytics account.</p>
                <p>Click the button below to reset your password:</p>
                <p style="text-align: center;">
                    <a href="{reset_url}" class="button">Reset Password</a>
                </p>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; font-size: 14px; color: #666;">
                    {reset_url}
                </p>
                <p><strong>This link will expire in 1 hour.</strong></p>
                <p>If you didn't request a password reset, you can safely ignore this email.</p>
            </div>
            <div class="footer">
                <p>This is an automated message from Executive Analytics.</p>
                <p>Please do not reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """

    plain_content = f"""
    Password Reset Request

    We received a request to reset your password for your Executive Analytics account.

    Click here to reset your password:
    {reset_url}

    This link will expire in 1 hour.

    If you didn't request a password reset, you can safely ignore this email.

    --
    Executive Analytics
    """

    try:
        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)

        message = Mail(
            from_email=Email(FROM_EMAIL, FROM_NAME),
            to_emails=To(to_email),
            subject="Password Reset Request - Executive Analytics",
        )
        message.add_content(Content("text/plain", plain_content))
        message.add_content(Content("text/html", html_content))

        response = sg.send(message)

        if response.status_code in (200, 201, 202):
            print(f"[Email Service] Password reset email sent to {to_email}")
            return True
        else:
            print(f"[Email Service] Failed to send email. Status: {response.status_code}")
            return False

    except Exception as e:
        print(f"[Email Service] Error sending email: {e}")
        return False


async def send_welcome_email(to_email: str) -> bool:
    """
    Send welcome email to new users (optional enhancement).

    Args:
        to_email: New user's email address

    Returns:
        True if email sent successfully, False otherwise
    """
    if not _is_email_configured():
        print(f"[Email Service] SendGrid not configured. Welcome email skipped for {to_email}")
        return False

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: #2563eb; color: white; padding: 20px; text-align: center; }}
            .content {{ padding: 30px; background: #f9fafb; }}
            .button {{
                display: inline-block;
                background: #2563eb;
                color: white;
                padding: 12px 30px;
                text-decoration: none;
                border-radius: 5px;
            }}
            .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to Executive Analytics!</h1>
            </div>
            <div class="content">
                <p>Hello,</p>
                <p>Thank you for creating an account with Executive Analytics.</p>
                <p>You can now connect your database and start asking questions in natural language.</p>
                <p style="text-align: center;">
                    <a href="{FRONTEND_URL}" class="button">Get Started</a>
                </p>
            </div>
            <div class="footer">
                <p>This is an automated message from Executive Analytics.</p>
            </div>
        </div>
    </body>
    </html>
    """

    try:
        sg = sendgrid.SendGridAPIClient(api_key=SENDGRID_API_KEY)

        message = Mail(
            from_email=Email(FROM_EMAIL, FROM_NAME),
            to_emails=To(to_email),
            subject="Welcome to Executive Analytics!",
        )
        message.add_content(Content("text/html", html_content))

        response = sg.send(message)
        return response.status_code in (200, 201, 202)

    except Exception as e:
        print(f"[Email Service] Error sending welcome email: {e}")
        return False
