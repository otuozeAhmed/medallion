from django.http import Http404
from django.urls import reverse_lazy, reverse
from django.utils.text import capfirst
from django.utils.translation import gettext, gettext_lazy as _
from django.views.generic.list import ListView
from django.views.generic.edit import FormMixin
from django.views.generic.detail import DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages

from djf_surveys.models import Survey, UserAnswer
from djf_surveys.forms import CreateSurveyForm, EditSurveyForm
from djf_surveys.mixin import ContextTitleMixin
from djf_surveys import app_settings
from djf_surveys.utils import NewPaginator


@method_decorator(login_required, name='dispatch')
class SurveyListView(ContextTitleMixin, ListView):
    model = Survey
    title_page = 'Survey List'
    paginate_by = app_settings.SURVEY_PAGINATION_NUMBER['survey_list']
    paginator_class = NewPaginator

    def get_queryset(self):
        query = self.request.GET.get('q')
        user = self.request.user
        object_list = self.model.objects.all()

        for survey in object_list:
            survey.user_has_answered = user in survey.answered_by.all()

        if query:
            object_list = object_list.filter(name__icontains=query)

        return object_list

    def get_context_data(self, **kwargs):
        page_number = self.request.GET.get('page', 1)
        context = super().get_context_data(**kwargs)
        page_range = context['page_obj'].paginator.get_elided_page_range(number=page_number)
        context['page_range'] = page_range
        return context


class SurveyFormView(FormMixin, DetailView):
    template_name = 'djf_surveys/form.html'
    success_url = reverse_lazy("djf_surveys:index")

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        self.object = self.get_object()
        if form.is_valid():
            form.save()
            messages.success(self.request, gettext("%(page_action_name)s successfully.") % dict(page_action_name=capfirst(self.title_page.lower())))
            return self.form_valid(form)
        else:
            messages.error(self.request, gettext("Something went wrong."))
            return self.form_invalid(form)


class CreateSurveyFormView(ContextTitleMixin, SurveyFormView):
    model = Survey
    form_class = CreateSurveyForm
    success_url = reverse_lazy("djf_surveys:index")
    title_page = _("Nomination Added")

    def dispatch(self, request, *args, **kwargs):
        survey = self.get_object()
        # Check if the user has already answered the survey
        user_answer = UserAnswer.objects.filter(survey=survey, user=request.user).first()
        if not request.user.is_authenticated and not survey.can_anonymous_user:
            messages.warning(request, gettext("Sorry, you must be logged in to fill out the survey."))
            return redirect("djf_surveys:index")
        
        # Check if the user has already answered the survey
        if user_answer:
            messages.warning(request, gettext("You have already nominated for this category."))
            return redirect("djf_surveys:index")
        
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        return form_class(survey=self.get_object(), user=self.request.user, **self.get_form_kwargs())

    def get_title_page(self):
        return self.get_object().name

    def get_sub_title_page(self):
        return self.get_object().description


@method_decorator(login_required, name='dispatch')
class EditSurveyFormView(ContextTitleMixin, SurveyFormView):
    form_class = EditSurveyForm
    title_page = "Edited Nomination"
    model = UserAnswer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object().survey
        return context

    def dispatch(self, request, *args, **kwargs):
        # handle if user not same
        user_answer = self.get_object()
        if user_answer.user != request.user or not user_answer.survey.editable:
            messages.warning(request, gettext("You can't edit this survey. You don't have permission."))
            return redirect("djf_surveys:index")
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, form_class=None):
        if form_class is None:
            form_class = self.get_form_class()
        user_answer = self.get_object()
        return form_class(user_answer=user_answer, **self.get_form_kwargs())

    def get_title_page(self):
        return self.get_object().survey.name

    def get_sub_title_page(self):
        return self.get_object().survey.description


@method_decorator(login_required, name='dispatch')
class DeleteSurveyAnswerView(DetailView):
    model = UserAnswer

    def dispatch(self, request, *args, **kwargs):
        user_answer = self.get_object()
        survey = user_answer.survey

        # Check if the user is the owner of the survey or a superuser
        if user_answer.user != request.user and not request.user.is_superuser:
            messages.warning(request, gettext("You can't delete this survey. You don't have permission."))
            return redirect("djf_surveys:index")

        user_answer.delete()
        messages.success(self.request, gettext("Nomination successfully deleted."))

        # After deletion, redirect to the survey's detail page if the user is the owner
        if request.user == survey.user:
            return redirect("djf_surveys:detail", slug=survey.slug)
        else:
            return redirect("djf_surveys:index")


    def get(self, request, *args, **kwargs):
        user_answer = self.get_object()
        user_answer.delete()
        messages.success(self.request, gettext("Answer succesfully deleted."))
        return redirect("djf_surveys:detail", slug=user_answer.survey.slug)


class DetailSurveyView(ContextTitleMixin, DetailView):
    model = Survey
    template_name = "djf_surveys/answer_list.html"
    title_page = "Survey Detail"
    paginate_by = app_settings.SURVEY_PAGINATION_NUMBER['answer_list']

    def dispatch(self, request, *args, **kwargs):
        survey = self.get_object()

        # Check if the user is the owner of the survey or a superuser
        if False:
            messages.warning(request, gettext("You can't access this page. You don't have permission."))
            return redirect("djf_surveys:index")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        user = self.request.user
        survey = self.get_object()

        # Filter user's answers for this survey
        user_answers = UserAnswer.objects.filter(survey=survey, user=user) \
            .select_related('user').prefetch_related('answer_set__question')

        paginator = NewPaginator(user_answers, self.paginate_by)
        page_number = self.request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)
        page_range = paginator.get_elided_page_range(number=page_number)

        context = super().get_context_data(**kwargs)
        context['page_obj'] = page_obj
        context['page_range'] = page_range

        return context



@method_decorator(login_required, name='dispatch')
class DetailResultSurveyView(ContextTitleMixin, DetailView):
    title_page = _("Survey Result")
    template_name = "djf_surveys/detail_result.html"
    model = UserAnswer

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object'] = self.get_object()
        context['on_detail'] = True
        return context

    def dispatch(self, request, *args, **kwargs):
        user_answer = self.get_object()

        # Check if the user is the owner of the survey, a superuser, or the user who submitted the answer
        if not request.user.is_superuser and user_answer.user != request.user:
            messages.warning(request, gettext("You can't access this page. You don't have permission."))
            return redirect("djf_surveys:index")

        return super().dispatch(request, *args, **kwargs)

    def get_title_page(self):
        return self.get_object().survey.name

    def get_sub_title_page(self):
        return self.get_object().survey.description



def share_link(request, slug):
    # this func to handle link redirect to create form or edit form
    survey = get_object_or_404(Survey, slug=slug)
    if request.user.is_authenticated:
        user_answer = UserAnswer.objects.filter(survey=survey, user=request.user).last()
        if user_answer:
            return redirect(reverse_lazy("djf_surveys:edit", kwargs={'pk': user_answer.id}))
    return redirect(reverse_lazy("djf_surveys:create", kwargs={'slug': survey.slug}))


def home(request):
    return render(request, 'djf_surveys/home.html')


def redirect_error_page(request):
    return redirect('djf_surveys:home')