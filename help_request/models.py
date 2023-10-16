from django.db import models
from user_app.models import MyUser
from django.utils import timezone


class PriorityChoices:
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"

    CHOICES = [
        (LOW, "Low"),
        (MEDIUM, "Medium"),
        (HIGH, "High"),
    ]


class StatusChoices:
    ACTIVE = "Active"
    DECLINED = "Declined"
    FOR_RESTORATION = "For restoration"
    APPROVED = "Approved"
    IN_PROCESS = "In process"
    COMPLETED = "Completed"

    CHOICES = [
        (ACTIVE, "Active"),
        (DECLINED, "Declined"),
        (FOR_RESTORATION, "For restoration"),
        (APPROVED, "Approved"),
        (IN_PROCESS, "In process"),
        (COMPLETED, "Completed"),
    ]


class HelpRequest(models.Model):
    subject = models.CharField(max_length=255)
    text = models.TextField()
    requester = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='requests')
    priority = models.CharField(max_length=6, choices=PriorityChoices.CHOICES)
    status = models.CharField(max_length=15, choices=StatusChoices.CHOICES, default=StatusChoices.ACTIVE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.requester} -- {self.subject} -- {self.priority} -- {self.status}"


class DeclinedRequest(models.Model):
    declined_request = models.OneToOneField(HelpRequest, on_delete=models.CASCADE, related_name='declined_request')
    comment = models.TextField()

    def __str__(self):
        return f"{self.declined_request} -- declined"
