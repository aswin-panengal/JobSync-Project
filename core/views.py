# core/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.forms import ResumeUploadForm # Import the form from the accounts app
from django.contrib import messages
from . import utils # Your custom logic functions (parsing, API calls)
from django.core.files.storage import default_storage # For handling file paths

def index_view(request):
    """Renders the homepage."""
    return render(request, 'index.html')

def success_view(request):
    """Renders the success page after sign up."""
    return render(request, 'successpage.html')

@login_required
def resume_upload_view(request):
    """Handles resume upload, preference saving, triggering parsing, and redirecting."""
    profile = request.user.profile
    # Prepare initial data for form rendering (GET request or invalid POST)
    initial_data = {
        'experience_level_preference': profile.experience_level_preference,
        'employment_types': profile.employment_type_preference.split(',') if profile.employment_type_preference else [],
        'interested_domain': profile.interested_domain,
    }
    original_filename = profile.original_resume_filename
    context = {'original_filename': original_filename} # Used by JS to show existing file

    if request.method == 'POST':
        form = ResumeUploadForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Save form data to profile instance first, but don't commit fully yet
            saved_profile = form.save(commit=False)

            # Save original filename if a new file was uploaded
            if 'resume' in request.FILES:
                saved_profile.original_resume_filename = request.FILES['resume'].name

            # Explicitly set preferences from cleaned data before main save
            saved_profile.experience_level_preference = form.cleaned_data.get('experience_level_preference', 'Any')
            saved_profile.employment_type_preference = ",".join(form.cleaned_data.get('employment_types', [])) or '' # Save joined list or empty string
            #saved_profile.interested_domain = form.cleaned_data.get('interested_domain', '')
            domain = form.cleaned_data.get('interested_domain')
            if domain == 'Other':
                # Get text from the 'other' field
                saved_profile.interested_domain = form.cleaned_data.get('interested_domain_other', '')
            else:
                # Get text from the dropdown
                saved_profile.interested_domain = domain
            
            # Save profile instance with new resume file association and all preferences
            saved_profile.save()

            # Process the uploaded resume file if it exists
            if saved_profile.resume:
                resume_path = default_storage.path(saved_profile.resume.name)
                try:
                    # Call utility functions to parse PDF and extract skills
                    text = utils.extract_text_from_pdf(resume_path)
                    skills_list = utils.extract_skills(text)
                    saved_profile.skills = ", ".join(skills_list)
                    # Save only the updated skills field
                    saved_profile.save(update_fields=['skills'])
                    print(f"--- Skills extracted for {profile.user.username}: {len(skills_list)} found ---") # Log essential info
                except Exception as e:
                    print(f"ERROR during PDF processing/skill extraction for {profile.user.username}: {e}")
                    messages.error(request, "Could not process the uploaded resume.")
            else:
                 # Inform user if only preferences were updated (no new resume file)
                 if form.has_changed():
                     messages.success(request, "Preferences updated successfully.")
                 else:
                     messages.info(request, "No changes detected.") # Or "No new resume uploaded."

            # Redirect to results page after saving preferences and attempting parsing
            return redirect('results_page')
        else:
             # Form invalid: Prepare context to re-render the page with errors
             messages.error(request, "Please correct the form errors below.")
             context['form'] = form
             context.update(initial_data) # Keep initial data for unbound fields

    else: # GET request
        # Create form instance populated with current profile data and initial values
        form = ResumeUploadForm(instance=profile, initial=initial_data)
        context['form'] = form

    # Render the template for GET or invalid POST
    return render(request, 'resumeupload.html', context)


@login_required
def results_view(request):
    """Fetches jobs based on stored profile skills/preferences and renders results."""
    profile = request.user.profile

    # Retrieve preferences and skills from the profile
    skills_str = profile.skills
    location = profile.preferred_location
    salary = profile.expected_salary # Kept for display context
    experience = profile.experience_level_preference
    employment_types = profile.employment_type_preference # Comma-separated string from model
    interested_domain = profile.interested_domain

    # Prepare skills list for API call
    skills_list = [skill.strip() for skill in skills_str.split(',')] if skills_str else []
    skills_list = [skill for skill in skills_list if skill] # Remove empty strings

    # Call the utility function to fetch jobs from the API, passing preferences
    jobs_list = utils.fetch_jobs_api(
        skills_list=skills_list,
        location=location,
        interested_domain=interested_domain,
        salary=salary, # Passed but not directly used in API query
        experience=experience,
        employment_types=employment_types # Pass comma-separated string
    )
    print(f"Found {len(jobs_list)} jobs for {profile.user.username}") # Log job count

    # Prepare context data for the template
    context = {
        'jobs': jobs_list,
        'skills': skills_list,
        'location': location or "Not set",
        'salary': salary or "Not set",
        'experience': experience or "Any",
        # Pass employment types as a list for easier template looping
        'employment_types': employment_types.split(',') if employment_types else [],
        'interested_domain': interested_domain or "Not set"
    }
    return render(request, 'resultpage.html', context)