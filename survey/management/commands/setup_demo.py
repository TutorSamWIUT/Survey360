from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from survey.models import Survey, SurveyInvitation
from datetime import datetime, timedelta


class Command(BaseCommand):
    help = 'Set up demo data for Principal360 Survey System'
    
    def handle(self, *args, **options):
        self.stdout.write('Setting up demo data...')
        
        # Create demo admin user
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_user(
                username='admin',
                email='admin@principal360.com',
                password='admin123',
                first_name='Eddie',
                last_name='Admin',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(
                self.style.SUCCESS(f'Created admin user: admin/admin123')
            )
        else:
            admin = User.objects.get(username='admin')
            self.stdout.write('Admin user already exists')
        
        # Create demo survey
        if not Survey.objects.filter(leader_name='John Smith').exists():
            survey = Survey.objects.create(
                title='Leadership Assessment - Q4 2024',
                created_by=admin,
                leader_name='John Smith',
                leader_email='john.smith@school.edu',
                is_active=True
            )
            self.stdout.write(
                self.style.SUCCESS(f'Created demo survey for John Smith')
            )
            
            # Create some demo invitations
            demo_emails = [
                'teacher1@school.edu',
                'teacher2@school.edu', 
                'supervisor@school.edu',
                'student1@school.edu',
                'parent1@school.edu'
            ]
            
            expires_at = datetime.now() + timedelta(days=14)
            
            for email in demo_emails:
                SurveyInvitation.objects.create(
                    survey=survey,
                    email=email,
                    expires_at=expires_at
                )
            
            self.stdout.write(
                self.style.SUCCESS(f'Created {len(demo_emails)} demo invitations')
            )
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write('Demo setup complete!')
        self.stdout.write('='*50)
        self.stdout.write('\nAccess the admin interface at: http://localhost:8000/admin/')
        self.stdout.write('Login credentials: admin / admin123')
        self.stdout.write('\nDemo survey created for leader: John Smith')
        self.stdout.write('Leader token will be shown in admin dashboard')
        self.stdout.write('\n' + '='*50)