from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser

class Section(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class Coordinator(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    password = models.CharField(max_length=100)
    email = models.EmailField()
    contact_number = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    sections = models.ManyToManyField(Section, related_name='coordinators')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Chairman(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=20)
    Section = models.CharField(max_length=100)
    # Add more fields as needed

    def __str__(self):
        return self.username

class Intern(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    coordinator = models.ForeignKey(Coordinator, on_delete=models.CASCADE, related_name='interns')
    section = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class InternReport(models.Model):
    intern = models.ForeignKey(Intern, on_delete=models.CASCADE)
    week = models.CharField(max_length=20)
    date = models.DateField()
    hours = models.DecimalField(max_digits=4, decimal_places=2)
    activities = models.TextField()
    score = models.IntegerField()
    new_learnings = models.TextField()

    def __str__(self):
        return f"{self.intern} - Week {self.week} - {self.date}"

class SectionUpdate(models.Model):
    coordinator = models.ForeignKey(Coordinator, on_delete=models.CASCADE)
    update_text = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Update for {self.section} by {self.coordinator} at {self.submitted_at}"

class Assessment(models.Model):
    coordinator = models.ForeignKey(Coordinator, on_delete=models.CASCADE)
    intern = models.ForeignKey(Intern, on_delete=models.CASCADE)
    week = models.CharField(max_length=20)
    assessment = models.TextField()

    def __str__(self):
        return f"Assessment for {self.intern} by {self.coordinator} (Week {self.week})"

class Portfolio(models.Model):
    intern = models.OneToOneField(Intern, on_delete=models.CASCADE)
    rating = models.IntegerField()
    # Add other fields as needed

    def __str__(self):
        return f"Portfolio for {self.intern}"
