from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import secrets
import string


def generate_token(length=64):
    """Generate a cryptographically secure random token."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


class Survey(models.Model):
    """Main survey model representing a leadership assessment."""
    title = models.CharField(max_length=200)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_surveys')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    leader_name = models.CharField(max_length=100)
    leader_email = models.EmailField()
    leader_completed_self = models.BooleanField(default=False)
    leader_token = models.CharField(max_length=64, unique=True, default=generate_token)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} - {self.leader_name}"
    
    def get_response_count(self):
        return self.responses.exclude(is_leader_self_assessment=True).count()
    
    def get_total_response_count(self):
        return self.responses.count()
    
    def get_completion_rate(self):
        invitations = self.invitations.count()
        if invitations == 0:
            return 0
        completed = self.invitations.filter(used=True).count()
        return (completed / invitations) * 100


class SurveyInvitation(models.Model):
    """Invitation sent to participants to complete a survey."""
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='invitations')
    email = models.EmailField()
    token = models.CharField(max_length=64, unique=True, default=generate_token)
    sent_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    reminder_sent = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-sent_at']
        unique_together = ['survey', 'email']
        
    def __str__(self):
        return f"Invitation to {self.email} for {self.survey.leader_name}"
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        return not self.used and not self.is_expired


class SurveyResponse(models.Model):
    """Individual response to a survey."""
    RELATIONSHIP_CHOICES = [
        ('supervisor', 'Supervisor/Manager'),
        ('peer', 'Peer/Colleague'),
        ('teacher', 'Teacher/Staff'),
        ('student', 'Student'),
        ('parent', 'Parent/Community Representative'),
        ('self', 'Self'),
    ]
    
    LIKERT_CHOICES = [
        ('significantly_above', 'Significantly above expectations'),
        ('above', 'Above expectations'),
        ('slightly_above', 'Slightly above expectations'),
        ('meets', 'Meets expectations'),
        ('slightly_below', 'Slightly below expectations'),
        ('below', 'Below expectations'),
        ('significantly_below', 'Significantly below expectations'),
    ]
    
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    invitation = models.ForeignKey(SurveyInvitation, on_delete=models.CASCADE, null=True, blank=True, related_name='response')
    relationship = models.CharField(max_length=50, choices=RELATIONSHIP_CHOICES)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_leader_self_assessment = models.BooleanField(default=False)
    
    # Questions 2-55 (Leadership evaluation questions)
    q2_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q3_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q4_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q5_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q6_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q7_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q8_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q9_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q10_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q11_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q12_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q13_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q14_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q15_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q16_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q17_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q18_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q19_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q20_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q21_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q22_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q23_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q24_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q25_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q26_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q27_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q28_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q29_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q30_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q31_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q32_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q33_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q34_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q35_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q36_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q37_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q38_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q39_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q40_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q41_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q42_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q43_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q44_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q45_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q46_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q47_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q48_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q49_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q50_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q51_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q52_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q53_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q54_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    q55_response = models.CharField(max_length=50, choices=LIKERT_CHOICES)
    
    # Open-ended responses (Questions 58-60)
    continue_doing = models.TextField(blank=True, verbose_name="What should this leader CONTINUE doing?")
    stop_doing = models.TextField(blank=True, verbose_name="What should this leader STOP doing?")
    start_doing = models.TextField(blank=True, verbose_name="What should this leader START doing?")
    
    class Meta:
        ordering = ['-submitted_at']
        
    def __str__(self):
        return f"Response for {self.survey.leader_name} by {self.relationship}"


class StrengthRanking(models.Model):
    """Rankings for leader strengths (Question 56)."""
    STRENGTH_CHOICES = [
        ('guide_others', 'Ability to guide others towards a common goal'),
        ('oral_communication', 'Possesses excellent oral communication skills'),
        ('written_communication', 'Possesses effective written communication skills'),
        ('listener', 'Great listener'),
        ('express_ideas', 'Expresses ideas clearly'),
        ('teacher_development', 'Supports teacher professional development'),
        ('instructional_strategies', 'Supports teachers in implementing effective instructional strategies'),
        ('build_relationships', 'Ability to build positive relationships with others'),
        ('collaboration', 'Supports collaboration among all school stakeholders'),
        ('analyze_challenges', 'Ability to analyze challenges and implement solutions'),
        ('positive_culture', 'Creates a positive school culture'),
        ('innovation', 'Promotes and encourages innovation'),
        ('continuous_improvement', 'Supports and encourages continuous improvement'),
        ('timely_decisions', 'Makes timely decisions aligned with school mission and goals'),
        ('inclusive_decisions', 'Decisions encompass the needs of all stakeholders'),
        ('data_driven', 'Uses data to inform major decisions'),
        ('manages_emotions', 'Effectively manages emotions'),
        ('resilient', 'Resilient in effectively navigating change'),
        ('navigate_challenges', 'Able to navigate challenges and obstacles'),
        ('clear_vision', 'Has a clear vision for the school'),
        ('motivate_others', 'Able to motivate others to work towards shared goals'),
        ('integrity', 'Maintains a high level of integrity'),
        ('positive_environment', 'Create a positive school environment'),
        ('committed_learning', 'Committed to learning and growing professionally'),
        ('research_practices', 'Is up to date on the latest research and best practices'),
    ]
    
    response = models.ForeignKey(SurveyResponse, on_delete=models.CASCADE, related_name='strength_rankings')
    strength = models.CharField(max_length=100, choices=STRENGTH_CHOICES)
    rank = models.IntegerField()  # 1-5, where 5 is highest
    
    class Meta:
        ordering = ['-rank']
        unique_together = ['response', 'strength']
        
    def __str__(self):
        return f"{self.strength} - Rank {self.rank}"


class OpportunityRanking(models.Model):
    """Rankings for improvement opportunities (Question 57)."""
    OPPORTUNITY_CHOICES = [
        ('lacks_vision', 'Lacks a clear vision for the school'),
        ('verbal_communication', 'Struggles to verbally communicate ideas'),
        ('written_communication', 'Struggles to communicate in written formats'),
        ('low_morale', 'Leadership contributes to low morale'),
        ('resistant_change', 'Resistant to change'),
        ('foster_collaboration', 'Struggles to foster collaboration'),
        ('lack_trust', 'Leadership promotes a lack of trust among others'),
        ('address_issues', 'Struggles to address issues effectively'),
        ('micromanages', 'Micromanages others'),
        ('inhibits_autonomy', 'Inhibits autonomy and creativity'),
        ('pd_opportunities', 'Provide more sufficient PD opportunities for all staff'),
        ('positive_culture', 'Struggles to create a positive school culture'),
        ('engage_parents', 'Improve skills to effectively engage parents or community'),
        ('listening_skills', 'Needs to improve listening skills'),
        ('expressing_ideas', 'Difficulty expressing ideas'),
        ('delegate', 'Should delegate more effectively (distribution of tasks)'),
        ('feedback_processes', 'Could improve their feedback processes'),
        ('problem_solving', 'Could improve their problem solving skills'),
        ('follow_through', 'Seems to not follow through'),
        ('diverse_perspectives', 'Could improve their appreciation for diverse perspectives'),
        ('recognize_others', 'Could recognize others more often'),
    ]
    
    response = models.ForeignKey(SurveyResponse, on_delete=models.CASCADE, related_name='opportunity_rankings')
    opportunity = models.CharField(max_length=100, choices=OPPORTUNITY_CHOICES)
    rank = models.IntegerField()  # 1-5, where 5 is highest priority
    
    class Meta:
        ordering = ['-rank']
        unique_together = ['response', 'opportunity']
        
    def __str__(self):
        return f"{self.opportunity} - Priority {self.rank}"


class SurveyReport(models.Model):
    """Generated report for a completed survey."""
    survey = models.OneToOneField(Survey, on_delete=models.CASCADE, related_name='report')
    report_token = models.CharField(max_length=64, unique=True, default=generate_token)
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    sent_to_leader = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-generated_at']
        
    def __str__(self):
        return f"Report for {self.survey.leader_name}"
    
    def mark_as_sent(self):
        """Mark the report as sent to the leader."""
        self.sent_to_leader = True
        self.sent_at = timezone.now()
        self.save()