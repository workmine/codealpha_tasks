from django.db import models
from django.contrib.auth.models import User
from django.db.models import Max
import os

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, default="")
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    follows = models.ManyToManyField("self", related_name="followed_by", symmetrical=False, blank=True)

    def __str__(self):
        return self.user.username

class Post(models.Model):
    user = models.ForeignKey(User, related_name="posts", on_delete=models.CASCADE)
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    video = models.FileField(upload_to='post_videos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(User, related_name="liked_posts", blank=True)

    def total_likes(self):
        return self.likes.count()

class Comment(models.Model):
    post = models.ForeignKey(Post, related_name="comments", on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class Message(models.Model):
    sender = models.ForeignKey(User, related_name="sent_messages", on_delete=models.CASCADE)
    recipient = models.ForeignKey(User, related_name="received_messages", on_delete=models.CASCADE)
    body = models.TextField(blank=True, null=True)  # Allowed to be empty if sending just a file
    file = models.FileField(upload_to='chat_uploads/', blank=True, null=True) # New File Field
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} to {self.recipient}"

    class Meta:
        ordering = ['timestamp']

    # Helpers to check file type in HTML
    @property
    def is_image(self):
        if self.file:
            ext = os.path.splitext(self.file.name)[1].lower()
            return ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        return False

    @property
    def is_video(self):
        if self.file:
            ext = os.path.splitext(self.file.name)[1].lower()
            return ext in ['.mp4', '.mov', '.avi', '.webm']
        return False