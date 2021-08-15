from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect
from django.views.generic import DetailView
from Agah.forms import Interviewer_form, Answersheet_form, Responder_form, Question_form, Brand_form
from Agah.models import Survey, Question, AnswerSheet, Interviewer, Limit, Answer, Child, Option
from django.contrib import messages


class Survey_View(DetailView):
    model = Survey
    template_name = 'Survey.html'
    context_object_name = 'Survey'


@csrf_protect
def Personal(request, pk):
    answersheet = request.session.get('answersheet', None)
    survey = get_object_or_404(Survey, pk=pk)
    Q1 = get_object_or_404(Question, previous_question=None)
    if request.method == 'GET':
        if answersheet is None:
            interviewer_frm = Interviewer_form(request.GET)
            answersheet_frm = Answersheet_form(request.GET)
            responder_frm = Responder_form(request.GET)
        else:
            import jdatetime
            answersheet = get_object_or_404(AnswerSheet, pk=answersheet)
            answersheet.date = str(
                jdatetime.date.fromgregorian(year=answersheet.date.year, month=answersheet.date.month,
                                             day=answersheet.date.day))
            #
            interviewer_frm = Interviewer_form(request.POST, instance=answersheet.interviewer)
            answersheet_frm = Answersheet_form(request.POST, instance=answersheet)
            responder_frm = Responder_form(request.POST, instance=answersheet.responser)
        context = {'survey': survey, 'interviewer_frm': interviewer_frm, 'answersheet_frm': answersheet_frm,
                   'responder_frm': responder_frm, 'Q1': Q1}
        return render(request=request, template_name='Personal.html', context=context)
    else:
        if answersheet is None:
            interviewer_frm = Interviewer_form(request.POST)
            answersheet_frm = Answersheet_form(request.POST)
            responder_frm = Responder_form(request.POST)
            if interviewer_frm.is_valid() and answersheet_frm.is_valid() and responder_frm.is_valid():
                interviwer = get_object_or_404(Interviewer, code=interviewer_frm.cleaned_data.get('code'))
                responder = responder_frm.save()
                answersheet = answersheet_frm.save(commit=False)
                answersheet.responser = responder
                answersheet.survey = survey
                answersheet.interviewer = interviwer
                answersheet.save()
            else:
                context = {'survey': survey, 'interviewer_frm': interviewer_frm, 'answersheet_frm': answersheet_frm,
                           'responder_frm': responder_frm, 'Q1': Q1}
                return render(request=request, template_name='Personal.html', context=context)
        else:
            answersheet = get_object_or_404(AnswerSheet, pk=answersheet)
            interviewer_frm = Interviewer_form(request.POST)
            answersheet_frm = Answersheet_form(request.POST)
            responder_frm = Responder_form(request.POST)
            if interviewer_frm.is_valid() and answersheet_frm.is_valid() and responder_frm.is_valid():
                if answersheet_frm.has_changed():
                    answersheet.date = answersheet_frm.cleaned_data.get('date')
                    answersheet.day = answersheet_frm.cleaned_data.get('day')
                    answersheet.save()
                if interviewer_frm.has_changed():
                    answersheet.interviewer_id = interviewer_frm.cleaned_data.get('code')
                    answersheet.interviewer.save()
                if responder_frm.has_changed():
                    answersheet.responser.firstname = responder_frm.cleaned_data.get('firstname')
                    answersheet.responser.lastname = responder_frm.cleaned_data.get('lastname')
                    answersheet.responser.mobile = responder_frm.cleaned_data.get('mobile')
                    answersheet.responser.city_id = responder_frm.cleaned_data.get('city')
                    answersheet.responser.save()
        request.session['answersheet'] = answersheet.pk
        request.session['survey'] = survey.pk  # todo: should i delete?
        request.session['question'] = Q1.next_question.pk  # todo: should i delete?
        return redirect(reverse('agah:social'))


def interviwer_name(request):
    if request.method == 'GET' and request.is_ajax:
        try:
            interviwer = get_object_or_404(Interviewer, code=int(request.GET.get('code')))
        except:
            context = {}
            return JsonResponse(context, status=404)
        else:
            context = {'name': interviwer.name}
        return JsonResponse(context, status=200)


def check_age(age):
    if 18 <= age <= 24:
        return 1
    elif 25 <= age <= 29:
        return 2
    elif 30 <= age <= 34:
        return 3
    elif 35 <= age <= 39:
        return 4
    elif 40 <= age <= 44:
        return 5
    elif 45 <= age <= 49:
        return 6
    elif 50 <= age <= 54:
        return 7
    elif 55 <= age <= 59:
        return 8
    elif 60 <= age < 64:
        return 9
    else:
        return 0


@csrf_protect
def Social(request):
    answersheet = request.session.get('answersheet')
    try:
        answersheet = get_object_or_404(AnswerSheet, pk=answersheet)
    except:
        survey = get_object_or_404(Survey, title='پلتفرم‌های آنلاین')
        messages.info(request=request, message='شما پرسشنامه فعال ندارید')
        return redirect(reverse('agah:survey', args=[survey.pk]))
    Q2 = get_object_or_404(Question, pk=request.session['question'])
    Q3 = Q2.next_question
    Q4 = Q3.next_question
    Q4_1 = Q4.next_question
    T1 = Q4_1.next_question
    T2 = T1.next_question
    T3 = T2.next_question
    if request.method == 'GET':
        form = Question_form(request.GET,
                             instance={'Q2': Q2, 'Q3': Q3, 'Q4': Q4, 'Q4_1': Q4_1, 'T1': T1, 'T2': T2, 'T3': T3,
                                       'regions': T3.regions.filter(city=answersheet.responser.city)})
        context = {'Q2': Q2, 'Q3': Q3, 'Q4': Q4, 'Q4_1': Q4_1, 'T1': T1, 'T2': T2, 'T3': T3, 'answersheet': answersheet,
                   'form': form}
        return render(request, 'Social.html', context)
    else:
        marital_status = int(request.POST.get('marital_status'))
        age = int(request.POST.get('age'))
        age_category = check_age(age)
        del age
        if marital_status == 0 or age_category == 0:
            answersheet.delete()
            messages.info(request=request, message=('به علت عدم پاسخ به وضعيت تاهل نظرسنجی به اتمام رسید.'))
            return redirect(reverse('agah:survey', args=[answersheet.survey.pk]))
        if Limit.objects.filter(marital_status=marital_status, age=age_category).exists():
            limit = Limit.objects.get(marital_status=marital_status, age=age_category)
            if not answersheet.answers.filter(question__code='Q2').exists():
                if not limit.check_for_capacity():
                    answersheet.delete()
                    messages.info(request=request, message=('به علت اتمام ظرفیت گروه سنی نظرسنجی به اتمام رسید.'))
                    return redirect(reverse('agah:survey', args=[answersheet.survey.pk]))

        # Q2 save answer...
        answer = None
        if Answer.objects.filter(question=Q2, answersheet=answersheet).exists():
            answer = Answer.objects.get(question=Q2, answersheet=answersheet)
            answer.option = Q2.options.get(value=age_category)
            answer.point = Q2.options.get(value=age_category).point
        else:
            answer = Answer(question=Q2, answersheet=answersheet,
                            point=Q2.options.get(value=age_category).point,
                            option=Q2.options.get(value=age_category))
        answer.save()

        # Q3 save answer...
        if Answer.objects.filter(question=Q3, answersheet=answersheet).exists():
            answer = Answer.objects.get(question=Q3, answersheet=answersheet)
            if answer.answer != marital_status:
                Child.objects.filter(responder=answersheet.responser).delete()
            answer.option = Q3.options.get(value=marital_status)
            answer.point = Q3.options.get(value=marital_status).point
        else:
            answer = Answer(question=Q3, answersheet=answersheet, option=Q3.options.get(value=marital_status),
                            point=Q3.options.get(value=marital_status).point)
        answer.save()

        # Q4 save answer...
        number_of_child = request.POST.get('number_of_child', 0)
        if number_of_child == '':
            number_of_child = 0
        if Answer.objects.filter(question=Q4, answersheet=answersheet).exists():
            answer = Answer.objects.get(question=Q4, answersheet=answersheet)
            Child.objects.filter(responder=answersheet.responser).delete()
            answer.answer = int(number_of_child)
            answer.point = 0
        else:
            answer = Answer(question=Q4, answersheet=answersheet, answer=int(number_of_child), point=0)
        answer.save()

        # T1 save answer...
        home = request.POST.get('home')
        if Answer.objects.filter(question=T1, answersheet=answersheet).exists():
            answer = Answer.objects.get(question=T1, answersheet=answersheet)
            answer.option = T1.options.get(value=home)
            answer.point = T1.options.get(value=home).point
        else:
            answer = Answer(question=T1, answersheet=answersheet, option=T1.options.get(value=home),
                            point=T1.options.get(value=home).point)
        answer.save()

        # T2 save answer...
        job = request.POST.get('job')
        if Answer.objects.filter(question=T2, answersheet=answersheet).exists():
            answer = Answer.objects.get(question=T2, answersheet=answersheet)
            answer.answer = job
            answer.option = T2.options.get(value=job)
            answer.point = T2.options.get(value=job).point
        else:
            answer = Answer(question=T2, answersheet=answersheet, option=T2.options.get(value=job),
                            point=T2.options.get(value=job).point)
        answer.save()

        # T3 save answer...
        region = request.POST.get('region')
        if Answer.objects.filter(question=T3, answersheet=answersheet).exists():
            answer = Answer.objects.get(question=T3, answersheet=answersheet)
            answer.answer = region
            answer.point = T3.regions.get(value=region, city=answersheet.responser.city).point
        else:
            answer = Answer(question=T3, answersheet=answersheet,
                            answer=region,
                            point=T3.regions.get(value=region, city=answersheet.responser.city).point)
        answer.save()

        # T4_1 save answer...
        if int(number_of_child) > 0:
            if int(number_of_child) >= 1:
                first_child_year = int(request.POST.get('first_child_year'))
                first_child_gender = Q4_1.options.get(value=int(request.POST.get('first_child_gender')))
                first_child_age = int(request.POST.get('first_child_age'))
                child = Child(responder=answersheet.responser, gender=first_child_gender,
                              birthday_year=first_child_year,
                              age=first_child_age)
                child.save()

            if int(number_of_child) >= 2:
                second_child_year = int(request.POST.get('second_child_year'))
                second_child_gender = Q4_1.options.get(value=int(request.POST.get('second_child_gender')))
                second_child_age = int(request.POST.get('second_child_age'))
                child = Child(responder=answersheet.responser, gender=second_child_gender,
                              birthday_year=second_child_year,
                              age=second_child_age)
                child.save()
            if int(number_of_child) >= 3:
                third_child_year = int(request.POST.get('third_child_year'))
                third_child_gender = Q4_1.options.get(value=int(request.POST.get('third_child_gender')))
                third_child_age = int(request.POST.get('third_child_age'))
                child = Child(responder=answersheet.responser, gender=third_child_gender,
                              birthday_year=third_child_year,
                              age=third_child_age)
                child.save()

        answersheet.calculate_total_point()
        return redirect(reverse('agah:brand'))


@csrf_protect
def Brand(request):
    answersheet = request.session.get('answersheet')
    try:
        answersheet = get_object_or_404(AnswerSheet, pk=answersheet)
    except:
        survey = get_object_or_404(Survey, title='پلتفرم‌های آنلاین')
        messages.info(request=request, message='شما پرسشنامه فعال ندارید')
        return redirect(reverse('agah:survey', args=[survey.pk]))
    A1 = Question.objects.get(code='A1')
    A2 = Question.objects.get(code='A2')
    A4 = Question.objects.get(code='A4')
    A6 = Question.objects.get(code='A6')
    A7 = Question.objects.get(code='A7')
    A8 = Question.objects.get(code='A8')
    A9 = Question.objects.get(code='A9')
    A10 = Question.objects.get(code='A10')
    A11 = Question.objects.get(code='A11')
    A12 = Question.objects.get(code='A12')
    if request.method == 'GET':
        A1_form = Brand_form(request.GET, instance={'brands': A1.options.all(), 'question': A1})
        A2_form = Brand_form(request.GET, instance={'brands': A1.options.all(), 'question': A2})
        A4_form = Brand_form(request.GET, instance={'brands': A1.options.all(), 'question': A4})
        A6_form = Brand_form(request.GET, instance={'brands': A1.options.all(), 'question': A6})
        A7_form = Brand_form(request.GET, instance={'brands': A1.options.all(), 'question': A7})
        A8_form = Brand_form(request.GET, instance={'brands': A1.options.all(), 'question': A8})
        A9_form = Brand_form(request.GET, instance={'brands': A1.options.all(), 'question': A9})
        A10_form = Brand_form(request.GET, instance={'brands': A1.options.all(), 'question': A10})
        A11_form = Brand_form(request.GET, instance={'brands': A1.options.all(), 'question': A11})
        A12_form = Brand_form(request.GET, instance={'brands': A1.options.all(), 'question': A12})
        context = {'A1': A1, 'A1_form': A1_form,
                   'A2': A2, 'A2_form': A2_form,
                   'A4': A4, 'A4_form': A4_form,
                   'A6': A6, 'A6_form': A6_form,
                   'A7': A7, 'A7_form': A7_form,
                   'A8': A8, 'A8_form': A8_form,
                   'A9': A9, 'A9_form': A9_form,
                   'A10': A10, 'A10_form': A10_form,
                   'A11': A11, 'A11_form': A11_form,
                   'A12': A12, 'A12_form': A12_form,
                   }
        return render(request, '../templates/Brand.html', context=context)
    else:
        A1_answer = request.POST.get('A1')
        A2_answer = request.POST.getlist('A2')
        A4_answer = request.POST.getlist('A4')
        A6_answer = request.POST.getlist('A6')
        A7_answer = [request.POST.get(item) for item in request.POST if item.startswith('A7')]
        A8_answer = [request.POST.get(item) for item in request.POST if item.startswith('A8')]
        A9_answer = [request.POST.get(item) for item in request.POST if item.startswith('A9')]
        A10_answer = [request.POST.get(item) for item in request.POST if item.startswith('A10')]
        A11_answer = [request.POST.get(item) for item in request.POST if item.startswith('A11')]
        A12_answer = [request.POST.get(item) for item in request.POST if item.startswith('A12')]
        # todo:save if first  edit if is second
        # A1 save
        if answersheet.answers.filter(question=A1).exists():
            answer = answersheet.answers.get(question=A1)
            answer.option = A1.options.get(value=int(A1_answer))
        else:
            answer = Answer(point=0, answersheet=answersheet, question=A1, option=A1.options.get(value=int(A1_answer)))
        answer.save()
        # A2 save
        if answersheet.answers.filter(question=A2).exists():
            answers = answersheet.answers.filter(question=A2)
            answers.delete()
        for item in A2_answer:
            answer = Answer(point=0, answersheet=answersheet, question=A2, option=A1.options.get(value=int(item)))
            answer.save()
        # A4 save
        if answersheet.answers.filter(question=A4).exists():
            answers = answersheet.answers.filter(question=A4)
            answers.delete()
        for item in A4_answer:
            answer = Answer(point=0, answersheet=answersheet, question=A4, option=A1.options.get(value=int(item)))
            answer.save()
        # A6
        if answersheet.answers.filter(question=A6).exists():
            answers = answersheet.answers.filter(question=A6)
            answers.delete()
        for item in A6_answer:
            answer = Answer(point=0, answersheet=answersheet, question=A6, option=A1.options.get(value=int(item)))
            answer.save()
        # A7
        if answersheet.answers.filter(question=A7).exists():
            answers = answersheet.answers.filter(question=A7)
            answers.delete()
        for i in range(0, len(A7_answer)):
            answer = Answer(point=0, answersheet=answersheet, question=A7,
                            option=A1.options.get(value=int(A6_answer[i])), answer=A7_answer[i])
            answer.save()
        # A8
        if answersheet.answers.filter(question=A8).exists():
            answers = answersheet.answers.filter(question=A8)
            answers.delete()
        for i in range(0, len(A8_answer)):
            answer = Answer(point=0, answersheet=answersheet, question=A8,
                            option=A1.options.get(value=int(A6_answer[i])), answer=A8_answer[i])
            answer.save()
        # A9
        if answersheet.answers.filter(question=A9).exists():
            answers = answersheet.answers.filter(question=A9)
            answers.delete()
        for i in range(0, len(A9_answer)):
            answer = Answer(point=0, answersheet=answersheet, question=A9,
                            option=A1.options.get(value=int(A6_answer[i])), answer=A9_answer[i])
            answer.save()
        # A10
        if answersheet.answers.filter(question=A10).exists():
            answers = answersheet.answers.filter(question=A10)
            answers.delete()
        for i in range(0, len(A10_answer)):
            answer = Answer(point=0, answersheet=answersheet, question=A10,
                            option=A1.options.get(value=int(A6_answer[i])), answer=A10_answer[i])
            answer.save()
        # A11
        if answersheet.answers.filter(question=A11).exists():
            answers = answersheet.answers.filter(question=A11)
            answers.delete()
        for i in range(0, len(A11_answer)):
            answer = Answer(point=0, answersheet=answersheet, question=A11,
                            option=A1.options.get(value=int(A6_answer[i])), answer=A11_answer[i])
            answer.save()
        # A12
        if answersheet.answers.filter(question=A12).exists():
            answers = answersheet.answers.filter(question=A12)
            answers.delete()
        for i in range(0, len(A12_answer)):
            answer = Answer(point=0, answersheet=answersheet, question=A12,
                            option=A1.options.get(value=int(A4_answer[i])), answer=A12_answer[i])
            answer.save()
        pass
