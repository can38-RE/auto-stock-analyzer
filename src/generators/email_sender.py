"""Email sender module for sending reports via SMTP."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path
from datetime import datetime

from loguru import logger


class EmailSender:
    """Send emails via SMTP."""
    
    def __init__(self, smtp_server: str = "smtp.qq.com", smtp_port: int = 465):
        """Initialize email sender.
        
        Args:
            smtp_server: SMTP server address
            smtp_port: SMTP server port (465 for SSL, 587 for TLS)
        """
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
    
    def send_report(self, sender_email: str, auth_code: str, 
                    receiver_email: str, report_path: str) -> bool:
        """Send report via email.
        
        Args:
            sender_email: Sender's email address
            auth_code: SMTP authorization code
            receiver_email: Receiver's email address
            report_path: Path to the report file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Determine session based on Beijing time (UTC+8)
            now = datetime.utcnow()  # GitHub Actions uses UTC
            beijing_hour = (now.hour + 8) % 24  # Convert to Beijing time
            weekday = now.weekday()  # 0=Monday, 6=Sunday
            
            if weekday >= 5:  # Weekend
                session = "周末预测"
                emoji = "📅"
            elif beijing_hour < 12:
                session = "早盘"
                emoji = "🌅"
            else:
                session = "午盘"
                emoji = "☀️"
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = f"{emoji} {session}分析报告 - {now.strftime('%Y-%m-%d')} | 1900元激进策略"
            
            # Read report content
            report_path = Path(report_path)
            if not report_path.exists():
                logger.error(f"Report file not found: {report_path}")
                return False
            
            with open(report_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Create HTML part
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Send email via SSL
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(sender_email, auth_code)
                server.send_message(msg)
            
            logger.info(f"Email sent successfully to {receiver_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_report_with_attachment(self, sender_email: str, auth_code: str,
                                    receiver_email: str, report_path: str,
                                    subject: str = None) -> bool:
        """Send report as email attachment.
        
        Args:
            sender_email: Sender's email address
            auth_code: SMTP authorization code
            receiver_email: Receiver's email address
            report_path: Path to the report file
            subject: Email subject (optional)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = subject or f"AutoStockAnalyzer 每日分析报告 - {datetime.now().strftime('%Y-%m-%d')}"
            
            # Add body
            body = f"""
            <html>
            <body>
                <h2>AutoStockAnalyzer 每日分析报告</h2>
                <p>日期: {datetime.now().strftime('%Y-%m-%d')}</p>
                <p>请查看附件中的HTML报告文件。</p>
                <p><a href="https://can38-re.github.io/auto-stock-analyzer/">在线查看报告</a></p>
            </body>
            </html>
            """
            msg.attach(MIMEText(body, 'html', 'utf-8'))
            
            # Attach report file
            report_path = Path(report_path)
            if report_path.exists():
                with open(report_path, 'rb') as f:
                    attachment = MIMEBase('text', 'html')
                    attachment.set_payload(f.read())
                
                encoders.encode_base64(attachment)
                attachment.add_header(
                    'Content-Disposition',
                    f'attachment; filename="{report_path.name}"'
                )
                msg.attach(attachment)
            
            # Send email via SSL
            with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port) as server:
                server.login(sender_email, auth_code)
                server.send_message(msg)
            
            logger.info(f"Email with attachment sent successfully to {receiver_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email with attachment: {e}")
            return False


def send_daily_report(report_path: str) -> bool:
    """Send daily report email.
    
    Args:
        report_path: Path to the report file
        
    Returns:
        True if successful, False otherwise
    """
    import os
    
    # Get email configuration from environment
    sender_email = os.getenv("QQ_EMAIL")
    auth_code = os.getenv("QQ_SMTP_AUTH_CODE")
    receiver_email = os.getenv("RECEIVER_EMAIL", "437590034@qq.com")
    
    if not sender_email or not auth_code:
        logger.warning("Email configuration not found, skipping email sending")
        return False
    
    sender = EmailSender()
    return sender.send_report(sender_email, auth_code, receiver_email, report_path)
