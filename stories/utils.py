from datetime import date

from .models import Story

import json


def pg_group(age):
    ''' Determines the Parental Guidance group from age '''
    if age >= 18:
        return Story.Pg.ADULT
    elif age >= 12:
        return Story.Pg.ADOLESCENT
    else:
        return Story.Pg.UNIVERSAL


def calculate_age(born):
    ''' Calculates age of a person in years given date of birth in datetime.date format  '''
    today = date.today()
    return today.year - born.year - ((today.month, today.day) < (born.month, born.day))


def parseJson(file):
    ''' Converts and returns JSON formatted as Python Dictionaries if possible, else returns Nones '''
    try:
        return json.loads(file)
    except ValueError as e:
        return None


def extractLinks(sections):
    ''' Extracts Linking metadata from a list of Sections 
    
    Takes a list of sections in Dictionary format and outputs a List of "Sectionlinks"
    of the form {'from', 'to', 'button'}.
    '''
    links = []
    for section in sections:
        for linkitem in section['links']:
            links.append(
                {'from': section['position'], 'to': linkitem['to'], 'button': linkitem['button']})
    return links


def countStartingSections(sections):
    ''' Counts the number of sections with is_starting attribute set to True from a List of Sections '''
    starting_sections = 0
    for section in sections:
        if section['is_starting']:
            starting_sections += 1
    return starting_sections
