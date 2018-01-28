from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages

from . import models
from . import forms


def campaign(request, slug, template="campaign.html"):
    campaign = get_object_or_404(models.Campaign, slug=slug)

    return render(
        request,
        template,
        dict(
            campaign=campaign,
        ),
    )


def pledge(request, slug, post_pledge=None, template="pledge.html"):
    campaign = get_object_or_404(models.Campaign, slug=slug)

    if request.method == 'POST':
        pledge_form = forms.PledgeForm(request.POST)
        if pledge_form.is_valid():
            pledge = pledge_form.save(commit=False)
            pledge.campaign = campaign
            pledge.save()

            if post_pledge:
                post_pledge(request, pledge)

            messages.info(
                request,
                'Thanks for your pledge! You will receive an email shortly with more details.'
            )
            return redirect('campaign', campaign.slug)
    else:
        form = forms.PledgeForm()

    return render(
        request,
        template,
        dict(
            campaign=campaign,
            form=form,
        ),
    )


def reminder(request, slug, post_reminder=None, template="reminder.html"):
    campaign = get_object_or_404(models.Campaign, slug=slug)

    if request.method == 'POST':
        reminder_form = forms.ReminderForm(request.POST)
        if reminder_form.is_valid():
            reminder = reminder_form.save(commit=False)
            reminder.campaign = campaign
            reminder.save()
            if post_reminder:
                post_reminder(request, reminder)

            messages.info(
                request,
                'We will email you a reminder a few days before the campaign ends!'
            )
            return redirect('campaign', campaign.slug)

    else:
        form = forms.ReminderForm()

    return render(
        request,
        template,
        dict(
            campaign=campaign,
            form=form,
        ),
    )
