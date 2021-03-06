from django.shortcuts import render
from django.http import HttpResponse
from django.template import RequestContext, loader
from students.models import *
from django.core import serializers
import json


def index(request):
    questions = [row.question for row in Question.objects.all()]
    skills = [row.name for row in Skill.objects.all()]
    template = loader.get_template('index.html')
    context = RequestContext(request, {
        'questions': questions,
        'skills': skills
    })
    return HttpResponse(template.render(context))


"""
List of all students.
[
   "Marina",
   "Natasha",
   "Vika"
]
"""


def students(request):
    #output = serializers.serialize("json", Student.objects.all())
    #output = ', '.join([s.name for s in Student.objects.all()])
    output = []
    for row in Student.objects.all():
        output.append(row.name)
    return HttpResponse(json.dumps(output))
    #return HttpResponse("Hello, world. You're at the poll index.")


"""
Describes a student progress in questions and skills.
{
    "skills": ["memory"],
    "questions": ["What are 2 main types of memory?", "What is a trigger and how it works?", "What physical laws allows to store digital information?", "What is byte and what is processor bit?"]
}
"""


def student_descr(request, name):
    output = dict()
    skills = []
    questions = []
    for row in QuestionsAnswered.objects.filter(student=name):
        questions.append(row.question.id)
    skills = get_skills_for_questions(questions)
    output['skills'] = skills
    output['questions'] = questions
    return HttpResponse(json.dumps(output), content_type="application/json")


"""
List of all skills with parent-child relationship.
[{
    "name": "memory",
    "parent": ["basic_computing"],
    "child": ["caching", "operating_systems"]
}, {
    "name": "processor",
    "parent": ["basic_computing"],
    "child": ["operating_systems"]
}, {
    "name": "operating_systems",
    "parent": ["memory", "processor"],
    "child": []
}, {
    "name": "caching",
    "parent": ["memory"],
    "child": []
}, {
    "name": "basic_computing",
    "parent": [],
    "child": ["memory", "processor"]
}]
"""


def skills(request):
    output = []
    for row in Skill.objects.all():
        skillName = row.name
        skill = dict()
        skill['name'] = skillName
        skill['parent'] = []
        skill['child'] = []
        for parent in SkillsRelationship.objects.filter(child=skillName):
            skill['parent'].append(parent.parent.name)
        for child in SkillsRelationship.objects.filter(parent=skillName):
            skill['child'].append(child.child.name)
        output.append(skill)
    return HttpResponse(json.dumps(output), content_type="application/json")


def skills_page(request):
    skills = []
    for row in Skill.objects.all():
        skills.append(row.name)
    template = loader.get_template('skills.html')
    context = RequestContext(request, {
        'skills': skills
    })
    return HttpResponse(template.render(context))


"""
Description of skill.
{
   "questions":[
      "How processor understands when to perform it's operations?",
      "What is byte and what is processor bit?"
   ],
   "parent":[
      "basic_computing"
   ],
   "child":[
      "operating_systems"
   ]
}
"""


def skill_descr(request, name):
    output = dict()
    child = []
    parent = []
    data = SkillsRelationship.objects.all()
    for row in data:
        if name == row.parent.name:
            child.append(row.child.name)
        if name == row.child.name:
            parent.append(row.parent.name)
    questions = get_questions_for_skill(name)

    output['child'] = child
    output['parent'] = parent
    output['questions'] = questions
    return HttpResponse(json.dumps(output), content_type="application/json")


def skill_page(request, name):
    questions = []
    links = []
    skill = Skill.objects.get(name=name)
    for row in Link.objects.filter(skill=Skill(name)):
        links.append(row.link)
    for row in SkillQuestion.objects.filter(skill=Skill(name)):
        questions.append(row.question)
    template = loader.get_template('skill.html')
    context = RequestContext(request, {
        'skill': skill,
        'questions': questions,
        'links': links
    })
    return HttpResponse(template.render(context))


"""
List of all questions.
[
   "What are 2 main types of memory?",
   "How processor understands when to perform it's operations?",
   "What is a trigger and how it works?",
   "What physical laws allows to store digital information?",
   "What is a register and how does it work?",
   "How summator works, on what basic elements it's based?",
   "Assume you have 1 type logic element A and connection wires. Can you buiild a computer?",
   "What is byte and what is processor bit?"
]
"""


def questions(request):
    output = []
    for q in Question.objects.all():
        item = dict()
        item['question'] = q.question
        item['id'] = q.id
        output.append(item)
    return HttpResponse(json.dumps(output), content_type="application/json")


def questions_page(request):
    milestones = dict()
    for q in Question.objects.all():
        milestoneName = q.milestone.name
        milestoneDate = q.milestone.date
        if not milestones.get(milestoneName):
            milestones[milestoneName] = {
                'questions': [],
                'date': milestoneDate
            }
        milestones[milestoneName]['questions'].append({
            'id': q.id, 'question': q.question
        })
    template = loader.get_template('questions.html')
    context = RequestContext(request, {
        'milestones': milestones
    })
    return HttpResponse(template.render(context))


def roadmap_page(request):
    template = loader.get_template('roadmap.html')
    context = RequestContext(request)
    return HttpResponse(template.render(context))


"""
Description of a question. Currently a list of assosiated skills.
[
   "processor",
   "memory"
]
"""


def question_descr(request, id):
    output = get_skills_for_question(id)
    return HttpResponse(json.dumps(output))


def get_skills_for_questions(questions):
    result = []
    data = SkillQuestion.objects.all()
    skillMap = dict()
    for row in data:
        if not skillMap.has_key(row.skill.name):
            skillMap[row.skill.name] = [row.question.id]
        else:
            skillMap[row.skill.name].append(row.question.id)
    print skillMap
    for skill in skillMap.keys():
        required_questions = skillMap[skill]
        skill_aquired = True
        for rq in required_questions:
            answered = False
            for q in questions:
                if q == rq:
                    answered = True
                    break
            if not answered:
                skill_aquired = False
                break
        if skill_aquired:
            result.append(skill)
    return result


def get_skills_for_question(question):
    result = []
    data = SkillQuestion.objects.all()
    for row in data:
        if question == str(row.question.id):
            result.append(row.skill.name)
    return result


def get_questions_for_skill(skill):
    result = []
    data = SkillQuestion.objects.all()
    for row in data:
        if skill == row.skill.name:
            result.append(row.question.question)
    return result


def answers_page(request):
    questions = []
    for q in Question.objects.all():
        questions.append({
            'id': q.id, 'question': q.question
        })
    template = loader.get_template('answers.html')
    context = RequestContext(request, {
        'questions': questions
    })
    return HttpResponse(template.render(context))


def submit_answered(request, name):
    if request.method == 'POST':
        answered = request.POST['questions'].split(',')
        student = Student.objects.get(name=name)
        for id in answered:
            question = Question.objects.get(id=id)
            qa = QuestionsAnswered(student=student, question=question)
            qa.save()
    return HttpResponse(json.dumps("{ result: 'ok' }"), content_type="application/json")