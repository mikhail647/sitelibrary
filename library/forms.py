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
            'book_title': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'publication_year': forms.NumberInput(attrs={'min': 1000, 'max': timezone.now().year + 1, 'class': 'form-control'}),
            'publisher_name': forms.TextInput(attrs={'class': 'form-control'}),
            'acquisition_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'book_status': forms.Select(attrs={'class': 'form-select'}),
            'authors': forms.SelectMultiple(attrs={'size': '10', 'class': 'form-select'}),
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

    def __init__(self, *args, **kwargs):
        # Check if we are initializing from a request context
        is_from_request = kwargs.pop('is_from_request', False)
        reader_instance = kwargs.get('initial', {}).get('reader')

        super().__init__(*args, **kwargs)

        # If initialized from a request with a reader, make reader not required
        # and disable the widget. The view will handle setting the reader.
        if is_from_request and reader_instance:
            self.fields['reader'].required = False
            self.fields['reader'].widget.attrs['disabled'] = True
            # Ensure the initial value is correctly set for display
            self.initial['reader'] = reader_instance
        elif 'disabled' in self.fields['reader'].widget.attrs:
            # Clean up disabled attribute if not from request (e.g., on form error refresh)
            del self.fields['reader'].widget.attrs['disabled']

        # Ensure copy queryset is passed if provided (view needs to handle this)
        copy_queryset = kwargs.pop('copy_queryset', None)
        if copy_queryset is not None:
             self.fields['copy'].queryset = copy_queryset

# --- Registration Form --- #
class RegistrationForm(forms.ModelForm):
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Повторите пароль', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    # Role selection might imply ReaderType selection implicitly or need adjustment
    # We'll handle ReaderType assignment in the view for now.

    # --- Student Fields (Conditional) ---
    faculty = forms.CharField(label='Факультет', required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    study_group = forms.CharField(label='Группа', required=False, max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    course_number = forms.IntegerField(label='Курс', required=False, min_value=1, max_value=10, widget=forms.NumberInput(attrs={'class': 'form-control'}))

    # --- Teacher/Staff Fields (Conditional) ---
    department = forms.CharField(label='Кафедра/Отдел', required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    position = forms.CharField(label='Должность', required=False, max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    academic_degree = forms.CharField(label='Ученая степень', required=False, max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))
    academic_title = forms.CharField(label='Ученое звание', required=False, max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))

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
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
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
    # Add the date fields
    desired_start_date = forms.DateField(
        label="Желаемая дата начала (необяз.)",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    desired_end_date = forms.DateField(
        label="Желаемая дата окончания (необяз.)",
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    class Meta:
        model = BookRequest
        # Include the new date fields
        fields = ['book', 'requested_location', 'desired_start_date', 'desired_end_date']

    # Optional: Add validation to ensure end date is after start date
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("desired_start_date")
        end_date = cleaned_data.get("desired_end_date")

        if start_date and end_date:
            if end_date < start_date:
                raise forms.ValidationError(
                    "Желаемая дата окончания не может быть раньше даты начала."
                )
        return cleaned_data

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
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    notes = forms.CharField(
        label="Примечания (необязательно)",
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
    )

    class Meta:
        model = InterlibraryRequest
        fields = ['book', 'required_by_date', 'notes']