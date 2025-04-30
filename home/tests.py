from django.test import TestCase
from django.contrib.auth.models import User
from home.models import Dog

"""
class DogModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")

    def test_create_dog_valid(self):
        dog = Dog.objects.create(
            owner=self.user,
            name="Buddy",
            breed="tibetan",
            age=2,
            size="large",
            special_notes="Loves treats"
        )
        self.assertEqual(dog.name, "Buddy")
        self.assertEqual(dog.breed, "tibetan")
        self.assertEqual(dog.get_breed_display(), "Tibetan Mastiff")
        self.assertEqual(Dog.objects.count(), 1)
"""

from django.core.exceptions import ValidationError

class DogModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="12345")

    def test_create_dog_valid(self):
        dog = Dog.objects.create(
            owner=self.user,
            name="Buddy",
            breed="tibetan",
            age=2,
            size="large",
            special_notes="Loves treats"
        )
        self.assertEqual(dog.name, "Buddy")
        self.assertEqual(dog.breed, "tibetan")
        self.assertEqual(dog.get_breed_display(), "Tibetan Mastiff")
        self.assertEqual(Dog.objects.count(), 1)

    def test_invalid_breed(self):
        dog = Dog(owner=self.user, name="Buddy", breed="invalid", age=2)
        with self.assertRaises(ValidationError):
            dog.full_clean()
    
    def test_negative_age(self):
        dog = Dog(owner=self.user, name="Buddy", breed="lab", age=-1)
        with self.assertRaises(ValidationError):
            dog.full_clean()