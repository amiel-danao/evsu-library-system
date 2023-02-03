from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Div, Field
from crispy_bootstrap5.bootstrap5 import FloatingField
from dal import autocomplete
from django.utils.translation import gettext as _
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from system.context_processors import MOBILE_NO_REGEX
from .models import SMS, CustomUser
from django import forms
from evsu_library.managers import CustomUserManager
from system.models import Book, BookInstance, IncomingTransaction, OutgoingTransaction, Student

class BookInstanceForm(forms.ModelForm):
    class Meta:
        model = BookInstance
        fields = '__all__'
        exclude = ()

class OutgoingTransactionForm(forms.ModelForm):

    book = forms.CharField()
    borrower = forms.CharField()

    class Meta:
        model = OutgoingTransaction
        fields = '__all__'
        exclude = ()
        widgets = {
            'return_date': forms.widgets.DateInput(attrs={'type': 'date', 'class': 'restricted_today_date'}), 
        }

    def clean_book(self):
        data = self.cleaned_data['book']

        try:
            book = BookInstance.objects.get(id=data)
            if book.status == 'o':
                raise ValidationError(f'{book.book.title} is currently borrowed!')
            return book
        except Student.DoesNotExist as error:
            raise ValidationError(f'Book with id {data} doesn\'t exist!')

    def clean_borrower(self):
        data = self.cleaned_data['borrower']

        try:
            return Student.objects.get(school_id=data)
        except Student.DoesNotExist as error:
            raise ValidationError(f'Student with id {data} doesn\'t exist!')
        except ValidationError as error:
            raise ValidationError(f'Student with id {data} doesn\'t exist!')

        # Check some condition over data
        # raise ValidationError for bad results
        # else return data

class IncomingTransactionForm(forms.ModelForm):

    # borrower = forms.CharField()

    class Meta:
        model = IncomingTransaction
        fields = '__all__'
        exclude = ('date_returned', 'borrower')

    # def clean_borrower(self):

    #     try:
    #         id = self.cleaned_data['book']
    #         if id is None:
    #             raise ValidationError(f'book with id {id} not found!')
    #         outgoing = OutgoingTransaction.objects.filter(id=id).latest()
    #         return outgoing.borrower
    #     except Student.DoesNotExist as error:
    #         raise ValidationError(f'book with id {id} error!')
    #     except ValidationError as error:
    #         raise ValidationError(f'book with id {id} error!')






class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ("email", "password1", "password2")

    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class StudentProfileForm(forms.ModelForm):

    school_id = forms.RegexField(
        required=False,
        regex='^(?:\d{4}-\d{5})$',
        error_messages = {'invalid': _("Please input a valid Student Id No pattern: YYYY-xxxxx")}, label='Student Id No.')

    mobile_no = forms.RegexField(
        required=True,
        regex=MOBILE_NO_REGEX,
        error_messages = {'invalid': _("Please input a valid mobile number")}, label='Mobile No.')

    address = forms.CharField(widget=forms.Textarea())

    email = forms.EmailField(required=False)

    def __init__(self, *args, **kwargs):
        super(StudentProfileForm, self).__init__(*args, **kwargs)
        self.fields['email'].disabled = True
        self.fields['school_id'].disabled = True

    class Meta:
        model = Student
        fields = '__all__'
        exclude = ('user', 'qualified')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div(
                Div(FloatingField('email', readonly=True, disabled=True, required=False), css_class='col-6 rounded',),
                Div(FloatingField('school_id', readonly=True, disabled=True, required=False), css_class='col-6 rounded',),
                css_class='row mb-2',
            ),
            Div(
                Div(FloatingField('first_name'), css_class='col-4 rounded',),
                Div(FloatingField('middle_name'), css_class='col-4 rounded',),
                Div(FloatingField('last_name'), css_class='col-4 rounded',),
                css_class='row mb-2',
            ),
            Div(
                Div(FloatingField('gender', css_class='w-100'), css_class='col-4 rounded',),
                Div(FloatingField('section'), css_class='col-4 rounded',),
                Div(FloatingField('year', css_class='w-100'), css_class='col-4 rounded',),
                css_class='row mb-2',
            ),
            Div(
                Div(FloatingField('address'), css_class='col-6 rounded',),
                Div(FloatingField('mobile_no'), css_class='col-6 rounded',),
                css_class='row mb-2',
            ),
            Submit('submit', 'Update'),
        )



class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email', required=True)

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                _("Please confirm your email so you can log in."),
                code='inactive',
            )

MYCHOICES = ((1,1), (2,2))

class SMSForm(forms.ModelForm):
    # recepients = forms.Field(widget=autocomplete.ListSelect2(url='system:student-autocomplete'))
    message = forms.CharField(widget=forms.Textarea(attrs={"rows":6, "maxlength":150}), required=True)
    recepients = forms.CharField(widget=forms.TextInput(attrs={"hidden":""}), required=False)

    class Meta:
        model = SMS
        exclude = ()
        widgets = {
            'students': autocomplete.ModelSelect2Multiple(url='system:student-autocomplete')
        }


class BookIssuanceForm(forms.ModelForm):
    # recepients = forms.Field(widget=autocomplete.ListSelect2(url='system:student-autocomplete'))
    # message = forms.CharField(widget=forms.Textarea(attrs={"rows":6, "maxlength":150}), required=True)
    # borrower = forms.CharField(widget=forms.TextInput(), required=True)

    # class Meta:
    #     model = OutgoingTransaction
    #     fields = ('book', 'borrower', 'date_borrowed', 'return_date')
    #     widgets = {
    #         'borrower': autocomplete.ModelSelect2(url='system:student-autocomplete')
    #     }

    class Meta:
        model = OutgoingTransaction
        fields = '__all__'
        widgets = {
            'borrower': autocomplete.ModelSelect2(url='system:student-autocomplete')
        }

    def clean(self):
        cleaned_data = super(BookIssuanceForm, self).clean()
        if self.instance.pk is not None:
            return cleaned_data
        book = self.cleaned_data.get('book')
        
        if book.inventory_stock <= 0:
            self.add_error('book', 'Book has zero inventory stock!')
            # raise forms.ValidationError('Book has zero inventory stock!')
        # return cleaned_data



class MyCrispyForm(forms.ModelForm):


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        # self.helper.form_id = 'id-my-form'
        self.helper.form_class = 'form-control'
        # self.helper.form_method = 'post'
        # self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = Book
        # See note here: https://docs.djangoproject.com/en/1.10/ref/contrib/admin/#django.contrib.admin.ModelAdmin.form
        fields = []