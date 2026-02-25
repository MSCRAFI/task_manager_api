from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tasks',
        db_index=True
    )
    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True, default='')
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium',
        db_index=True
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    due_date = models.DateField(
        null=True,
        blank=True,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(
                # Composite index: covers the most common query pattern:
                # filter(user=X, status=Y, priority=Z).order_by('-created_at')
                fields=['user', 'status', 'priority', 'created_at'],
                name='idx_user_stat_prio_created'
            ),
            # Composite index for user + due_date ordering
            models.Index(
                fields=['user', 'due_date'],
                name='idx_user_due_date'
            ),
            # Composite index for user + title search
            models.Index(
                fields=['user', 'title'],
                name='idx_user_title'
            ),

        ]

    def __str__(self):
        return f"{self.title} ({self.user.username})"
