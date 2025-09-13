"""
Management command to test the survey invitation email template.
Usage: python manage.py test_invitation recipient@example.com "Leader Name"
"""

from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.utils import timezone
from datetime import timedelta


class Command(BaseCommand):
    help = 'Test survey invitation email template'

    def add_arguments(self, parser):
        parser.add_argument(
            'email',
            type=str,
            help='Email address to send test invitation to'
        )
        parser.add_argument(
            'leader_name',
            type=str,
            nargs='?',
            default='Dr. Sarah Johnson',
            help='Leader name for the test invitation'
        )

    def handle(self, *args, **options):
        recipient_email = options['email']
        leader_name = options['leader_name']
        
        self.stdout.write(self.style.WARNING('=' * 60))
        self.stdout.write(self.style.WARNING('SURVEY INVITATION EMAIL TEST'))
        self.stdout.write(self.style.WARNING('=' * 60))
        
        # Create test data
        expires_at = timezone.now() + timedelta(days=14)
        survey_url = f"http://localhost:8000/survey/test-token-abc123xyz/"
        
        # Prepare email context
        context = {
            'leader_name': leader_name,
            'survey_url': survey_url,
            'expires_at': expires_at,
            'email': recipient_email,
        }
        
        self.stdout.write(f'\nSending test invitation to: {recipient_email}')
        self.stdout.write(f'Leader Name: {leader_name}')
        self.stdout.write(f'Test Survey URL: {survey_url}')
        self.stdout.write('-' * 40)
        
        try:
            # Render email templates
            html_message = render_to_string('emails/invitation.html', context)
            plain_message = strip_tags(html_message)
            
            # Create and send email
            email = EmailMessage(
                subject=f'Leadership Assessment Survey for {leader_name}',
                body=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email],
            )
            email.content_subtype = 'html'
            email.body = html_message
            email.send(fail_silently=False)
            
            self.stdout.write(self.style.SUCCESS(
                f'\n✅ SUCCESS! Test invitation email sent to {recipient_email}'
            ))
            
            self.stdout.write(self.style.SUCCESS(
                f'\n📧 Check {recipient_email} inbox for the survey invitation'
            ))
            
            self.stdout.write('\n' + '=' * 60)
            self.stdout.write('Email Details:')
            self.stdout.write(f'  Subject: Leadership Assessment Survey for {leader_name}')
            self.stdout.write(f'  From: {settings.DEFAULT_FROM_EMAIL}')
            self.stdout.write(f'  To: {recipient_email}')
            self.stdout.write(f'  Template: emails/invitation.html')
            self.stdout.write('=' * 60)
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(
                f'\n❌ ERROR: Failed to send invitation email'
            ))
            self.stdout.write(self.style.ERROR(f'Error details: {str(e)}'))