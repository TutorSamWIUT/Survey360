"""Utility functions for the survey application."""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.urls import reverse
from datetime import datetime, timedelta
import secrets
import string


def generate_secure_token(length=64):
    """Generate a cryptographically secure random token."""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))


def send_survey_invitation(invitation, request=None):
    """Send survey invitation email to participant."""
    survey = invitation.survey
    
    # Build the survey URL
    if request:
        survey_url = request.build_absolute_uri(
            reverse('participant_survey', kwargs={'token': invitation.token})
        )
    else:
        survey_url = f"{settings.DEFAULT_DOMAIN}/survey/{invitation.token}/"
    
    # Prepare email context
    context = {
        'leader_name': survey.leader_name,
        'survey_url': survey_url,
        'expires_at': invitation.expires_at,
        'email': invitation.email,
    }
    
    # Render email templates
    html_message = render_to_string('emails/invitation.html', context)
    plain_message = strip_tags(html_message)
    
    # Send email
    try:
        send_mail(
            subject=f'Leadership Assessment Survey for {survey.leader_name}',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invitation.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error sending email to {invitation.email}: {e}")
        return False


def send_leader_self_assessment_email(survey, request=None):
    """Send self-assessment invitation to the leader."""
    from django.urls import reverse
    from django.core.mail import EmailMessage
    from django.template.loader import render_to_string
    from django.utils.html import strip_tags
    from django.conf import settings
    
    # Build the self-assessment URL
    if request:
        self_assessment_url = request.build_absolute_uri(
            reverse('leader_self_assessment', kwargs={'token': survey.leader_token})
        )
    else:
        self_assessment_url = f"{getattr(settings, 'DEFAULT_DOMAIN', 'http://localhost:8000')}/survey/leader/{survey.leader_token}/"
    
    # Prepare email context
    context = {
        'leader_name': survey.leader_name,
        'survey_title': survey.title,
        'self_assessment_url': self_assessment_url,
        'created_by': survey.created_by.get_full_name() or survey.created_by.username,
    }
    
    # Render email template
    html_message = render_to_string('emails/leader_self_assessment.html', context)
    plain_message = strip_tags(html_message)
    
    try:
        email = EmailMessage(
            subject=f'Complete Your Leadership Self-Assessment - {survey.title}',
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[survey.leader_email],
        )
        email.content_subtype = 'html'
        email.body = html_message
        email.send(fail_silently=False)
        return True
    except Exception as e:
        print(f"Error sending self-assessment email to {survey.leader_email}: {e}")
        return False


def send_report_to_leader(report, request=None):
    """Send report link to leader."""
    survey = report.survey
    
    # Build the report URL
    if request:
        report_url = request.build_absolute_uri(
            reverse('view_report', kwargs={'report_token': report.report_token})
        )
    else:
        report_url = f"{getattr(settings, 'DEFAULT_DOMAIN', 'http://localhost:8000')}/report/{report.report_token}/"
    
    # Prepare email context
    context = {
        'leader_name': survey.leader_name,
        'report_url': report_url,
        'survey_title': survey.title,
    }
    
    # Render email templates
    html_message = render_to_string('emails/report_ready.html', context)
    plain_message = strip_tags(html_message)
    
    # Send email
    try:
        send_mail(
            subject=f'Your Leadership Assessment Report is Ready',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[survey.leader_email],
            html_message=html_message,
            fail_silently=False,
        )
        report.mark_as_sent()
        return True
    except Exception as e:
        print(f"Error sending report to {survey.leader_email}: {e}")
        return False


def calculate_likert_score(value):
    """Convert Likert scale response to numeric score."""
    scores = {
        'significantly_above': 7,
        'above': 6,
        'slightly_above': 5,
        'meets': 4,
        'slightly_below': 3,
        'below': 2,
        'significantly_below': 1,
    }
    return scores.get(value, 4)


def get_question_texts():
    """Return dictionary of question numbers and their text."""
    return {
        2: "This leader communicates a clear vision for the school's future.",
        3: "This leader allocates resources (financial, human, and/or time) to support the school's vision.",
        4: "This leader integrates the school's core values into the daily operations of the campus.",
        5: "This leader ensures diverse stakeholders are respected and represented within the school environment.",
        6: "This leader supports the recruitment of a diverse staff that mirrors the student population.",
        7: "This leader models the school's core values in all aspects of leadership.",
        8: "This leader fosters open communication among others.",
        9: "This leader cultivates an inclusive school culture where everyone feels valued.",
        10: "This leader implements and evaluates a comprehensive safety and security plan.",
        11: "This leader provides training or resources to recognize and respond effectively to potential safety threats, including bullying, harassment, and violence.",
        12: "This leader promotes a sense of ownership and responsibility among others.",
        13: "This leader promotes the development of leadership in others.",
        14: "This leader is supportive of district priorities and/or initiatives.",
        15: "This leader uses research and/or best practices to improve curriculum and instruction.",
        16: "This leader ensures professional development experiences translate into improved practice.",
        17: "This leader promotes a culture of continuous learning and growth.",
        18: "This leader advocates for school resources and support.",
        19: "This leader is transparent with pertinent information.",
        20: "This leader models ethical behavior.",
        21: "This leader places students at the center of educational decisions.",
        22: "This leader seeks to understand others.",
        23: "This leader proactively communicates information.",
        24: "This leader is positive in their demeanor.",
        25: "This leader builds positive relationships with all members of the school community.",
        26: "This leader effectively resolves conflicts in a manner that promotes mutual understanding.",
        27: "This leader builds consensus to achieve common goals.",
        28: "This leader navigates challenging situations while maintaining positive relationships.",
        29: "This leader advocates for students' needs and rights, even in the face of resistance.",
        30: "This leader takes personal responsibility to advance student success.",
        31: "This leader seeks ways to include families and community members in the school community.",
        32: "This leader collaborates with local organizations to address the broader needs of students and families.",
        33: "This leader ensures school policies, practices, and programs are inclusive and equitable for everyone.",
        34: "This leader fosters a culture of inclusivity and diversity within the school community.",
        35: "This leader communicates instructional goals to staff, students, and parents.",
        36: "This leader ensures alignment between curriculum, instruction, and assessment within the school.",
        37: "This leader promotes a culture of differentiated instruction to meet the diverse needs of students.",
        38: "This leader provides opportunities for teachers to enhance their understanding and implementation of the curriculum.",
        39: "This leader monitors curriculum implementation and student outcomes to ensure continuous improvement.",
        40: "This leader views feedback as an opportunity for improvement.",
        41: "This leader helps teachers improve instruction.",
        42: "This leader uses feedback mechanisms (surveys, focus groups, etc.) to improve.",
        43: "This leader collaborates with others to identify priority areas for school improvement.",
        44: "This leader communicates updates and successes regarding school improvement efforts.",
        45: "This leader works with others to establish and accomplish school goals.",
        46: "This leader supports using a variety of assessment methods to measure student progress and learning.",
        47: "This leader uses assessment data to improve student achievement.",
        48: "This leader fosters a culture of collaboration among teachers to share teaching strategies and best practices.",
        49: "This leader fosters a work environment that values the contributions of all staff members.",
        50: "This leader seeks out and secures additional funding to enhance programs and services.",
        51: "This leader provides effective resources to support campus instructional needs.",
        52: "This leader aligns the school budget with campus goals.",
        53: "This leader supports the integration of technology into teaching and learning practices.",
        54: "This leader inspires and empowers others to pursue lifelong learning.",
        55: "This leader supports ongoing learning and professional growth opportunities.",
    }


def get_strength_choices():
    """Return list of strength choices for ranking."""
    return [
        "Ability to guide others towards a common goal",
        "Possesses excellent oral communication skills",
        "Possesses effective written communication skills",
        "Great listener",
        "Expresses ideas clearly",
        "Supports teacher professional development",
        "Supports teachers in implementing effective instructional strategies",
        "Ability to build positive relationships with others",
        "Supports collaboration among all school stakeholders",
        "Ability to analyze challenges and implement solutions",
        "Creates a positive school culture",
        "Promotes and encourages innovation",
        "Supports and encourages continuous improvement",
        "Makes timely decisions aligned with school mission and goals",
        "Decisions encompass the needs of all stakeholders",
        "Uses data to inform major decisions",
        "Effectively manages emotions",
        "Resilient in effectively navigating change",
        "Able to navigate challenges and obstacles",
        "Has a clear vision for the school",
        "Able to motivate others to work towards shared goals",
        "Maintains a high level of integrity",
        "Create a positive school environment",
        "Committed to learning and growing professionally",
        "Is up to date on the latest research and best practices",
    ]


def get_opportunity_choices():
    """Return list of opportunity choices for ranking."""
    return [
        "Lacks a clear vision for the school",
        "Struggles to verbally communicate ideas",
        "Struggles to communicate in written formats",
        "Leadership contributes to low morale",
        "Resistant to change",
        "Struggles to foster collaboration",
        "Leadership promotes a lack of trust among others",
        "Struggles to address issues effectively",
        "Micromanages others",
        "Inhibits autonomy and creativity",
        "Provide more sufficient PD opportunities for all staff",
        "Struggles to create a positive school culture",
        "Improve skills to effectively engage parents or community",
        "Needs to improve listening skills",
        "Difficulty expressing ideas",
        "Should delegate more effectively (distribution of tasks)",
        "Could improve their feedback processes",
        "Could improve their problem solving skills",
        "Seems to not follow through",
        "Could improve their appreciation for diverse perspectives",
        "Could recognize others more often",
    ]


def calculate_default_expiration():
    """Calculate default expiration date (14 days from now)."""
    return datetime.now() + timedelta(days=14)