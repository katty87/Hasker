from .models import Question


def trending_questions(request):
    trending_question_list = Question.objects.all()[:5]
    return {'trending_question_list': trending_question_list}
