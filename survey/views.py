"""Views for the survey application."""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count, Avg, Q
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json

from .models import Survey, SurveyInvitation, SurveyResponse, StrengthRanking, OpportunityRanking, SurveyReport
from .forms import AdminLoginForm, CreateSurveyForm, InvitationForm, SurveyResponseForm, LeaderSelfAssessmentForm
from .utils import (
    send_survey_invitation, send_report_to_leader, send_leader_self_assessment_email,
    calculate_likert_score, get_question_texts, get_strength_choices, get_opportunity_choices
)


# Admin Views
def admin_login_view(request):
    """Custom admin login view."""
    if request.user.is_authenticated:
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        form = AdminLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_staff:
                login(request, user)
                messages.success(request, f'Welcome back, {user.first_name or username}!')
                return redirect('admin_dashboard')
            else:
                messages.error(request, 'Invalid credentials or insufficient permissions.')
    else:
        form = AdminLoginForm()
    
    return render(request, 'admin/login.html', {'form': form})


@login_required
def admin_dashboard_view(request):
    """Admin dashboard view."""
    if not request.user.is_staff:
        return HttpResponseForbidden()
    
    # Get statistics
    total_surveys = Survey.objects.count()
    active_surveys = Survey.objects.filter(is_active=True).count()
    completed_surveys = Survey.objects.filter(leader_completed_self=True).count()
    
    # Get recent surveys
    recent_surveys = Survey.objects.all()[:5]
    
    # Get surveys needing attention
    pending_self_assessment = Survey.objects.filter(leader_completed_self=False)[:5]
    
    context = {
        'total_surveys': total_surveys,
        'active_surveys': active_surveys,
        'completed_surveys': completed_surveys,
        'recent_surveys': recent_surveys,
        'pending_self_assessment': pending_self_assessment,
    }
    
    return render(request, 'admin/dashboard.html', context)


@login_required
def survey_list_view(request):
    """List all surveys."""
    if not request.user.is_staff:
        return HttpResponseForbidden()
    
    surveys = Survey.objects.all().prefetch_related('responses', 'invitations')
    
    # Apply filters
    status_filter = request.GET.get('status')
    if status_filter == 'active':
        surveys = surveys.filter(is_active=True)
    elif status_filter == 'completed':
        surveys = surveys.filter(leader_completed_self=True)
    elif status_filter == 'pending':
        surveys = surveys.filter(leader_completed_self=False)
    
    context = {
        'surveys': surveys,
        'status_filter': status_filter,
    }
    
    return render(request, 'admin/survey_list.html', context)


@login_required
def create_survey_view(request):
    """Create a new survey."""
    if not request.user.is_staff:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = CreateSurveyForm(request.POST)
        if form.is_valid():
            survey = form.save(commit=False)
            survey.created_by = request.user
            survey.save()
            
            # Send leader self-assessment email automatically
            if send_leader_self_assessment_email(survey, request):
                messages.success(request, f'Survey created for {survey.leader_name}. Self-assessment email sent to {survey.leader_email}.')
            else:
                messages.warning(request, f'Survey created for {survey.leader_name}, but failed to send self-assessment email. You can resend it manually.')
            
            return redirect('survey_detail', survey_id=survey.id)
    else:
        form = CreateSurveyForm()
    
    return render(request, 'admin/create_survey.html', {'form': form})


@login_required
def survey_detail_view(request, survey_id):
    """View survey details."""
    if not request.user.is_staff:
        return HttpResponseForbidden()
    
    survey = get_object_or_404(Survey, id=survey_id)
    
    # Get all responses
    responses = survey.responses.all()
    invitations = survey.invitations.all()
    
    # Calculate statistics
    stats = {
        'total_invitations': invitations.count(),
        'completed_invitations': invitations.filter(used=True).count(),
        'pending_invitations': invitations.filter(used=False, expires_at__gt=timezone.now()).count(),
        'expired_invitations': invitations.filter(used=False, expires_at__lte=timezone.now()).count(),
        'total_responses': responses.count(),
        'self_assessment_complete': survey.leader_completed_self,
    }
    
    # Check if report exists
    try:
        report = survey.report
    except SurveyReport.DoesNotExist:
        report = None
    
    context = {
        'survey': survey,
        'responses': responses,
        'invitations': invitations,
        'stats': stats,
        'report': report,
        'invitation_form': InvitationForm() if survey.leader_completed_self else None,
    }
    
    return render(request, 'admin/survey_detail.html', context)


@login_required
def admin_logout_view(request):
    """Logout admin user."""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('admin_login')


# Survey Views
def leader_self_assessment_view(request, token):
    """Leader self-assessment view."""
    survey = get_object_or_404(Survey, leader_token=token)
    
    if survey.leader_completed_self:
        messages.info(request, 'You have already completed your self-assessment.')
        return redirect('leader_dashboard', token=token)
    
    if request.method == 'POST':
        form = LeaderSelfAssessmentForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.survey = survey
            response.relationship = 'self'
            response.is_leader_self_assessment = True
            response.save()
            
            # Save rankings
            strengths = form.cleaned_data['strengths']
            opportunities = form.cleaned_data['opportunities']
            
            # Process strength rankings from POST data
            for i, strength_id in enumerate(strengths):
                rank = request.POST.get(f'strength_rank_{strength_id}', 5-i)
                strength_text = get_strength_choices()[int(strength_id)]
                StrengthRanking.objects.create(
                    response=response,
                    strength=strength_text,
                    rank=int(rank)
                )
            
            # Process opportunity rankings from POST data
            for i, opp_id in enumerate(opportunities):
                rank = request.POST.get(f'opportunity_rank_{opp_id}', 5-i)
                opp_text = get_opportunity_choices()[int(opp_id)]
                OpportunityRanking.objects.create(
                    response=response,
                    opportunity=opp_text,
                    rank=int(rank)
                )
            
            # Mark survey as self-assessment complete
            survey.leader_completed_self = True
            survey.save()
            
            messages.success(request, 'Self-assessment completed successfully!')
            return redirect('leader_dashboard', token=token)
    else:
        form = LeaderSelfAssessmentForm()
    
    context = {
        'survey': survey,
        'form': form,
        'is_self_assessment': True,
    }
    
    # Always use original template (remove test templates)
    template_name = 'survey/leader_self_assessment_full.html'
    return render(request, template_name, context)


def leader_dashboard_view(request, token):
    """Leader dashboard after completing self-assessment."""
    survey = get_object_or_404(Survey, leader_token=token)
    
    if not survey.leader_completed_self:
        return redirect('leader_self_assessment', token=token)
    
    if request.method == 'POST':
        form = InvitationForm(request.POST)
        if form.is_valid():
            emails = form.cleaned_data['emails']
            expires_at = form.cleaned_data['expires_at']
            
            created_count = 0
            failed_emails = []
            
            for email in emails:
                # Check if invitation already exists
                if not SurveyInvitation.objects.filter(survey=survey, email=email).exists():
                    invitation = SurveyInvitation.objects.create(
                        survey=survey,
                        email=email,
                        expires_at=expires_at
                    )
                    # Send invitation email
                    try:
                        if send_survey_invitation(invitation, request):
                            created_count += 1
                            print(f"✅ Email sent successfully to: {email}")
                        else:
                            failed_emails.append(email)
                            print(f"❌ Failed to send email to: {email}")
                    except Exception as e:
                        failed_emails.append(email)
                        print(f"❌ Exception sending email to {email}: {e}")
                else:
                    print(f"⚠️ Invitation already exists for: {email}")
            
            if created_count > 0:
                messages.success(request, f'Successfully sent {created_count} invitations.')
            if failed_emails:
                messages.warning(request, f'Failed to send emails to: {", ".join(failed_emails)}')
            
            return redirect('leader_dashboard', token=token)
    else:
        form = InvitationForm()
    
    invitations = survey.invitations.all()
    
    context = {
        'survey': survey,
        'form': form,
        'invitations': invitations,
    }
    
    return render(request, 'survey/leader_dashboard.html', context)


def participant_survey_view(request, token):
    """Participant survey view."""
    try:
        invitation = SurveyInvitation.objects.get(token=token)
    except SurveyInvitation.DoesNotExist:
        # Invalid token - show invalid link page
        context = {
            'invitation': None,
            'admin_email': settings.DEFAULT_FROM_EMAIL.split('<')[-1].rstrip('>') if '<' in settings.DEFAULT_FROM_EMAIL else settings.DEFAULT_FROM_EMAIL
        }
        return render(request, 'survey/invalid_link.html', context)
    
    # Check if invitation is valid
    if invitation.used or invitation.is_expired:
        context = {
            'invitation': invitation,
            'admin_email': settings.DEFAULT_FROM_EMAIL.split('<')[-1].rstrip('>') if '<' in settings.DEFAULT_FROM_EMAIL else settings.DEFAULT_FROM_EMAIL
        }
        return render(request, 'survey/invalid_link.html', context)
    
    survey = invitation.survey
    
    if request.method == 'POST':
        form = SurveyResponseForm(request.POST)
        if form.is_valid():
            response = form.save(commit=False)
            response.survey = survey
            response.invitation = invitation
            response.save()
            
            # Save rankings
            strengths = form.cleaned_data['strengths']
            opportunities = form.cleaned_data['opportunities']
            
            # Process strength rankings
            for i, strength_id in enumerate(strengths):
                rank = request.POST.get(f'strength_rank_{strength_id}', 5-i)
                strength_text = get_strength_choices()[int(strength_id)]
                StrengthRanking.objects.create(
                    response=response,
                    strength=strength_text,
                    rank=int(rank)
                )
            
            # Process opportunity rankings
            for i, opp_id in enumerate(opportunities):
                rank = request.POST.get(f'opportunity_rank_{opp_id}', 5-i)
                opp_text = get_opportunity_choices()[int(opp_id)]
                OpportunityRanking.objects.create(
                    response=response,
                    opportunity=opp_text,
                    rank=int(rank)
                )
            
            # Mark invitation as used
            invitation.used = True
            invitation.used_at = timezone.now()
            invitation.save()
            
            messages.success(request, 'Thank you for completing the survey!')
            # Use redirect to prevent form resubmission
            return redirect('thank_you')
    else:
        form = SurveyResponseForm()
    
    context = {
        'survey': survey,
        'invitation': invitation,
        'form': form,
        'is_self_assessment': False,
    }
    
    # Always use original template (remove test templates)
    template_name = 'survey/participant_survey.html'
    return render(request, template_name, context)


def thank_you_view(request):
    """Thank you page after survey submission."""
    return render(request, 'survey/thank_you.html')


def submit_survey_view(request, token):
    """Handle survey submission (redirect endpoint)."""
    if 'invitation' in request.path:
        return participant_survey_view(request, token)
    else:
        return leader_self_assessment_view(request, token)


# Report Views
@login_required
def generate_report_view(request, survey_id):
    """Generate report for a survey."""
    if not request.user.is_staff:
        return HttpResponseForbidden()
    
    survey = get_object_or_404(Survey, id=survey_id)
    
    # Check if report already exists
    report, created = SurveyReport.objects.get_or_create(
        survey=survey,
        defaults={'generated_by': request.user}
    )
    
    if not created:
        report.generated_at = timezone.now()
        report.generated_by = request.user
        report.save()
    
    messages.success(request, 'Report generated successfully!')
    return redirect('view_report', report_token=report.report_token)


def view_report(request, report_token):
    """View survey report."""
    report = get_object_or_404(SurveyReport, report_token=report_token)
    survey = report.survey
    
    # Get all responses
    responses = survey.responses.all()
    
    # Calculate statistics for each question
    question_stats = {}
    question_texts = get_question_texts()
    
    for q_num in range(2, 56):
        field_name = f'q{q_num}_response'
        scores = []
        scores_by_relationship = {
            'self': [],
            'supervisor': [],
            'peer': [],
            'teacher': [],
            'student': [],
            'parent': []
        }
        
        for response in responses:
            value = getattr(response, field_name)
            if value:  # Only include non-empty responses
                score = calculate_likert_score(value)
                scores.append(score)
                
                # Group by relationship type
                relationship = 'self' if response.is_leader_self_assessment else response.relationship
                if relationship in scores_by_relationship:
                    scores_by_relationship[relationship].append(score)
        
        if scores:
            # Calculate averages by relationship
            avg_by_relationship = {}
            for rel, rel_scores in scores_by_relationship.items():
                avg_by_relationship[rel] = round(sum(rel_scores) / len(rel_scores), 2) if rel_scores else None
            
            question_stats[q_num] = {
                'text': question_texts[q_num],
                'average': round(sum(scores) / len(scores), 2),
                'scores': scores,
                'response_count': len(scores),
                'by_relationship': avg_by_relationship,
            }
    
    # Get top strengths and opportunities
    all_strengths = {}
    all_opportunities = {}
    
    for response in responses:
        for strength in response.strength_rankings.all():
            if strength.strength not in all_strengths:
                all_strengths[strength.strength] = []
            all_strengths[strength.strength].append(strength.rank)
        
        for opportunity in response.opportunity_rankings.all():
            if opportunity.opportunity not in all_opportunities:
                all_opportunities[opportunity.opportunity] = []
            all_opportunities[opportunity.opportunity].append(opportunity.rank)
    
    # Calculate average rankings
    top_strengths = []
    for strength, ranks in all_strengths.items():
        avg_rank = sum(ranks) / len(ranks)
        top_strengths.append((strength, avg_rank, len(ranks)))
    top_strengths.sort(key=lambda x: x[1], reverse=True)
    
    top_opportunities = []
    for opportunity, ranks in all_opportunities.items():
        avg_rank = sum(ranks) / len(ranks)
        top_opportunities.append((opportunity, avg_rank, len(ranks)))
    top_opportunities.sort(key=lambda x: x[1], reverse=True)
    
    # Get open-ended responses
    continue_responses = [r.continue_doing for r in responses if r.continue_doing]
    stop_responses = [r.stop_doing for r in responses if r.stop_doing]
    start_responses = [r.start_doing for r in responses if r.start_doing]
    
    # Calculate overall statistics
    total_responses = responses.count()
    participant_responses = responses.exclude(is_leader_self_assessment=True).count()
    
    # Calculate participant counts by relationship type
    supervisors_count = responses.filter(relationship='supervisor').count()
    peers_count = responses.filter(relationship='peer').count()
    staff_count = responses.filter(relationship='teacher').count()
    students_count = responses.filter(relationship='student').count()
    community_count = responses.filter(relationship='parent').count()
    
    # Calculate overall average score
    all_scores = []
    for stats in question_stats.values():
        all_scores.extend(stats['scores'])
    overall_average = round(sum(all_scores) / len(all_scores), 2) if all_scores else 0
    
    context = {
        'report': report,
        'survey': survey,
        'response_count': total_responses,
        'participant_count': participant_responses,
        'overall_average': overall_average,
        'question_stats': question_stats,
        'top_strengths': top_strengths[:10],
        'top_opportunities': top_opportunities[:10],
        'continue_responses': continue_responses,
        'stop_responses': stop_responses,
        'start_responses': start_responses,
        'supervisors_count': supervisors_count,
        'peers_count': peers_count,
        'staff_count': staff_count,
        'students_count': students_count,
        'community_count': community_count,
    }
    
    return render(request, 'reports/web_report.html', context)


@login_required
def send_report_view(request, survey_id):
    """Send report to leader."""
    if not request.user.is_staff:
        return HttpResponseForbidden()
    
    survey = get_object_or_404(Survey, id=survey_id)
    
    try:
        report = survey.report
        if send_report_to_leader(report, request):
            messages.success(request, f'Report sent to {survey.leader_email}')
        else:
            messages.error(request, 'Failed to send report email.')
    except SurveyReport.DoesNotExist:
        messages.error(request, 'Report not generated yet.')
    
    return redirect('survey_detail', survey_id=survey_id)


# API Endpoints
@csrf_exempt
@require_http_methods(["POST"])
def api_submit_survey(request, token):
    """API endpoint for survey submission."""
    try:
        data = json.loads(request.body)
        
        # Determine if it's a leader or participant survey
        if 'invitation_token' in data:
            invitation = get_object_or_404(SurveyInvitation, token=data['invitation_token'])
            survey = invitation.survey
            
            if invitation.used:
                return JsonResponse({'error': 'Survey already completed'}, status=400)
            if invitation.is_expired:
                return JsonResponse({'error': 'Survey link expired'}, status=400)
        else:
            survey = get_object_or_404(Survey, leader_token=token)
            invitation = None
            
            if survey.leader_completed_self:
                return JsonResponse({'error': 'Self-assessment already completed'}, status=400)
        
        # Create response
        response = SurveyResponse.objects.create(
            survey=survey,
            invitation=invitation,
            relationship=data.get('relationship'),
            is_leader_self_assessment=(invitation is None),
            **{f'q{i}_response': data.get(f'q{i}') for i in range(2, 56)},
            continue_doing=data.get('continue_doing', ''),
            stop_doing=data.get('stop_doing', ''),
            start_doing=data.get('start_doing', '')
        )
        
        # Save rankings
        for strength_data in data.get('strengths', []):
            StrengthRanking.objects.create(
                response=response,
                strength=strength_data['text'],
                rank=strength_data['rank']
            )
        
        for opp_data in data.get('opportunities', []):
            OpportunityRanking.objects.create(
                response=response,
                opportunity=opp_data['text'],
                rank=opp_data['rank']
            )
        
        # Update invitation/survey status
        if invitation:
            invitation.used = True
            invitation.used_at = timezone.now()
            invitation.save()
        else:
            survey.leader_completed_self = True
            survey.save()
        
        return JsonResponse({'success': True, 'message': 'Survey submitted successfully'})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def api_generate_report(request, survey_id):
    """API endpoint to generate report."""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    survey = get_object_or_404(Survey, id=survey_id)
    
    report, created = SurveyReport.objects.get_or_create(
        survey=survey,
        defaults={'generated_by': request.user}
    )
    
    if not created:
        report.generated_at = timezone.now()
        report.generated_by = request.user
        report.save()
    
    report_url = request.build_absolute_uri(
        reverse('view_report', kwargs={'report_token': report.report_token})
    )
    
    return JsonResponse({
        'success': True,
        'report_url': report_url,
        'report_token': report.report_token
    })