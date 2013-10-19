"""Forms."""

import json
from django import forms
from django.forms.models import modelformset_factory, modelform_factory
from django.forms.widgets import HiddenInput
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from student_manager import models


class StudentForm(forms.ModelForm):

    class Meta:
        model = models.Student
        exclude = ('modulo_matrikel',)

    def clean_matrikel(self):
        student_id = self.instance.id  if self.instance else None
        matrikel = self.cleaned_data['matrikel']
        models.validate_matrikel(matrikel, student_id)
        return matrikel


class MasterExamForm(forms.ModelForm):
    class Meta:
        model = models.MasterExam

    def clean_mark_limits(self):
        mark_limits_str = self.cleaned_data['mark_limits']
        if mark_limits_str:
            try:
                mark_limits = json.loads(mark_limits_str)
                if type(mark_limits) != list:
                    raise ValueError
                for entry in mark_limits:
                    if type(entry) != list or len(entry) != 2:
                        raise ValueError
            except ValueError:
                raise ValidationError('Expect list of point-mark-tuples')
        return mark_limits_str


class ExamForm(forms.ModelForm):
    class Meta:
        model = models.Exam
        exclude = ('mark', 'final_mark')


ExamFormSet = modelformset_factory(
    models.Exam,
    form=modelform_factory(models.Exam, fields=('points',)),
    extra=0)


class NumberExercisesForm(forms.Form):
    num_exercises = forms.IntegerField(widget=HiddenInput)


class ImportExercisesForm(forms.Form):
    group = forms.IntegerField(required=False)
    column_separator = forms.CharField(max_length=1, initial=';')
    csv_file = forms.FileField(label=_('CSV file'))
    format = forms.ChoiceField(choices=(
            ('', 'Please select'),
            (1, 'Exercise table (one entry per exercise)'),
            (2, 'Big table (one column per sheet)')))


class ImportStudentsForm(forms.Form):
    column_separator = forms.CharField(max_length=1, initial=';')
    csv_file = forms.FileField(label=_('CSV file'))


class PrintStudentsOptForm(forms.Form):
    matrikel = forms.ChoiceField(label=_('Selection'),
                                 choices=(('on', 'Students with matrikel'),
                                          ('', 'Students without matrikel')),
                                 initial='on')
    total = forms.BooleanField(label=_('Display total/bonus columns'))


class ImportExamsForm(forms.Form):
    examnr = forms.ModelChoiceField(
        label='Exam number', 
        queryset=models.MasterExam.objects.all())
    file = forms.FileField(label=_('File'))


class PrintExamsOptForm(forms.Form):
    examnr = forms.ModelChoiceField(
        label='Exam number', 
        queryset=models.MasterExam.objects.all())
    format = forms.ChoiceField(
        choices=(('exam_obscured', 'seat list - with obscured matrikel'),
                 ('exam_full', 'seat list - with full data'),
                 ('result_obscured', 'result list - with obscured matrikel'),
                 ('result_full', 'result list - with full data')))


class QueryExamsOptForm(forms.Form):
    examnr = forms.ModelChoiceField(
        label='Exam number', 
        queryset=models.MasterExam.objects.all())


class ImportRegistrationsForm(forms.Form):
    file = forms.FileField(label=_('CSV or Wusel XLS file'))
    csv_separator = forms.CharField(max_length=1, initial=';')
    update_choice = forms.ChoiceField(
        label='Update data for existing students?',
        choices=(('none', "don't update existing data"),
                 ('stud', 'update only student data'),
                 ('regist', 'update only registration data'),
                 ('all', 'update student and registration data'))
        )
    import_choice = forms.ChoiceField(
        label='Import data for new students?',
        choices=(('none', "don't import new data"),
                 ('stud', 'import only student data'),
                 ('all', 'import student and registration data'))
        )

