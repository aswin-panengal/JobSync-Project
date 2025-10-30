
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Profile # Ensure Profile model has the updated fields

# --- Reusable Choices ---

# Values match JSearch API 'job_requirements' parameter
EXPERIENCE_CHOICES = [
    ('Any', 'Any Experience Level'),
    ('no_experience', 'No Experience / Intern'),
    ('under_3_years_experience', 'Under 3 Years Experience'),
    ('more_than_3_years_experience', 'More than 3 Years Experience'),
]

QUALIFICATION_CHOICES = [
    ('', 'Select'),
    ('High School', 'High School'),
    ('Diploma', 'Diploma'),
    ('Bachelors Degree', "Bachelor's Degree"),
    ('Masters Degree', "Master's Degree"),
    ('PhD', 'PhD'),
    ('Other', 'Other'),
]

# Values match JSearch API 'employment_types' parameter
EMPLOYMENT_CHOICES = [
    ('FULLTIME', 'Full-time'),
   #('CONTRACTOR', 'Contractor'),
    ('PARTTIME', 'Part-time'),
    ('INTERN', 'Internship'),
]

LOCATION_CHOICES = [
    ('Bengaluru', 'Bengaluru'),
    ('Chennai', 'Chennai'),
    ('Delhi', 'Delhi'),
    ('Hyderabad', 'Hyderabad'),
    ('Mumbai', 'Mumbai'),
    ('Puducherry', 'Puducherry'),
    ('Remote', 'Remote'),
    ('India', 'India (General)'), # Use 'India' for broader search
]

SALARY_CHOICES = [
    ('Any', 'Any Salary'),
    ('5 LPA+', '₹5 LPA+'),
    ('10 LPA+', '₹10 LPA+'),
    ('20 LPA+', '₹20 LPA+'),
]

DOMAIN_CHOICES = [
    ('', 'Select Domain'),
    ('Web Development', 'Web Development (Backend/Frontend/Fullstack)'),
    ('Data Science', 'Data Science / Analysis'),
    ('Machine Learning', 'Machine Learning / AI'),
    ('Cloud Computing', 'Cloud Computing (AWS/Azure/GCP)'),
    ('DevOps', 'DevOps / Site Reliability'),
    ('Mobile Development', 'Mobile Development (Android/iOS)'),
    ('Cybersecurity', 'Cybersecurity'),
    ('Database Administration', 'Database Administration'),
    ('Networking', 'Networking'),
    ('UI/UX Design', 'UI/UX Design'),
    ('Project Management', 'Project Management'),
    ('Other', 'Other'),
]

# --- Base Tailwind CSS Class for Widgets ---
tailwind_classes = 'mt-1 block w-full px-3 py-2 bg-white border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'


class UserRegisterForm(forms.ModelForm):
    """Handles User object creation (email/password) during sign up."""
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': tailwind_classes, 'id': 'password'}))
    confirm_password = forms.CharField(label="Confirm Password", widget=forms.PasswordInput(attrs={'class': tailwind_classes, 'id': 'id_confirm_password'}))

    class Meta:
        model = User
        fields = ['email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs.update({'class': tailwind_classes, 'placeholder': 'you@example.com'})

    def clean_confirm_password(self):
        """Validates that passwords match."""
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return confirm_password

    def clean_email(self):
        """Validates that the email is unique (case-insensitive)."""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email


class ProfileForm(forms.ModelForm):
    """Handles Profile details during initial sign up."""
    highest_qualification = forms.ChoiceField(
        choices=QUALIFICATION_CHOICES,
        widget=forms.Select(attrs={'class': tailwind_classes})
    )
    experience_level_preference = forms.ChoiceField(
        choices=EXPERIENCE_CHOICES,
        label="Experience Level",
        widget=forms.Select(attrs={'class': tailwind_classes})
    )
    interested_domain = forms.ChoiceField(
        choices=DOMAIN_CHOICES,
        required=True, # Domain is required during sign-up
        widget=forms.Select(attrs={'class': tailwind_classes})
    )
    interested_domain_other = forms.CharField(
        required=False, # Only required if dropdown is 'Other' (handled in view/JS)
        max_length=100,
        label="If 'Other', please specify domain",
        widget=forms.TextInput(attrs={'class': tailwind_classes + ' mt-2', 'id': 'id_interested_domain_other'})
    )
    class Meta:
        model = Profile
        # Fields shown on the sign-up form
        fields = ['first_name', 'last_name', 'phone_number', 'age',
                  'highest_qualification', 'interested_domain',
                  'experience_level_preference']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply styling and placeholders to form fields
        self.fields['first_name'].widget.attrs.update({'placeholder': 'Enter first name'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Enter last name'})
        self.fields['phone_number'].widget.attrs.update({'placeholder': 'e.g., 9876543210'})
        self.fields['age'].widget.attrs.update({'placeholder': 'Enter age'})
        # Apply base Tailwind classes to all fields defined in Meta
        for field_name in self.Meta.fields:
             if field_name in self.fields and hasattr(self.fields[field_name].widget, 'attrs'):
                 current_classes = self.fields[field_name].widget.attrs.get('class', '')
                 if tailwind_classes not in current_classes:
                     self.fields[field_name].widget.attrs['class'] = f'{tailwind_classes} {current_classes}'.strip()


class SignInForm(AuthenticationForm):
    """Customizes the default Django login form to use email."""
    # Override username field to accept email
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'autofocus': True, 'class': tailwind_classes, 'placeholder': 'you@example.com', 'id': 'id_username'})
    )
    password = forms.CharField(
        strip=False, # Keep leading/trailing whitespace
        widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'class': tailwind_classes, 'placeholder': 'Password', 'id': 'id_password'}),
    )


class ResumeUploadForm(forms.ModelForm):
    """Handles resume upload and setting job search preferences."""
    experience_level_preference = forms.ChoiceField(
        choices=EXPERIENCE_CHOICES,
        required=False, # Preference is optional
        label="Experience Level",
        widget=forms.Select(attrs={'class': tailwind_classes})
    )
    employment_types = forms.MultipleChoiceField(
        choices=EMPLOYMENT_CHOICES,
        widget=forms.CheckboxSelectMultiple(), # Use checkboxes
        required=False, # Preference is optional
        label="Employment Types"
    )
    interested_domain = forms.ChoiceField(
        choices=DOMAIN_CHOICES,
        required=True, # Domain required for searching jobs
        widget=forms.Select(attrs={'class': tailwind_classes})
    )

    class Meta:
        model = Profile
        # Fields shown on the resume upload/preference page
        fields = ['preferred_location', 'interested_domain',
                  'experience_level_preference', 'employment_types',
                  'resume'] # Resume field comes from Profile model
        widgets = {
            'resume': forms.FileInput(attrs={'id': 'id_resume', 'class': 'hidden'}), # Hide default input for custom UI
            'preferred_location': forms.Select(choices=LOCATION_CHOICES, attrs={'class': tailwind_classes}),
            # expected_salary removed from this form
        }
        labels = {
            'preferred_location': 'Preferred Location',
            'interested_domain': 'Interested Domain',
            # Other labels defined directly on fields above
        }


class ProfileEditForm(forms.ModelForm):
    """Handles editing the main Profile details (excluding resume/skills)."""
    highest_qualification = forms.ChoiceField(
        choices=QUALIFICATION_CHOICES,
        required=False, # Fields are optional when editing
        widget=forms.Select(attrs={'class': tailwind_classes})
    )
    experience_level_preference = forms.ChoiceField(
        choices=EXPERIENCE_CHOICES,
        required=False,
        label="Experience Level",
        widget=forms.Select(attrs={'class': tailwind_classes})
    )
    interested_domain = forms.ChoiceField(
        choices=DOMAIN_CHOICES,
        required=False, # Field is optional when editing
        widget=forms.Select(attrs={'class': tailwind_classes})
    )
    interested_domain_other = forms.CharField(
        required=False,
        max_length=100,
        label="If 'Other', please specify domain",
        widget=forms.TextInput(attrs={'class': tailwind_classes + ' mt-2', 'id': 'id_interested_domain_other'})
    )
    class Meta:
        model = Profile
        # Fields editable on the profile edit page
        fields = ['first_name', 'last_name', 'phone_number', 'age',
                  'highest_qualification', 'interested_domain',
                  'experience_level_preference']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply styling and placeholders
        self.fields['first_name'].widget.attrs.update({'placeholder': 'Enter first name'})
        self.fields['last_name'].widget.attrs.update({'placeholder': 'Enter last name'})
        self.fields['phone_number'].widget.attrs.update({'placeholder': 'e.g., 9876543210'})
        self.fields['age'].widget.attrs.update({'placeholder': 'Enter age'})
        # Apply base Tailwind classes to all fields
        for field_name in self.Meta.fields:
             if field_name in self.fields and hasattr(self.fields[field_name].widget, 'attrs'):
                 current_classes = self.fields[field_name].widget.attrs.get('class', '')
                 if tailwind_classes not in current_classes:
                     self.fields[field_name].widget.attrs['class'] = f'{tailwind_classes} {current_classes}'.strip()