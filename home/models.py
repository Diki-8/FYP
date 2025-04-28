from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User 


class Contact(models.Model):
    name = models.CharField(max_length=122)
    email = models.CharField(max_length=122)
    message = models.TextField()
    date = models.DateField(default=timezone.now)

class Dog(models.Model):
    SIZE_CHOICES = [
        ('small', 'Small (under 20 lbs)'),
        ('medium', 'Medium (20-50 lbs)'),
        ('large', 'Large (50-90 lbs)'),
    ]

    BREED_CHOICES = [
        ('beagle', 'Beagle'),
        ('bhote', 'Bhote Kukur'),
        ('boxer', 'Boxer'),
        ('bulldog', 'Bulldog'),
        ('chihuahua', 'Chihuahua'),
        ('cocker', 'Cocker Spaniel'),
        ('dalmatian', 'Dalmatian'),
        ('damchi', 'Damchi'),
        ('german', 'German Shepherd'),
        ('golden', 'Golden Retriever'),
        ('husky', 'Siberian Husky'),
        ('japanese', 'Japanese Spitz'),
        ('lab', 'Labrador Retriever'),
        ('lhasa', 'Lhasa Apso'),
        ('maltese', 'Maltese'),
        ('pomeranian', 'Pomeranian'),
        ('poodle', 'Poodle'),
        ('pug', 'Pug'),
        ('rottweiler', 'Rottweiler'),
        ('shih', 'Shih Tzu'),
        ('spaniel', 'English Springer Spaniel'),
        ('tibetan', 'Tibetan Mastiff'),
        ('yorkie', 'Yorkshire Terrier'),
    ]

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dogs')
    name = models.CharField(max_length=100)
    breed = models.CharField(max_length=100, choices=BREED_CHOICES, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    size = models.CharField(max_length=10, choices=SIZE_CHOICES, blank=True)
    special_notes = models.TextField(blank=True)

class TimeSlot(models.Model):
    start_time = models.TimeField()
    end_time = models.TimeField()
    service_type = models.CharField(
        max_length=20,
        choices=[
            ('boarding', 'Boarding'),
            ('daycare', 'Daycare'),
            ('grooming', 'Grooming')
        ]
    )
    
    def __str__(self):
        return f"{self.get_service_type_display()} - {self.start_time.strftime('%I:%M %p')} to {self.end_time.strftime('%I:%M %p')}"
    
    @staticmethod
    def generate_default_slots():
        """Creates slots from 7 AM to 7 PM"""
        from datetime import time
        
        slots = []
        for hour in range(7, 19): 
            start = time(hour, 0)  
            end = time(hour + 1, 0)  
            slots.append(TimeSlot(start_time=start, end_time=end, service_type='grooming'))
        
        return slots

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dog = models.ForeignKey(Dog, on_delete=models.CASCADE)
    
    service = models.CharField(max_length=20, choices=[
        ('boarding', 'Boarding'),
        ('daycare', 'Daycare'),
        ('grooming', 'Grooming')
    ], null=True, blank=True)

    status = models.CharField(max_length=20, choices=[
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed')
    ], default='confirmed')

    date = models.DateField()
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, null=True, default=1)
    special_requests = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('date', 'time_slot', 'dog')
