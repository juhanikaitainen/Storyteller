import decimal
import json
from datetime import date

from accounts.models import Transaction, Wallet
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseNotFound)
from django.shortcuts import redirect, render
from users.decorators import moderator_required, not_frozen, writer_required
from users.models import Customuser

from .forms import StoryApprovalForm
from .models import Section, Sectionlink, Story, Userdata
from .schema import storySchemaValidate
from .utils import *

# Create your views here.


@login_required
@not_frozen
def story_home(request):
    userinfo = Customuser.objects.get(djangouser=request.user)
    return render(request, 'stories/home.html', {'userinfo': userinfo})


@login_required
@not_frozen
def story_list(request):
    userinfo = Customuser.objects.get(djangouser=request.user)
    age = calculate_age(userinfo.dob)
    catalog = Story.objects.filter(approved=True, rating__lte=pg_group(age))
    return render(request, 'stories/all.html', {'catalog': catalog})


@login_required
@not_frozen
def story_detail(request, id):
    userinfo = Customuser.objects.get(djangouser=request.user)
    age = calculate_age(userinfo.dob)
    hits = Story.objects.filter(
        pk=id, approved=True, rating__lte=pg_group(age))
    if len(hits) > 0:
        story = hits[0]
        wallet = Wallet.objects.get(owner=request.user)
        data = Userdata.objects.filter(user=request.user, story=story)
        resumePos = None
        canbuy = True
        if len(data) > 0:
            resumePos = data[0].section
        elif wallet.balance < story.price:
            canbuy = False
        elif story.author == request.user or userinfo.usertype >= userinfo.Category.MODERATOR:
            Userdata(story=story, user=request.user, section=Section.objects.get(
                is_starting=True, story=story)).save()
            resumePos = Userdata.objects.filter(
                user=request.user, story=story)[0].section
        return render(request, 'stories/detail.html', {'story': story, 'resumePos': resumePos, 'canbuy': canbuy})
    else:
        return HttpResponseNotFound('This story does not exist!')


@login_required
@not_frozen
def story_buy(request, id):
    userinfo = Customuser.objects.get(djangouser=request.user)
    age = calculate_age(userinfo.dob)
    hits = Story.objects.filter(
        pk=id, approved=True, rating__lte=pg_group(age))

    # if this story should be visible to the user then len(hits) > 0
    if len(hits) > 0:
        # get the story
        story = hits[0]
        # get wallet of the user
        wallet = Wallet.objects.get(owner=request.user)
        data = Userdata.objects.filter(
            user=request.user, story=story)  # get user's owned stories

        # check if already owned or not enough funds
        if len(data) > 0 or request.user == story.author or userinfo.usertype >= Customuser.Category.MODERATOR:
            return HttpResponse('You already own this story!')
        elif wallet.balance < story.price:
            return HttpResponse('You do not have enough coins to buy this story.')

        # can buy now, deduct amount from wallet
        wallet.balance -= story.price
        # add deduction to transaction history
        Transaction(person=request.user, withdrawn=True,
                    amount=story.price).save()
        wallet.save()

        # send the deducted money into author's wallet
        Wallet.objects.filter(owner=story.author).update(
            balance=F('balance') + story.price)
        # add this to transaction history
        Transaction(person=story.author, withdrawn=False,
                    amount=story.price).save()

        # add this story to buyer's userdata
        starting_section = Section.objects.filter(
            is_starting=True, story=story)
        newdata = Userdata(story=story, user=request.user,
                           section=starting_section[0])
        newdata.save()
        return redirect('stories:my')
    else:
        return HttpResponseNotFound('This story does not exist!')


@login_required
@not_frozen
def story_my(request):
    return render(request, 'stories/my.html', {'mystories': Userdata.objects.filter(user=request.user)})


@login_required
@not_frozen
@moderator_required
def story_approve(request):
    return render(request, 'stories/approve.html', {'stories': Story.objects.filter()})


@login_required
@not_frozen
@moderator_required
def story_approve_id(request, id):
    try:
        story = Story.objects.get(pk=id)
    except Story.DoesNotExist:
        return HttpResponseNotFound('Cannot approve this story!')
    if request.method == 'POST':
        form = StoryApprovalForm(request.POST)
        if form.is_valid():
            story.rating = form.cleaned_data['rating']
            story.approved = form.cleaned_data['approved']
            story.save()
            return redirect('stories:approve')
    else:
        form = StoryApprovalForm()
    return render(request, 'stories/approval-form.html', {'form': form, 'story': story, 'firstsection': Section.objects.get(is_starting=True, story=story)})


@login_required
@not_frozen
def story_read(request, storyid, sectionid):
    try:
        story = Story.objects.get(id=storyid)
    except Story.DoesNotExist:
        return HttpResponseNotFound('Story does not exist')

    try:
        section = Section.objects.get(id=sectionid, story=story)
    except Section.DoesNotExist:
        return HttpResponseNotFound('Section does not exist')

    find_position = Userdata.objects.filter(story=story, user=request.user)
    customuser = Customuser.objects.get(djangouser=request.user)
    if len(find_position) > 0:
        position = find_position[0]
        position.section = section
        position.save()
    elif story.author == request.user or customuser.usertype >= Customuser.Category.MODERATOR:
        position = Userdata(story=story, user=request.user, section=Section.objects.get(
            story=story, is_starting=True))
        position.save()
    else:
        return HttpResponseForbidden('You are not allowed to access this story')

    links = None
    if not position.section.is_ending:
        links = Sectionlink.objects.filter(fromsection=position.section)
    return render(request, 'stories/read.html', {'fsid': Section.objects.get(is_starting=True, story=story), 'sid': story.id, 'name': story.title, 'section': position.section, 'links': links})


@login_required
@not_frozen
@writer_required
def story_new(request):
    def renderError(err):
        return render(request, 'stories/new.html', {'err': err, 'fileinfo': request.POST['jsonfile'].strip()})

    if request.method == 'POST':
        jsonstory = request.POST['jsonfile']
        parsed = parseJson(jsonstory)
        if (parsed is not None) and storySchemaValidate(parsed):
            meta = parsed['meta']
            sections = parsed['sections']

            if countStartingSections(sections) > 1:
                return renderError("There can be only one starting section")

            story_positions = {section['position'] for section in sections}

            if len(sections) != len(story_positions):
                return renderError("Story Positions Are Not Unique")

            links = extractLinks(sections)
            for link in links:
                if link['from'] not in story_positions or link['to'] not in story_positions:
                    return renderError("Broken Story Link: " + str(link))

            link_locations = {link['to'] for link in links}
            for section in sections:
                if not (section['position'] in link_locations or section['is_starting']):
                    return renderError("Unreachable Section found: " + str(section))

            story = None
            try:
                Btitle = meta['title']
                Bsummary = meta['summary']
                story = Story(title=Btitle, summary=Bsummary, approved=False, rating=Story.Pg.UNIVERSAL,
                              price=decimal.Decimal(meta['price']), author=request.user)
                story.save()
            except Exception as e:
                return renderError("Error Code: STORY_SAVE. Please contact the system administrator")

            try:
                for section in sections:
                    Btext = section['text']
                    Bposition = section['position']
                    Section(is_starting=section['is_starting'], is_ending=section['is_ending'],
                            text=Btext, story=story, storypos=Bposition).save()
                for link in links:
                    Bfrom = link['from']
                    Bto = link['to']
                    Bbutton = link['button']
                    Sectionlink(fromsection=Section.objects.get(story=story, storypos=Bfrom), tosection=Section.objects.get(
                        story=story, storypos=Bto), button=Bbutton).save()
            except Exception as e:
                story.delete()
                return renderError("Error Code: SECTION_SAVE. Please contact the system administrator")

            return redirect('stories:valid')
        else:
            return renderError("INVALID format. Please check the documentation for the correct format!")
    return render(request, 'stories/new.html', {'err': None, 'fileinfo': None})


@login_required
@not_frozen
@writer_required
def story_valid(request):
    return render(request, 'stories/valid.html')
