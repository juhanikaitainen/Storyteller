from django.shortcuts import render, redirect
from django.http import HttpResponseNotFound, HttpResponse, HttpResponseForbidden
from .models import Story, Section, Sectionlink, Userdata
from accounts.models import Wallet, Transaction
from users.models import Customuser
from users.decorators import not_frozen, moderator_required, writer_required
from django.contrib.auth.decorators import login_required
from datetime import date
from django.db.models import F
from .forms import StoryApprovalForm
import json
import decimal

# Create your views here.

def calculate_age(born):
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

def pg_group(age):
    if age >= 18:
        return Story.Pg.ADULT
    elif age >= 12:
        return Story.Pg.ADOLESCENT
    else:
        return Story.Pg.UNIVERSAL

def parse(file):
    try:
        return json.loads(file)
    except ValueError as e:
        return None

@login_required
@not_frozen
def story_home(request):
    userinfo = Customuser.objects.get(djangouser=request.user)
    return render(request, 'stories/home.html', { 'userinfo': userinfo })

@login_required
@not_frozen
def story_list(request):
    userinfo = Customuser.objects.get(djangouser=request.user)
    age = calculate_age(userinfo.dob)
    catalog = Story.objects.filter(approved=True, rating__lte=pg_group(age))
    return render(request, 'stories/all.html', { 'catalog': catalog })

@login_required
@not_frozen
def story_detail(request, id):
    userinfo = Customuser.objects.get(djangouser=request.user)
    age = calculate_age(userinfo.dob)
    hits = Story.objects.filter(pk=id, approved=True, rating__lte=pg_group(age))
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
            Userdata(story=story, user=request.user, section=Section.objects.get(is_starting=True, story=story)).save()
            resumePos = Userdata.objects.filter(user=request.user, story=story)[0].section
        return render(request, 'stories/detail.html', { 'story': story, 'resumePos': resumePos, 'canbuy': canbuy })
    else:
        return HttpResponseNotFound('This story does not exist!')

@login_required
@not_frozen
def story_buy(request, id):
    userinfo = Customuser.objects.get(djangouser=request.user)
    age = calculate_age(userinfo.dob)
    hits = Story.objects.filter(pk=id, approved=True, rating__lte=pg_group(age))

    # if this story should be visible to the user then len(hits) > 0
    if len(hits) > 0:
        story = hits[0]                                                 # get the story
        wallet = Wallet.objects.get(owner=request.user)                 # get wallet of the user
        data = Userdata.objects.filter(user=request.user, story=story)  # get user's owned stories

        # check if already owned or not enough funds
        if len(data) > 0 or request.user == story.author or userinfo.usertype >= Customuser.Category.MODERATOR:
            return HttpResponse('You already own this story!')
        elif wallet.balance < story.price:
            return HttpResponse('You do not have enough coins to buy this story.')

        # can buy now, deduct amount from wallet
        wallet.balance -= story.price
        Transaction(person=request.user, withdrawn=True, amount=story.price).save()   # add deduction to transaction history
        wallet.save()

        # send the deducted money into author's wallet
        Wallet.objects.filter(owner=story.author).update(balance = F('balance') + story.price)
        Transaction(person=story.author, withdrawn=False, amount=story.price).save()  # add this to transaction history
        
        # add this story to buyer's userdata
        starting_section = Section.objects.filter(is_starting=True, story=story)
        newdata = Userdata(story=story, user=request.user, section=starting_section[0])
        newdata.save()
        return redirect('stories:my')
    else:
        return HttpResponseNotFound('This story does not exist!')

@login_required
@not_frozen
def story_my(request):
    return render(request, 'stories/my.html', { 'mystories': Userdata.objects.filter(user=request.user) })

@login_required
@not_frozen
@moderator_required
def story_approve(request):
    return render(request, 'stories/approve.html', { 'stories': Story.objects.filter(approved=False) })

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
    return render(request, 'stories/approval-form.html', { 'form': form, 'story': story })

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
        position = Userdata(story=story, user=request.user, section=Section.objects.get(story=story, is_starting=True))
        position.save()
    else:
        return HttpResponseForbidden('You are not allowed to access this story')
    
    links = None
    if not position.section.is_ending:
        links = Sectionlink.objects.filter(fromsection=position.section)
    print(story.title)
    return render(request, 'stories/read.html', { 'fsid': Section.objects.get(is_starting=True, story=story), 'sid': story.id, 'name': story.title, 'section': position.section, 'links': links })

def validateStructure(parsed):
    if 'meta' in parsed and 'sections' in parsed:
        if 'title' in parsed['meta'] and 'summary' in parsed['meta'] and 'price' in parsed['meta'] and isinstance(parsed['sections'], list) :
            return True
    return False


@login_required
@not_frozen
@writer_required
def story_new(request):
    err = None
    print("Here")
    if request.method == 'POST':
        jsonstory = request.POST['jsonfile']
        parsed = parse(jsonstory)
        if parsed is not None and validateStructure(parsed):
            try:
                meta = parsed['meta']
                sections = parsed['sections']
                links = []
                for section in sections:
                    if not section['is_ending']:
                        for linkitem in section['links']:
                            links.append({ 'from': section['position'], 'to': linkitem['to'], 'button': linkitem['button'] })
                story = Story(title=meta['title'], summary=meta['summary'], approved=False, rating=Story.Pg.UNIVERSAL, price=decimal.Decimal(meta['price']), author=request.user)
                story.save()
                sectionList = []
                for section in sections:
                    Section(is_starting=section['is_starting'], is_ending=section['is_ending'], text=section['text'], story=story, storypos=section['position']).save()
                for link in links:
                    Sectionlink(fromsection=Section.objects.get(story=story, storypos=link['from']), tosection=Section.objects.get(story=story, storypos=link['to']), button=link['button']).save()
                return redirect('stories:valid')
            except Exception:
                story.delete()
                err = "Invalid format."
        else:
            err = "Not valid JSON"
    return render(request, 'stories/new.html', { 'err': err })


@login_required
@not_frozen
@writer_required
def story_valid(request):
    return render(request, 'stories/valid.html')

    




