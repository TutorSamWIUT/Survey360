from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from survey.models import Survey, SurveyInvitation, SurveyResponse, StrengthRanking, OpportunityRanking, SurveyReport
from survey.utils import get_strength_choices, get_opportunity_choices
from datetime import datetime, timedelta
import random
import secrets
import string


class Command(BaseCommand):
    help = 'Generate comprehensive dummy data for Principal360 Survey System'
    
    # Sample leader data
    LEADERS = [
        ("Dr. Sarah Johnson", "sarah.johnson@springfield.edu"),
        ("Michael Chen", "michael.chen@riverside.edu"),
        ("Jennifer Martinez", "jennifer.martinez@oakwood.edu"),
        ("Robert Williams", "robert.williams@hillside.edu"),
        ("Dr. Angela Davis", "angela.davis@meadowbrook.edu"),
        ("David Thompson", "david.thompson@clearwater.edu"),
        ("Maria Rodriguez", "maria.rodriguez@sunnydale.edu"),
        ("James Wilson", "james.wilson@greenfield.edu"),
        ("Dr. Lisa Anderson", "lisa.anderson@westview.edu"),
        ("Kevin Brown", "kevin.brown@eastside.edu"),
        ("Amanda Taylor", "amanda.taylor@northgate.edu"),
        ("Christopher Lee", "christopher.lee@southpark.edu"),
        ("Dr. Patricia White", "patricia.white@central.edu"),
        ("Daniel Garcia", "daniel.garcia@lakeside.edu"),
        ("Michelle Thomas", "michelle.thomas@valley.edu"),
        ("Ryan Jackson", "ryan.jackson@highland.edu"),
        ("Dr. Rebecca Harris", "rebecca.harris@forest.edu"),
        ("Brandon Clark", "brandon.clark@mountain.edu"),
        ("Nicole Lewis", "nicole.lewis@river.edu"),
        ("Anthony Walker", "anthony.walker@summit.edu"),
        ("Dr. Stephanie Hall", "stephanie.hall@bridge.edu"),
        ("Jonathan Allen", "jonathan.allen@crossroads.edu"),
        ("Melissa Young", "melissa.young@horizon.edu"),
        ("Gregory King", "gregory.king@pinnacle.edu"),
        ("Dr. Christina Wright", "christina.wright@gateway.edu"),
        ("Matthew Lopez", "matthew.lopez@cornerstone.edu"),
        ("Rachel Green", "rachel.green@beacon.edu"),
        ("Steven Adams", "steven.adams@lighthouse.edu"),
        ("Dr. Kimberly Baker", "kimberly.baker@anchor.edu"),
        ("Timothy Gonzalez", "timothy.gonzalez@compass.edu"),
    ]
    
    # Sample participant email domains
    EMAIL_DOMAINS = [
        "@school.edu", "@district.edu", "@community.org", "@parent.net", "@student.edu"
    ]
    
    # Sample first names
    FIRST_NAMES = [
        "Alex", "Jordan", "Casey", "Taylor", "Morgan", "Riley", "Avery", "Cameron",
        "Quinn", "Blake", "Drew", "Sage", "Rowan", "Finley", "Emery", "Hayden",
        "Parker", "River", "Skyler", "Dakota", "Peyton", "Reagan", "Kendall", "Aubrey",
        "Devon", "Reese", "Jamie", "Logan", "Bailey", "Sydney", "Ashton", "Charlie"
    ]
    
    LAST_NAMES = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
        "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
        "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker"
    ]
    
    # Realistic survey responses based on typical patterns
    LIKERT_WEIGHTS = {
        'significantly_above': 5,
        'above': 15,
        'slightly_above': 25,
        'meets': 35,
        'slightly_below': 15,
        'below': 4,
        'significantly_below': 1,
    }
    
    RELATIONSHIP_WEIGHTS = {
        'supervisor': 5,
        'peer': 40,
        'teacher': 30,
        'student': 15,
        'parent': 10,
    }
    
    # Sample open-ended responses
    CONTINUE_RESPONSES = [
        "Strong communication with all stakeholders",
        "Always available to support teachers and staff",
        "Maintains high expectations for student achievement",
        "Great at building relationships with families",
        "Excellent at problem-solving and conflict resolution",
        "Provides clear vision and direction for the school",
        "Supportive of teacher professional development",
        "Demonstrates integrity in all decisions",
        "Advocates effectively for school resources",
        "Creates a positive school culture",
        "Shows genuine care for student well-being",
        "Encourages innovation and creativity",
        "Maintains transparency in decision-making",
        "Builds strong community partnerships",
        "Demonstrates cultural competency and inclusiveness"
    ]
    
    STOP_RESPONSES = [
        "Micromanaging teachers and staff",
        "Making decisions without consulting stakeholders",
        "Being resistant to new ideas and change",
        "Not following through on commitments",
        "Inconsistent communication patterns",
        "Showing favoritism toward certain staff members",
        "Avoiding difficult conversations",
        "Not providing enough feedback to staff",
        "Being overly critical without offering solutions",
        "Neglecting self-care and work-life balance"
    ]
    
    START_RESPONSES = [
        "Regular classroom visits and instructional feedback",
        "More frequent staff recognition and appreciation",
        "Better delegation of responsibilities to staff",
        "Implementing more collaborative decision-making processes",
        "Providing more professional development opportunities",
        "Improving data analysis and use for school improvement",
        "Enhancing parent and community engagement",
        "Developing stronger systems for student support",
        "Creating more opportunities for teacher leadership",
        "Improving technology integration and support",
        "Building stronger partnerships with local organizations",
        "Implementing more effective communication systems",
        "Focusing more on equity and inclusion initiatives",
        "Providing more mentoring for new teachers",
        "Improving crisis management and emergency procedures"
    ]

    def add_arguments(self, parser):
        parser.add_argument(
            '--leaders',
            type=int,
            default=30,
            help='Number of leaders to create (default: 30)'
        )
        parser.add_argument(
            '--min-responses',
            type=int,
            default=50,
            help='Minimum responses per leader (default: 50)'
        )
        parser.add_argument(
            '--max-responses',
            type=int,
            default=100,
            help='Maximum responses per leader (default: 100)'
        )
    
    def handle(self, *args, **options):
        num_leaders = options['leaders']
        min_responses = options['min_responses']
        max_responses = options['max_responses']
        
        self.stdout.write(self.style.SUCCESS('🚀 Starting dummy data generation...'))
        self.stdout.write(f'Creating {num_leaders} leaders with {min_responses}-{max_responses} responses each')
        
        # Clear existing dummy data (keep admin user)
        self.stdout.write('Clearing existing dummy data...')
        Survey.objects.all().delete()
        
        # Get or create admin user
        admin_user = User.objects.filter(is_staff=True).first()
        if not admin_user:
            admin_user = User.objects.create_user(
                username='admin',
                email='admin@principal360.com',
                password='admin123',
                first_name='Eddie',
                last_name='Admin',
                is_staff=True,
                is_superuser=True
            )
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        
        leaders_created = 0
        total_responses = 0
        
        for i in range(min(num_leaders, len(self.LEADERS))):
            leader_name, leader_email = self.LEADERS[i]
            
            # Create survey
            survey = Survey.objects.create(
                title=f"Leadership Assessment - Q{random.randint(1,4)} 202{random.randint(3,5)}",
                created_by=admin_user,
                leader_name=leader_name,
                leader_email=leader_email,
                leader_completed_self=True,  # Mark as completed to show full workflow
                is_active=True,
                created_at=datetime.now() - timedelta(days=random.randint(1, 90))
            )
            
            # Create leader self-assessment
            self_response = self.create_survey_response(survey, None, 'self', True)
            
            # Generate random number of participants
            num_responses = random.randint(min_responses, max_responses)
            
            # Create invitations and responses
            for j in range(num_responses):
                # Generate participant email
                first_name = random.choice(self.FIRST_NAMES)
                last_name = random.choice(self.LAST_NAMES)
                domain = random.choice(self.EMAIL_DOMAINS)
                email = f"{first_name.lower()}.{last_name.lower()}{j}{domain}"
                
                # Create invitation
                invitation = SurveyInvitation.objects.create(
                    survey=survey,
                    email=email,
                    expires_at=datetime.now() + timedelta(days=random.randint(7, 30)),
                    used=True,  # Mark as used since we're creating responses
                    used_at=datetime.now() - timedelta(days=random.randint(1, 30)),
                    sent_at=datetime.now() - timedelta(days=random.randint(1, 45))
                )
                
                # Choose relationship type based on weights
                relationship = self.weighted_choice(self.RELATIONSHIP_WEIGHTS)
                
                # Create response
                response = self.create_survey_response(survey, invitation, relationship, False)
                
                total_responses += 1
            
            # Create report for surveys with enough responses
            if num_responses >= 5:
                SurveyReport.objects.create(
                    survey=survey,
                    generated_by=admin_user,
                    generated_at=datetime.now() - timedelta(days=random.randint(1, 10)),
                    sent_to_leader=random.choice([True, False])
                )
            
            leaders_created += 1
            
            if leaders_created % 5 == 0:
                self.stdout.write(f'Created {leaders_created} leaders with responses...')
        
        # Generate some surveys in different states
        self.create_partial_surveys(admin_user)
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS('🎉 Dummy data generation complete!'))
        self.stdout.write('='*60)
        self.stdout.write(f'✅ Created {leaders_created} leaders')
        self.stdout.write(f'✅ Generated {total_responses + leaders_created} total responses')
        self.stdout.write(f'✅ Created {Survey.objects.count()} surveys')
        self.stdout.write(f'✅ Generated {SurveyReport.objects.count()} reports')
        self.stdout.write('\n📊 Survey Status Breakdown:')
        
        completed_self = Survey.objects.filter(leader_completed_self=True).count()
        pending_self = Survey.objects.filter(leader_completed_self=False).count()
        with_reports = SurveyReport.objects.count()
        
        self.stdout.write(f'   • Self-assessments completed: {completed_self}')
        self.stdout.write(f'   • Pending self-assessments: {pending_self}')
        self.stdout.write(f'   • Reports generated: {with_reports}')
        
        self.stdout.write('\n🌐 Access your enhanced system at: http://localhost:8000/admin/')
        self.stdout.write('📧 Login: admin / admin123')
        self.stdout.write('='*60)

    def weighted_choice(self, choices):
        """Choose random item based on weights."""
        items = list(choices.keys())
        weights = list(choices.values())
        return random.choices(items, weights=weights, k=1)[0]

    def create_survey_response(self, survey, invitation, relationship, is_self_assessment):
        """Create a realistic survey response."""
        
        # Generate responses for questions 2-55
        responses = {}
        for i in range(2, 56):
            # Add some variation based on relationship type and question
            response_value = self.weighted_choice(self.LIKERT_WEIGHTS)
            responses[f'q{i}_response'] = response_value
        
        # Create the response
        response = SurveyResponse.objects.create(
            survey=survey,
            invitation=invitation,
            relationship=relationship,
            is_leader_self_assessment=is_self_assessment,
            submitted_at=datetime.now() - timedelta(days=random.randint(1, 30)),
            **responses,
            continue_doing=random.choice(self.CONTINUE_RESPONSES) if random.random() > 0.3 else "",
            stop_doing=random.choice(self.STOP_RESPONSES) if random.random() > 0.5 else "",
            start_doing=random.choice(self.START_RESPONSES) if random.random() > 0.4 else "",
        )
        
        # Create strength rankings
        strength_choices = get_strength_choices()
        selected_strengths = random.sample(strength_choices, 5)
        
        for i, strength in enumerate(selected_strengths):
            StrengthRanking.objects.create(
                response=response,
                strength=strength,
                rank=5-i  # 5 = highest, 1 = lowest
            )
        
        # Create opportunity rankings
        opportunity_choices = get_opportunity_choices()
        selected_opportunities = random.sample(opportunity_choices, 5)
        
        for i, opportunity in enumerate(selected_opportunities):
            OpportunityRanking.objects.create(
                response=response,
                opportunity=opportunity,
                rank=5-i  # 5 = highest priority, 1 = lowest
            )
        
        return response

    def create_partial_surveys(self, admin_user):
        """Create some surveys in different completion states."""
        
        # Create surveys with no self-assessment completed
        for i in range(3):
            survey = Survey.objects.create(
                title=f"New Leadership Assessment - {['Spring', 'Fall', 'Winter'][i]} 2024",
                created_by=admin_user,
                leader_name=f"Dr. {random.choice(['Alice', 'Bob', 'Carol'])} {random.choice(['New', 'Pending', 'Waiting'])}",
                leader_email=f"pending{i}@newschool.edu",
                leader_completed_self=False,  # Pending self-assessment
                is_active=True,
                created_at=datetime.now() - timedelta(days=random.randint(1, 7))
            )
        
        # Create surveys with self-assessment but few responses
        for i in range(2):
            survey = Survey.objects.create(
                title=f"Mid-Year Assessment - {['Elementary', 'Middle'][i]} School",
                created_by=admin_user,
                leader_name=f"Principal {random.choice(['Starting', 'Beginning'])} {random.choice(['Collection', 'Gathering'])}",
                leader_email=f"collecting{i}@activeschool.edu",
                leader_completed_self=True,
                is_active=True,
                created_at=datetime.now() - timedelta(days=random.randint(5, 15))
            )
            
            # Add self-assessment
            self.create_survey_response(survey, None, 'self', True)
            
            # Add few responses (2-4)
            for j in range(random.randint(2, 4)):
                first_name = random.choice(self.FIRST_NAMES)
                last_name = random.choice(self.LAST_NAMES)
                email = f"{first_name.lower()}.{last_name.lower()}@activeschool.edu"
                
                invitation = SurveyInvitation.objects.create(
                    survey=survey,
                    email=email,
                    expires_at=datetime.now() + timedelta(days=14),
                    used=True,
                    used_at=datetime.now() - timedelta(days=random.randint(1, 10)),
                    sent_at=datetime.now() - timedelta(days=random.randint(3, 20))
                )
                
                self.create_survey_response(survey, invitation, 'peer', False)