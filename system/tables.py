import django_tables2 as tables
from system.models import Book, BookInstance, OutgoingTransaction, Penalty
from django.utils.translation import gettext_lazy as _


class BookInstanceTable(tables.Table):
    class Meta:
        model = BookInstance
        template_name = "django_tables2/bootstrap5.html"
        fields = ("book", "book__author", "book__genre", "book__publish_date", "status", 'location', "borrow_count")
        empty_text = _("No books found for this search query.")
        attrs = {'class': 'table table-hover shadow records-table'}
        # row_attrs = {'data-href': lambda book: book.get_absolute_url}

class BookTable(tables.Table):
    def render_overtime_fine(self, value):
        return f'₱{value}'

    class Meta:
        model = Book
        template_name = "django_tables2/bootstrap5.html"
        fields = ('isbn', 'author', 'title', 'genre', 'overtime_fine', 'inventory_stock')
        empty_text = _("No books found for this search query.")
        attrs = {'class': 'table table-hover shadow records-table'}

class OutgoingTransactionTable(tables.Table):
    # status = tables.Column(empty_values=())

    class Meta:
        model = OutgoingTransaction
        template_name = "django_tables2/bootstrap5.html"
        fields = ("book__book__title", "date_borrowed", "return_date")
        empty_text = _("No books borrowed.")
        attrs = {'class': 'table table-hover shadow records-table'}


class PenaltyTable(tables.Table):
    unpaid_penalty = tables.Column(verbose_name= 'Penalty' )
    
    def render_unpaid_penalty(self, value):
        return f'₱{value}'

    class Meta:
        model = Penalty
        template_name = "django_tables2/bootstrap5.html"
        fields = ("transaction__borrower__school_id", "transaction__borrower__full_name", "transaction__book__title", "transaction__returned", "unpaid_penalty", "date_paid")
        empty_text = _("No records")
        attrs = {'class': 'table table-hover shadow records-table'}



    # def render_status(self, value, record):
    #     if record:
    #         book = record.book
    #         if book.status == 'o':
    #             return 'On hand'
    #     return 'Returned'