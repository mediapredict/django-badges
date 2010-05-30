from django.db import models
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from signals import badge_awarded
from badges.managers import BadgeManager

LEVEL_CHOICES = (
        ("1", "Bronze"),
        ("2", "Silver"),
        ("3", "Gold"),
        ("4", "Diamond"),
        )

class Badge(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    user = models.ManyToManyField(User, related_name="badges", through='BadgeToUser')
    level = models.CharField(max_length=1, choices=LEVEL_CHOICES)
    
    icon = models.ImageField(upload_to='badge_images')
    
    objects = BadgeManager()
    
    @property
    def meta_badge(self):
        from utils import registered_badges
        return registered_badges[self.id]
    
    @property
    def title(self):
        return self.meta_badge.title
    
    @property
    def description(self):
        return self.meta_badge.description
    
    def __unicode__(self):
        return u"%s" % self.title
    
    def get_absolute_url(self):
        return reverse('badge_detail', kwargs={'slug': self.id})
    
    def award_to(self, user):
        has_badge = self in user.badges.all()
        if self.meta_badge.one_time_only and has_badge:
            return False
        
        BadgeToUser.objects.create(badge=self, user=user)
                
        badge_awarded.send(sender=self.meta_badge, user=user, badge=self)
        
        message_template = "You just got the %s Badge!"
        user.message_set.create(message = message_template % self.title)
        
        return BadgeToUser.objects.filter(badge=self, user=user).count()

class BadgeToUser(models.Model):
    badge = models.ForeignKey(Badge)
    user = models.ForeignKey(User)
    
    created = models.DateTimeField(auto_now_add=True)