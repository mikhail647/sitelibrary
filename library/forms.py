from django import forms
from .models import BookCatalog, BookLoan, BookCopy, LibraryReader, CustomUser, ReaderType, BookRequest, LibraryLocation, InterlibraryRequest, StudentReader, TeacherReader
from django.utils import timezone
from django.db.models import Q
from django_select2.forms import Select2Widget

class BookCatalogForm(forms.ModelForm):
    class Meta:
        model = BookCatalog
        fields = ['book_title', 'isbn', 'publication_year', 'publisher_name', 'acquisition_date', 'book_status', 'authors']
        widgets = {
            'publication_year': forms.NumberInput(attrs={'min': 1000, 'max': timezone.now().year + 1}),
            'acquisition_date': forms.DateInput(attrs={'type': 'date'}),
            'authors': forms.SelectMultiple(attrs={'size': '10'}),
        }

class BookLoanForm(forms.ModelForm):
    reader = forms.ModelChoiceField(
        queryset=LibraryReader.objects.filter(
            reader_status='active',
            suspension_end_date__isnull=True
        ).select_related('user'),
        label="Читатель (поиск по ФИО или номеру билета)",
        widget=Select2Widget(attrs={'data-placeholder': 'Выберите читателя'}),
        to_field_name='reader_id'
    )

    copy = forms.ModelChoiceField(
        queryset=BookCopy.objects.filter(copy_status='available').select_related('book', 'location'),
        label="Экземпляр книги (поиск по инв. номеру или названию)",
        widget=Select2Widget(attrs={'data-placeholder': 'Выберите экземпляр'}),
        to_field_name='copy_id'
    )

    class Meta:
        model = BookLoan
        fields = ['reader', 'copy']

# --- Registration Form --- #
class RegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput)
    # Role selection might imply ReaderType selection implicitly or need adjustment
    # We'll handle ReaderType assignment in the view for now.

    # --- Student Fields (Conditional) ---
    faculty = forms.CharField(label='Факультет', required=False, max_length=100)
    study_group = forms.CharField(label='Группа', required=False, max_length=20)
    course_number = forms.IntegerField(label='Курс', required=False, min_value=1, max_value=10)

    # --- Teacher/Staff Fields (Conditional) ---
    department = forms.CharField(label='Кафедра/Отдел', required=False, max_length=100)
    position = forms.CharField(label='Должность', required=False, max_length=100)
    academic_degree = forms.CharField(label='Ученая степень', required=False, max_length=50)
    academic_title = forms.CharField(label='Ученое звание', required=False, max_length=50)

    class Meta:
        model = CustomUser
        # Removed role from here, will handle implicitly or differently
        fields = ('username', 'first_name', 'last_name', 'email') 
        labels = {
            'username': 'Логин',
            'first_name': 'Имя', 
            'last_name': 'Фамилия',
            'email': 'Email',
            # 'role': 'Роль', # Role might be determined differently now
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Initially hide conditional fields? Or manage visibility with JS?
        # For now, they are always present but marked not required.
        # A better UX would use JS to show/hide based on a selected profile type.

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Пароли не совпадают.')
        return cd['password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Пользователь с таким Email уже существует.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        # Basic validation example: Ensure student fields are provided if type is Student
        # This logic is complex here, better handled in the view after determining type.
        return cleaned_data

# --- Book Request Form (User) --- #
class BookRequestForm(forms.ModelForm):
    # Filter books to show only those potentially available
    # A better approach might be to filter based on BookCatalog status or counts in the view
    book = forms.ModelChoiceField(
        queryset=BookCatalog.objects.filter(copies__copy_status='available').distinct(),
        label="Книга",
        widget=Select2Widget(attrs={'data-placeholder': 'Выберите книгу для запроса'})
    )
    requested_location = forms.ModelChoiceField(
        queryset=LibraryLocation.objects.all(),
        label="Желаемый пункт выдачи",
        widget=Select2Widget(attrs={'data-placeholder': 'Выберите пункт выдачи'})
    )

    class Meta:
        model = BookRequest
        fields = ['book', 'requested_location']

# --- Interlibrary Request Form (User) --- #
class InterlibraryRequestForm(forms.ModelForm):
    # Filter books - maybe allow searching all books?
    # Consider if users should only request books NOT currently available locally.
    book = forms.ModelChoiceField(
        queryset=BookCatalog.objects.all().order_by('book_title'), # Or filter as needed
        label="Книга (поиск по названию)",
        widget=Select2Widget(attrs={'data-placeholder': 'Выберите книгу для запроса МБА'})
    )
    required_by_date = forms.DateField(
        label="Требуется к дате (необязательно)",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    notes = forms.CharField(
        label="Примечания (необязательно)",
        required=False,
        widget=forms.Textarea(attrs={'rows': 3})
    )

    class Meta:
        model = InterlibraryRequest
        fields = ['book', 'required_by_date', 'notes']