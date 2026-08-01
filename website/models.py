from django.db import models

class User(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=100)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    status = models.CharField(max_length=50, default="Plant Lover")
    ai_scan_count = models.IntegerField(default=0)
    ai_scan_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name
    

class Plant(models.Model):
    name = models.CharField(max_length=100, unique=True)
    page = models.CharField(max_length=50, blank=True, null=True)
    watering = models.CharField(max_length=200)
    sunlight = models.CharField(max_length=200)
    soil = models.CharField(max_length=200)
    fertilizer = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.name

class Contact(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class MyPlant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "plant")

    def __str__(self):
        return f"{self.user.name} - {self.plant.name}"


class AiScan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plant_name = models.CharField(max_length=100)
    scan_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.name} - {self.plant_name}"

class WateringReminder(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plant_name = models.CharField(max_length=100, null=True, blank=True)
    watering_date = models.DateField()
    watering_time = models.TimeField()
    repeat = models.CharField(max_length=30, default="Doesn't Repeat")
    is_watered = models.BooleanField(default=False)
    watered_on = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notification_sent = models.BooleanField(default=False)
    missed_popup_shown = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.plant_name} - {self.user.name}"




class ScheduleReminder(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE)

    plant_name = models.CharField(max_length=100)

    task = models.CharField(max_length=100)

    schedule_date = models.DateField()

    schedule_time = models.TimeField()

    repeat = models.CharField(max_length=50)

    is_done = models.BooleanField(default=False)

    done_on = models.DateTimeField(null=True, blank=True)

    notification_sent = models.BooleanField(default=False)

    missed_popup_shown = models.BooleanField(default=False)

    def __str__(self):
        return self.plant_name

class FavoritePlant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plant = models.ForeignKey(Plant, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "plant")

    def __str__(self):
        return f"{self.user.name} - {self.plant.name}"

class PushSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    endpoint = models.TextField(unique=True)
    p256dh = models.TextField()
    auth = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.name
# Create your models here.
