from datetime import datetime

import factory

from main.models import Question, Tag, QuestionVote, Answer
from user.tests.fixtures import UserFactory


class TagFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Tag

    name = factory.Sequence(lambda n: "tag%s" % n)


class QuestionVoteFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = QuestionVote

    value = 1
    user = factory.SubFactory(UserFactory)


class QuestionFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Question

    header = factory.Sequence(lambda n: 'How to do thing %s?' % n)
    content = factory.Sequence(lambda n: 'I want to do thing #%s but I am stuck. Can anybody help me?' % n)
    user = factory.SubFactory(UserFactory)
    create_date = factory.LazyFunction(datetime.now)

    @factory.post_generation
    def tags(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for tag in extracted:
                self.tags.add(tag)


class AnswerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Answer

    content = factory.Sequence(lambda n: 'Answer content #%s' % n)
    user = factory.SubFactory(UserFactory)
    create_date = factory.LazyFunction(datetime.now)
    is_correct = False

