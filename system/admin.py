from django.utils.html import strip_tags
from smtplib import SMTPDataError
from django.contrib import messages #import messages
from django.core.mail import send_mail
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from django.contrib import admin
from django.apps import apps
from django.contrib.auth.models import Group
from system.filters import BookFilter
from system.forms import BookInstanceForm, BookIssuanceForm, IncomingTransactionForm, MyCrispyForm, OutgoingTransactionForm
from system.models import SMS, Book, BookInstance, CustomUser, Genre, IncomingTransaction, OutgoingTransaction, Author, Penalty, Student, Year
from django.contrib.admin.views.main import ChangeList
from django.urls import reverse
from django.utils.html import format_html
from django.utils import timezone
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.db.models import Q

from system.tables import PenaltyTable


admin.site.unregister(Group)
exempted_models = (Group, SMS)

class NoRelatedFieldButtons(admin.ModelAdmin):
    list_per_page = 10

    def formfield_for_dbfield(self, *args, **kwargs):
        formfield = super().formfield_for_dbfield(*args, **kwargs)

        formfield.widget.can_delete_related = False
        formfield.widget.can_change_related = False
        formfield.widget.can_add_related = False  # can change this, too
        formfield.widget.can_view_related = False  # can change this, too

        if isinstance(formfield.widget, RelatedFieldWidgetWrapper):
            select_widget = formfield.widget.widget
            formfield.widget = select_widget
        return formfield

    def get_form(self, request, obj, change, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        return form


@admin.register(Genre)
class GenreAdmin(NoRelatedFieldButtons):
    exclude = ('is_active', 'was_deleted')
    search_fields = ('name',)
    

@admin.register(OutgoingTransaction)
class OutgoingTransactionAdmin(NoRelatedFieldButtons):
    form = BookIssuanceForm
    # readonly_fields = ('borrower', 'book', 'date_borrowed')
    fields = ('book', 'borrower', 'date_borrowed', 'return_date')
    list_display = ('borrower_id', 'borrower_name', 'book', 'date_borrowed', 'return_date', 'mark_as_returned')
    search_fields = ('borrower_id', 'borrower_name', 'book',)
    autocomplete_fields = ('borrower', )
    list_display_links = None


    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.filter(returned=False)
        return qs

    def borrower_name(self, obj):
        return f'{obj.borrower.first_name} {obj.borrower.last_name}'

    def borrower_id(self, obj):
        return f'{obj.borrower.school_id}'

    def has_add_permission(self, request):
        return request.user.is_superuser and ("add" in request.path or "change" in request.path)

    def mark_as_returned(self, obj):
        url = reverse('system:mark_as_returned',  args=[obj.id])
        icon = f'<svg class="mark_as_returned" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 16 16" stroke-width="1" stroke="currentColor" class="w-6 h-6 cursor-pointer hover:text-green-500 transition-all"><path d="M2.5 8a5.5 5.5 0 0 1 8.25-4.764.5.5 0 0 0 .5-.866A6.5 6.5 0 1 0 14.5 8a.5.5 0 0 0-1 0 5.5 5.5 0 1 1-11 0z"></path><path d="M15.354 3.354a.5.5 0 0 0-.708-.708L8 9.293 5.354 6.646a.5.5 0 1 0-.708.708l3 3a.5.5 0 0 0 .708 0l7-7z"></path></svg>'
        a_link = f'<a href="{url}">{icon}</a>'        
        return mark_safe(f'<div class="text-sm flex justify-center text-gray-900 w-25">{a_link}</div>')

    def get_changeform_initial_data(self, request):
        book_id = request.GET.get('book_id', None)
        initial_book = Book.objects.none
        if book_id is not None:
            initial_book = Book.objects.filter(pk=book_id).first()

        return {
            'book': initial_book,
        }

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def save_model(self, request, obj, form, change):
        #Newly created
        if change is False:
            book = obj.book
            book.inventory_stock = max(book.inventory_stock-1, 0)
            book.save()

        super(OutgoingTransactionAdmin, self).save_model(request, obj, form, change)


@admin.register(Book)
class BookAdmin(NoRelatedFieldButtons):
    fields = ('isbn', 'author', 'title', 'genre', 'inventory_stock', 'book_price', 'overtime_fine')
    list_display = ('isbn', 'author', 'book_title', 'category', 'price', 'stock', 'manage_borrow')
    search_fields = ('isbn', 'title',)
    list_filter = ('genre', )

    list_display_links = None
    
    def changelist_view(self, request, extra_context=None):
        request.GET._mutable=True
        queryset = self.get_queryset(request)
        queryset = queryset.filter(Q(author=request.GET.pop('author', None)))
        filter = BookFilter(request.GET, queryset=queryset)
        my_context = {
            'filter' : filter
        }
        request.GET._mutable=False
        return super(BookAdmin, self).changelist_view(request,
            extra_context=my_context)

    def book_title(self, obj):
        return obj.title

    def category(self, obj):
        return obj.genre

    def price(self, obj):
        return f'₱{obj.book_price}'

    def stock(self, obj):
        return obj.inventory_stock

    @admin.display(description='Manage/Borrow')
    def manage_borrow(self, obj):
        url = reverse('admin:%s_%s_change' % (obj._meta.app_label,  obj._meta.model_name),  args=[obj.id] )
        edit_svg = '<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 cursor-pointer hover:text-blue-500 transition-all"><path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10"></path></svg>'
        a_edit = f'<a href="{url}">{edit_svg}</a>'# % (url,  obj.__unicode__())

        borrow_svg = f'<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 cursor-pointer hover:text-green-500 transition-all"><path stroke-linecap="round" stroke-linejoin="round" d="M19.5 12c0-1.232-.046-2.453-.138-3.662a4.006 4.006 0 00-3.7-3.7 48.678 48.678 0 00-7.324 0 4.006 4.006 0 00-3.7 3.7c-.017.22-.032.441-.046.662M19.5 12l3-3m-3 3l-3-3m-12 3c0 1.232.046 2.453.138 3.662a4.006 4.006 0 003.7 3.7 48.656 48.656 0 007.324 0 4.006 4.006 0 003.7-3.7c.017-.22.032-.441.046-.662M4.5 12l3 3m-3-3l-3 3"></path></svg>'
        borrow_url = f"%s?book_id={obj.pk}" %  reverse('admin:%s_%s_add' % (obj._meta.app_label,  OutgoingTransaction._meta.model_name))
        a_borrow = f'<a href="{borrow_url}">{borrow_svg}</a>'

        return mark_safe(f'''<div class="text-sm flex justify-center text-gray-900 w-25">
            {a_edit}
            {a_borrow}
            </div>''')
    


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    search_fields = ('school_id', 'full_name', 'year_and_section', 'mobile_no')
    fields = ('first_name', 'middle_name', 'last_name', 'gender', 'school_id', 'year', 'section', 'address', 'mobile_no', 'email', 'qualified')
    list_display = ('school_id', 'full_name', 'year_and_section', 'mobile_no', 'manage_me')
    list_display_links = ('manage_me', )
    

    def full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'

    def year_and_section(self, obj):
        return f'{Year(obj.year).label} {obj.section}'

    @admin.display(description='Manage')
    def manage_me(self, obj):
        return mark_safe('<div class="text-sm flex justify-center text-gray-900 w-25"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-6 h-6 cursor-pointer hover:text-blue-500 transition-all"><path stroke-linecap="round" stroke-linejoin="round" d="M16.862 4.487l1.687-1.688a1.875 1.875 0 112.652 2.652L10.582 16.07a4.5 4.5 0 01-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 011.13-1.897l8.932-8.931zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0115.75 21H5.25A2.25 2.25 0 013 18.75V8.25A2.25 2.25 0 015.25 6H10"></path></svg></div>')
    


    def get_readonly_fields(self, request, obj=None):
        if obj: # obj is not None, so this is an edit
            return ['email', ] # Return a list or tuple of readonly fields' names
        else: # This is an addition
            return []

    def save_model(self, request, obj, form, change):
        #Newly created
        if change is False:
            existing_user = get_user_model().objects.filter(email=obj.email).first()
            random_valid_password = get_user_model().objects.make_random_password()
            if existing_user is None:
                existing_user = get_user_model().objects.create_student(email=obj.email, password=random_valid_password)
            else:
                existing_user.set_password(random_valid_password)
            obj.user = existing_user
            
            if random_valid_password is not None:
                try:
                    href = ''
                    html_message = f'We would like to inform you that your account is now ready and created by the admin, \nThis is your initial password : <b>{random_valid_password}</b>, please do not share your password to anyone.\n If you want to change your password, you can do it by clicking this <a href="{href}">link</a>'
                    send_mail(
                        'EVSU - Student Account Registration',
                        strip_tags(messages),
                        'evsu.gmail.com',
                        (obj.email, ),
                        fail_silently=False,
                        html_message=html_message
                    )
                except SMTPDataError as error:
                    messages.error(f'{error}\n Please try again later.')
        super(StudentAdmin, self).save_model(request, obj, form, change)


@admin.register(Penalty)
class PenaltyAdmin(admin.ModelAdmin):
    fields = ('unpaid', 'due_date')
    readonly_fields = ('unpaid', 'due_date')
    search_fields = ('transaction__book__title', )
    list_display = ('borrower_id', 'borrower_name_link', 'book_borrowed', 'unpaid', 'mark_as_paid')
    list_display_links = None

    def due_date(self, obj):
        return f'Return Date : {obj.transaction.return_date}'

    @admin.display(description='Unpaid Penalty')
    def unpaid(self, obj):
        return f'₱{obj.unpaid_penalty}'

    @admin.display(description='Borrower Name')
    def borrower_name_link(self, obj):
        url = f"%s?borrower_id={obj.transaction.borrower.school_id}" %  reverse('system:transaction_history')
        link = f'<a href={url}>{obj.transaction.borrower.full_name}</a>'
        return mark_safe(link)

    def book_borrowed(self, obj):
        return obj.transaction.book.title

    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False

    def borrower_id(self, obj):
        return obj.transaction.borrower.school_id

    def borrower_name(self, obj):
        return obj.transaction.borrower.full_name

    def mark_as_paid(self, obj):
        url = reverse('system:mark_as_paid',  args=[obj.id])
        icon = f'<svg class="mark_as_paid" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 16 16" stroke-width="1" stroke="currentColor" class="w-6 h-6 cursor-pointer hover:text-green-500 transition-all"><path d="M2.5 8a5.5 5.5 0 0 1 8.25-4.764.5.5 0 0 0 .5-.866A6.5 6.5 0 1 0 14.5 8a.5.5 0 0 0-1 0 5.5 5.5 0 1 1-11 0z"></path><path d="M15.354 3.354a.5.5 0 0 0-.708-.708L8 9.293 5.354 6.646a.5.5 0 1 0-.708.708l3 3a.5.5 0 0 0 .708 0l7-7z"></path></svg>'
        a_link = f'<a href="{url}">{icon}</a>'        
        return mark_safe(f'<div class="text-sm flex justify-center text-gray-900 w-25">{a_link}</div>')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(transaction__paid=False)


    def changelist_view(self, request, extra_context=None):
        my_context = {
            'send_notif': True
        }
        return super(PenaltyAdmin, self).changelist_view(request,
            extra_context=my_context)


app_config = apps.get_app_config('system')
models = app_config.get_models()

# for model in models:
#     if model.__class__ in exempted_models:
#         continue
#     try:
#         admin.site.register(model)
#     except admin.sites.AlreadyRegistered:
#         pass

admin.site.site_header = "evsu Book Library"
admin.site.site_title = 'Evsu Book Library System'
admin.site.index_title = "Welcome to evsu Book Library"
