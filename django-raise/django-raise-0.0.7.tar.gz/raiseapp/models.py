from django.db import models
from django.utils.timezone import now


class Campaign(models.Model):
    title = models.CharField(max_length=256)
    slug = models.SlugField()
    short = models.TextField()
    body = models.TextField()

    goal = models.IntegerField()
    end_date = models.DateField()

    _raised = None

    @property
    def raised(self):
        if self._raised is None:
            pledge_sum = (
                self.pledge_set
                .exclude(active=False)
                .aggregate(models.Sum('amount'))
            )['amount__sum']

            if pledge_sum is None:
                self._raised = 0
            else:
                self._raised = pledge_sum

        return self._raised

    @property
    def percent(self):
        return self.raised / self.goal

    @property
    def display_percent(self):
        percent_value = self.percent * 100
        return '{:.0f}'.format(percent_value)

    @property
    def pledge_count(self):
        return self.pledge_set.exclude(active=False).count()

    @property
    def days_to_go(self):
        today = now().date()
        delta = self.end_date - today

        days = delta.days

        if days < 0:
            days = 0

        return days

    def __str__(self):
        return self.title


class Reward(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    amount = models.IntegerField()
    description = models.TextField()
    timeframe = models.TextField(blank=True)

    class Meta:
        ordering = ['amount']

    @property
    def display_amount(self):
        # TODO: If you wanted to do currencies you would do it here
        return str(self.amount)

    def __str__(self):
        return self.display_amount


class Reminder(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    email = models.EmailField()

    active = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email


class Pledge(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    email = models.EmailField()
    name = models.CharField(max_length=256)
    amount = models.IntegerField()

    comments = models.TextField(blank=True)

    active = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.email
