"""
Management command to test email configuration.
Usage: python manage.py test_email recipient@example.com
"""

from django.core.management.base import BaseCommand
from django.core.mail import send_mail, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import sys


class Command(BaseCommand):
    help = 'Test email configuration by sending a test email'

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            type=str,
            help='Email address to send test email to'
        )
        parser.add_argument(
            '--html',
            action='store_true',
            help='Send HTML formatted email'
        )

    def handle(self, *args, **options):
        recipient_email = options['email']
        use_html = options.get('html', False)
        
        self.stdout.write(self.style.WARNING('=' * 60))
        self.stdout.write(self.style.WARNING('EMAIL CONFIGURATION TEST'))
        self.stdout.write(self.style.WARNING('=' * 60))
        
        # Display current email configuration
        self.stdout.write('\nCurrent Email Configuration:')
        self.stdout.write(f'  EMAIL_BACKEND: {settings.EMAIL_BACKEND}')
        self.stdout.write(f'  EMAIL_HOST: {settings.EMAIL_HOST}')
        self.stdout.write(f'  EMAIL_PORT: {settings.EMAIL_PORT}')
        self.stdout.write(f'  EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}')
        self.stdout.write(f'  EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}')
        self.stdout.write(f'  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}')
        
        # Check if using console backend
        if 'console' in settings.EMAIL_BACKEND.lower():
            self.stdout.write(self.style.WARNING(
                '\n⚠️  WARNING: Using Console Email Backend - '
                'Emails will be printed below, not actually sent!'
            ))
        
        self.stdout.write(f'\nSending test email to: {recipient_email}')
        self.stdout.write('-' * 40)
        
        try:
            if use_html:
                # HTML email test
                subject = 'Principal360 - HTML Email Test'
                html_content = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body {{
                            font-family: Arial, sans-serif;
                            max-width: 600px;
                            margin: 0 auto;
                            padding: 20px;
                        }}
                        .header {{
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                            color: white;
                            padding: 30px;
                            border-radius: 10px;
                            text-align: center;
                        }}
                        .content {{
                            background: #f8f9fa;
                            padding: 30px;
                            border-radius: 10px;
                            margin-top: 20px;
                        }}
                        .success {{
                            color: #28a745;
                            font-weight: bold;
                        }}
                        .config {{
                            background: white;
                            padding: 15px;
                            border-radius: 5px;
                            margin: 20px 0;
                        }}
                        .config li {{
                            margin: 10px 0;
                        }}
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>Principal360 Email Test</h1>
                        <p>Testing HTML Email Configuration</p>
                    </div>
                    
                    <div class="content">
                        <h2 class="success">✅ Email Configuration Working!</h2>
                        
                        <p>Congratulations! Your email configuration is working correctly.</p>
                        
                        <div class="config">
                            <h3>Current Configuration:</h3>
                            <ul>
                                <li><strong>Email Host:</strong> {settings.EMAIL_HOST}</li>
                                <li><strong>Email Port:</strong> {settings.EMAIL_PORT}</li>
                                <li><strong>From Email:</strong> {settings.DEFAULT_FROM_EMAIL}</li>
                                <li><strong>TLS Enabled:</strong> {settings.EMAIL_USE_TLS}</li>
                            </ul>
                        </div>
                        
                        <p>You can now send survey invitations to participants!</p>
                        
                        <p><strong>Next Steps:</strong></p>
                        <ol>
                            <li>Login to the admin panel</li>
                            <li>Create a survey for a leader</li>
                            <li>Send invitations to participants</li>
                            <li>Monitor responses and generate reports</li>
                        </ol>
                    </div>
                </body>
                </html>
                """
                
                plain_message = strip_tags(html_content)
                
                email = EmailMessage(
                    subject=subject,
                    body=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[recipient_email],
                )
                email.content_subtype = 'html'
                email.body = html_content
                email.send(fail_silently=False)
                
            else:
                # Plain text email test
                subject = 'Principal360 - Email Configuration Test'
                message = f'''
Hello!

This is a test email from the Principal360 Survey System.

If you're receiving this email, your email configuration is working correctly!

Current Configuration:
- Email Host: {settings.EMAIL_HOST}
- Email Port: {settings.EMAIL_PORT}
- From Email: {settings.DEFAULT_FROM_EMAIL}
- TLS Enabled: {settings.EMAIL_USE_TLS}

You can now send survey invitations to participants.

Best regards,
Principal360 Survey System
                '''
                
                send_mail(
                    subject=subject,
                    message=message.strip(),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[recipient_email],
                    fail_silently=False,
                )
            
            self.stdout.write(self.style.SUCCESS(
                f'\n✅ SUCCESS! Test email sent to {recipient_email}'
            ))
            
            if 'console' in settings.EMAIL_BACKEND.lower():
                self.stdout.write(self.style.WARNING(
                    '\n📧 Email content printed above (Console Backend)'
                ))
            else:
                self.stdout.write(self.style.SUCCESS(
                    f'\n📧 Check {recipient_email} inbox for the test email'
                ))
            
            self.stdout.write(self.style.SUCCESS(
                '\n✨ Your email configuration is working! You can now send survey invitations.'
            ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'\n❌ ERROR: Failed to send email'
            ))
            self.stdout.write(self.style.ERROR(f'Error details: {str(e)}'))
            
            # Provide troubleshooting tips
            self.stdout.write(self.style.WARNING('\n' + '=' * 60))
            self.stdout.write(self.style.WARNING('TROUBLESHOOTING TIPS:'))
            self.stdout.write(self.style.WARNING('=' * 60))
            
            if 'gmail' in settings.EMAIL_HOST.lower():
                self.stdout.write('''
For Gmail:
1. Enable 2-Factor Authentication
2. Generate an App Password: https://myaccount.google.com/apppasswords
3. Use the App Password (16 characters) in EMAIL_HOST_PASSWORD
4. Make sure "Less secure app access" is not the issue
                ''')
            elif 'sendgrid' in settings.EMAIL_HOST.lower():
                self.stdout.write('''
For SendGrid:
1. Verify your SendGrid API key is correct
2. Make sure EMAIL_HOST_USER is set to 'apikey' (literal string)
3. Verify sender domain/email is authenticated in SendGrid
                ''')
            elif 'office365' in settings.EMAIL_HOST.lower() or 'outlook' in settings.EMAIL_HOST.lower():
                self.stdout.write('''
For Microsoft 365/Outlook:
1. Verify your password is correct
2. Check if your organization requires app-specific passwords
3. Ensure SMTP is enabled for your account
                ''')
            
            self.stdout.write('''
General Tips:
1. Check your .env file has correct values
2. Verify firewall/network allows outbound connections on port 587
3. Try using EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend for testing
4. Check Django logs for more detailed error messages
            ''')
            
            sys.exit(1)