from django.conf.urls import patterns, url

from students import views

urlpatterns = patterns('',
	url(r'^$', views.index, name='index'),
    url(r'^students$', views.students, name='students'),
    url(r'^student/(?P<name>[a-zA-Z]+)', views.student_descr, name='student_descr'),
    url(r'^skills.json', views.skills, name='skills'),
    url(r'^skills', views.skills_page, name='skills_page'),
    url(r'^skill/(?P<name>[a-zA-Z_-]+).json', views.skill_descr, name='skill_descr'),
    url(r'^skill/(?P<name>[a-zA-Z_-]+)', views.skill_page, name='skill_page'),
    url(r'^questions.json', views.questions, name='questions'),
    url(r'^questions', views.questions_page, name='questions_page'),
    url(r'^question/(?P<id>\d+)', views.question_descr, name='question_descr'),
    url(r'^roadmap$', views.roadmap_page, name='roadmap_page'),
    url(r'^answers$', views.answers_page, name='answers_page'),
    url(r'^answered/(?P<name>[a-zA-Z]+)$', views.submit_answered, name='submit_answered')
)