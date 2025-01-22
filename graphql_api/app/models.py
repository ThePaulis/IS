from django.db import models

class Player(models.Model):
    name = models.CharField(max_length=100)
    full_name = models.CharField(max_length=255)
    birth_date = models.CharField(max_length=10)  # Store as string, e.g., 'YYYY-MM-DD'
    age = models.CharField(max_length=3)  # Change to CharField to store age as string
    height_cm = models.CharField(max_length=10)  # Store height as string
    weight_kgs = models.CharField(max_length=10)  # Store weight as string
    positions = models.CharField(max_length=100)
    nationality = models.CharField(max_length=100)
    overall_rating = models.CharField(max_length=3)  # Store rating as string
    potential = models.CharField(max_length=3)  # Store potential as string
    value_euro = models.CharField(max_length=12)  # Store as string for currency values
    wage_euro = models.CharField(max_length=12)  # Store wage as string
    preferred_foot = models.CharField(max_length=10)
    international_reputation = models.CharField(max_length=2)  # Store as string
    weak_foot = models.CharField(max_length=2)  # Store as string
    skill_moves = models.CharField(max_length=2)  # Store as string
    body_type = models.CharField(max_length=50)
    release_clause_euro = models.CharField(max_length=12)  # Store as string
    national_team = models.CharField(max_length=100)
    national_rating = models.CharField(max_length=3)  # Store national rating as string
    national_team_position = models.CharField(max_length=50)
    national_jersey_number = models.CharField(max_length=3)  # Store as string
    crossing = models.CharField(max_length=2)  # Store as string
    finishing = models.CharField(max_length=2)  # Store as string
    heading_accuracy = models.CharField(max_length=2)  # Store as string
    short_passing = models.CharField(max_length=2)  # Store as string
    volleys = models.CharField(max_length=2)  # Store as string
    dribbling = models.CharField(max_length=2)  # Store as string
    curve = models.CharField(max_length=2)  # Store as string
    freekick_accuracy = models.CharField(max_length=2)  # Store as string
    long_passing = models.CharField(max_length=2)  # Store as string
    ball_control = models.CharField(max_length=2)  # Store as string
    acceleration = models.CharField(max_length=2)  # Store as string
    sprint_speed = models.CharField(max_length=2)  # Store as string
    agility = models.CharField(max_length=2)  # Store as string
    reactions = models.CharField(max_length=2)  # Store as string
    balance = models.CharField(max_length=2)  # Store as string
    shot_power = models.CharField(max_length=2)  # Store as string
    jumping = models.CharField(max_length=2)  # Store as string
    stamina = models.CharField(max_length=2)  # Store as string
    strength = models.CharField(max_length=2)  # Store as string
    long_shots = models.CharField(max_length=2)  # Store as string
    aggression = models.CharField(max_length=2)  # Store as string
    interceptions = models.CharField(max_length=2)  # Store as string
    positioning = models.CharField(max_length=2)  # Store as string
    vision = models.CharField(max_length=2)  # Store as string
    penalties = models.CharField(max_length=2)  # Store as string
    composure = models.CharField(max_length=2)  # Store as string
    marking = models.CharField(max_length=2)  # Store as string
    standing_tackle = models.CharField(max_length=2)  # Store as string
    sliding_tackle = models.CharField(max_length=2)  # Store as string

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = 'players'
