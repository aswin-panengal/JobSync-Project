# accounts/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
# Import forms AND the choices list needed for the 'Other' logic in profile_edit_view
from .forms import (
    UserRegisterForm,
    ProfileForm,
    SignInForm,
    ProfileEditForm,
    DOMAIN_CHOICES # Import choices list
)

def signup_view(request):
    """Handles new user registration."""
    if request.method == 'POST':
        user_form = UserRegisterForm(request.POST)
        profile_form = ProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            # Create User
            user = user_form.save(commit=False)
            user.username = user_form.cleaned_data['email']
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            # Update associated Profile
            profile = user.profile
            profile.first_name = profile_form.cleaned_data.get('first_name', '')
            profile.last_name = profile_form.cleaned_data.get('last_name', '')
            profile.phone_number = profile_form.cleaned_data.get('phone_number', '')
            profile.age = profile_form.cleaned_data.get('age', None)
            profile.highest_qualification = profile_form.cleaned_data.get('highest_qualification', '')
            profile.experience_level_preference = profile_form.cleaned_data.get('experience_level_preference', 'Any')

            # Handle 'Interested Domain' including 'Other' option
            domain_choice = profile_form.cleaned_data.get('interested_domain')
            if domain_choice == 'Other':
                profile.interested_domain = profile_form.cleaned_data.get('interested_domain_other', '').strip() or 'Other'
            else:
                profile.interested_domain = domain_choice
            profile.save()

            #messages.success(request, "Account created successfully! Please sign in.")
            return redirect('success_page') # Redirect to success page after success
        else:
            # Re-render form with validation errors
            messages.error(request, "Please correct the errors below.")
            # Optional: Log errors to terminal for debugging
            # print("Signup User Form Errors:", user_form.errors)
            # print("Signup Profile Form Errors:", profile_form.errors)
            context = {'user_form': user_form, 'profile_form': profile_form}
            return render(request, 'signup.html', context)

    else: # GET request - display empty forms
        user_form = UserRegisterForm()
        profile_form = ProfileForm()

    context = {'user_form': user_form, 'profile_form': profile_form}
    return render(request, 'signup.html', context)


def signin_view(request):
    """Handles user login using email."""
    if request.method == 'POST':
        form = SignInForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            #messages.info(request, "Welcome back!")
            return redirect('resume_upload') # Go to resume upload page after login
        # Invalid login falls through to render form with errors
    else: # GET request - display empty form
        form = SignInForm()
    return render(request, 'signin.html', {'form': form})


def logout_view(request):
    """Logs the user out."""
    logout(request)
    #messages.success(request, "You have been logged out.")
    return redirect('index') # Go back to homepage


@login_required # Protects view for logged-in users only
def profile_edit_view(request):
    """Allows users to edit their profile details."""
    profile = request.user.profile # Get current user's profile
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=profile)
        if form.is_valid():
            # Get instance but don't save yet to handle 'Other' domain logic
            profile_instance = form.save(commit=False)

            # Handle 'Interested Domain' including 'Other' option
            domain_choice = form.cleaned_data.get('interested_domain')
            if domain_choice == 'Other':
                profile_instance.interested_domain = form.cleaned_data.get('interested_domain_other', '').strip() or 'Other'
            else:
                profile_instance.interested_domain = domain_choice

            profile_instance.save() # Save the final changes
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile_edit') # Redirect back to the same page
        else:
            # Re-render form with validation errors
            messages.error(request, "Please correct the errors below.")
            # Optional: Log errors
            # print("Profile Edit Form Errors:", form.errors)
    else: # GET request
        # Prepare initial data for the 'Other' text field if needed
        initial_data = {}
        # Get list of standard domain values (excluding the blank option)
        standard_domain_values = [choice[0] for choice in DOMAIN_CHOICES if choice[0]]
        # If current saved domain is not a standard one, pre-fill 'Other' field
        if profile.interested_domain not in standard_domain_values and profile.interested_domain:
             initial_data['interested_domain_other'] = profile.interested_domain # Pre-fill text box
             initial_data['interested_domain'] = 'Other' # Select 'Other' in dropdown

        # Create form instance pre-populated with current profile data and initial 'Other' data if applicable
        form = ProfileEditForm(instance=profile, initial=initial_data if initial_data else None)

    # Render template for GET or invalid POST
    return render(request, 'profile_edit.html', {'form': form})