from django.db.models.signals import post_save
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from evsu_library.managers import CustomUserManager
import uuid
from datetime import date
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from isbn_field import ISBNField
from django.utils.translation import gettext_lazy as _
import django.db.models.options as options

options.DEFAULT_NAMES = options.DEFAULT_NAMES + ('icon',)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(_("email address"), unique=True)
    picture = models.ImageField(
        upload_to='images/', blank=True, null=True, default='')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    @property
    def username(self):
        return self.email

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "User"


class TimeStampedMixin(models.Model):
    """
    Abstract model that defines the auto populated 'created_date' and
    'last_modified' fields.

    This model must be used as the base for all the models in the project.
    """
    created_date = models.DateTimeField(
        editable=False,
        blank=True, null=True,
        auto_now_add=True,
        verbose_name=_('created date')
    )
    last_modified = models.DateTimeField(
        editable=False,
        blank=True, null=True,
        auto_now=True,
        verbose_name=_('last modified'),
    )

    class Meta:

        abstract = True


class CatalogueMixin(TimeStampedMixin):
    """
    Abstract model that defines name, is active and extends
    from TimeStampedMixin.
    This model must be used as the base for catalogue models in the project.
    """
    name = models.CharField(
        max_length=255,
        verbose_name='name',
        unique=True
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='is active'
    )
    was_deleted = models.BooleanField(
        default=False,
        verbose_name='was deleted'
    )

    class Meta:
        abstract = True

    def __str__(self):
        return self.name




class Genre(CatalogueMixin):
    """
    Model representing a book genre.
    """
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')


class Author(TimeStampedMixin):
    """
    Model representing an author.
    """
    first_name = models.CharField(max_length=100)

    last_name = models.CharField(max_length=100)

    date_of_birth = models.DateField('Birth', null=True, blank=True)

    date_of_death = models.DateField('Died', null=True, blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        verbose_name = _('author')
        verbose_name_plural = _('authors')

    def __str__(self):
        """
        String for representing the Model object
        """
        return '{0} ({1})'.format(self.first_name, self.last_name)


class Book(models.Model):
    """
    Model representing a book (but not a specific copy of a book).
    """
    author = models.CharField(max_length=255, blank=False, default='')

    isbn = ISBNField(clean_isbn=False, unique=True)

    title = models.CharField(verbose_name='Book Title', max_length=255, default='', blank=False)

    inventory_stock = models.PositiveIntegerField(default=0, validators=(MinValueValidator(0),))
    # ManyToManyField used because genre can contain many books.
    # Books can cover many genres.
    # Genre class has already been defined so we can specify the object above.
    genre = models.ForeignKey(        
        Genre,
        on_delete=models.SET_NULL,
        verbose_name='Book Category',
        null=True
    )

    book_price = models.FloatField(default=0, validators=(MinValueValidator(0) ,), help_text='Student will be responsible to pay ₱{} if they lost the borrowed book')
    overtime_fine = models.FloatField(default=0, validators=(MinValueValidator(0) ,), help_text='Student will be responsible to pay ₱{} if they exceeded the return date')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _('book')
        verbose_name_plural = _('books')

    class JSONAPIMeta:
        resource_name = 'books'

def generate_school_id():
    
    try_student_id = get_next_school_id()
    while(Student.objects.filter(school_id=try_student_id).first() is not None):
        try_student_id = get_next_school_id()
    return try_student_id

def get_next_school_id():
    year = timezone.now().year
    latest_student = Student.objects.order_by('-pk').first()
    current_index = 0
    if latest_student is not None:
        current_index = int(latest_student.school_id.split('-')[1])
    current_index += 1

    return f'{year}-{str(current_index).zfill(5)}'

class Gender(models.IntegerChoices):
    MALE = 1, "Male"
    FEMALE = 2, "Female"


class Year(models.IntegerChoices):
    FIRST = 1, "1st Year"
    SECOND = 2, "2nd Year"
    THIRD = 3, "3rd Year"
    FOURTH = 4, "4th Year"

class Qualified(models.IntegerChoices):
    QUALIFIED = 1, "Qualified"
    NOT_QUALIFIED = 0, "Not Qualified"

# LMS-M-3453

class Student(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, blank=True, null=True)
    school_id = models.CharField(verbose_name='ID Number' , max_length=10, blank=False, unique=True, default=generate_school_id)
    email = models.EmailField(unique=True, blank=False, default='')
    first_name = models.CharField(blank=False, default='', max_length=50)
    middle_name = models.CharField(blank=True, max_length=50)
    last_name = models.CharField(blank=False, max_length=50)
    gender = models.IntegerField(default=Gender.MALE, choices=Gender.choices)
    year = models.IntegerField(default=Year.FIRST, choices=Year.choices, blank=False)
    section = models.CharField(max_length=50, default='', blank=False)
    address = models.CharField(max_length=255, default='', blank=False)
    mobile_no = models.CharField(verbose_name='Phone Number', blank=True, max_length=11)
    qualified = models.IntegerField(default=Qualified.QUALIFIED, choices=Qualified.choices)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return f'{self.school_id}, {self.first_name} {self.last_name}'



class BookInstance(models.Model):
    """
    Model representing a specific copy of a book
    (i.e. that can be borrowed from the library).
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE,
        related_name='books',
        related_query_name='book'
    )

    LOAN_STATUS = (
        ('o', 'On loan'),
        ('a', 'Available'),
    )

    status = models.CharField(
        max_length=1, choices=LOAN_STATUS, blank=True, default='a'
    )

    borrow_count = models.PositiveIntegerField(default=0)

    location = models.CharField(max_length=200, blank=True)


    class Meta:
        verbose_name = _('book instance')
        verbose_name_plural = _('book instances')

    def __str__(self):
        """
        String for representing the Model object
        """
        return '{0} ({1})'.format(self.id, self.book.title)





class Transaction(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE,)
    borrower = models.ForeignKey(Student, on_delete=models.CASCADE,)
    class Meta:
        abstract = True


class IncomingTransaction(Transaction):
    date_returned = models.DateField(default=timezone.now, blank=True)
    
    def __str__(self) -> str:
        return f'{self.book.book.title} - {self.borrower}'
    

class OutgoingTransaction(Transaction):
    date_borrowed = models.DateField(verbose_name='Date of Book Issuance', default=timezone.now, blank=True)
    return_date = models.DateField(verbose_name='Date of Returning Book', blank=False, null=False, help_text='The system automatically set the min number of day of borrowing book in to 3 days.')
    paid = models.BooleanField(default=False)
    returned = models.BooleanField(default=False)

    def clean(self):
        return super().clean()

    class Meta:
        verbose_name = _("Issued Book")
        verbose_name_plural = _("Issued Books")

    def __str__(self) -> str:
        return f'{self.book.title} - {self.borrower}'

class SMS(models.Model):
    students = models.ManyToManyField(Student)
    message = models.CharField(max_length=150, blank=False)


class Penalty(models.Model):
    transaction = models.ForeignKey(OutgoingTransaction, on_delete=models.CASCADE, blank=False, null=True)
    unpaid_penalty = models.FloatField(default=0, validators=(MinValueValidator(0), ))
    date_paid = models.DateField(null=True)

    class Meta:
        verbose_name_plural = 'Penalties'

    def __str__(self):
        return f'{self.transaction.book.title} - {self.transaction.borrower.full_name}'