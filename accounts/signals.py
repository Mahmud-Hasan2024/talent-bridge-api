from django.db.models.signals import post_migrate, post_save
from django.contrib.auth.models import Group
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_migrate)
def create_default_groups(sender, **kwargs):
    if not sender.name.endswith("accounts"):
        return

    groups = ["Admin", "Employer", "Job Seeker"]
    for group_name in groups:
        Group.objects.get_or_create(name=group_name)


@receiver(post_save, sender=User)
def assign_user_group(sender, instance, created, **kwargs):
    if created:
        group_name = None
        if instance.role == "admin":
            group_name = "Admin"
        elif instance.role == "employer":
            group_name = "Employer"
        elif instance.role == "seeker":
            group_name = "Job Seeker"

        if group_name:
            group = Group.objects.get(name=group_name)
            instance.groups.add(group)
