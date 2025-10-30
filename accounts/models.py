# accounts/models.py

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    # Link to the built-in User model
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Basic user information
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    highest_qualification = models.CharField(max_length=100, blank=True)
    interested_domain = models.CharField(max_length=100, blank=True)

    # Job search preferences
    preferred_location = models.CharField(max_length=100, blank=True)
    expected_salary = models.CharField(max_length=50, blank=True)
    # Stores the JSearch 'job_requirements' string (e.g., 'under_3_years_experience')
    experience_level_preference = models.CharField(max_length=50, blank=True, null=True, default='Any')
    # Stores comma-separated JSearch 'employment_types' (e.g., 'FULLTIME,INTERN')
    employment_type_preference = models.CharField(max_length=100, blank=True, null=True, default='FULLTIME')

    # Resume related fields
    resume = models.FileField(upload_to='resumes/', null=True, blank=True) 
    skills = models.TextField(null=True, blank=True) # Stores extracted skills as text
    original_resume_filename = models.CharField(max_length=255, null=True, blank=True) # Stores original upload name

    def __str__(self):
        """String representation of the Profile."""
        return f'{self.user.username} Profile'

# --- Signals ---

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    """Ensure Profile is created/saved when User is created/saved."""
    if created:
        Profile.objects.create(user=instance)
    # Ensure profile relationship exists before trying to save (accounts for potential delays)
    if hasattr(instance, 'profile'):
        instance.profile.save()