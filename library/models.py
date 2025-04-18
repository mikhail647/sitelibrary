from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from decimal import Decimal
from django.core.validators import MinValueValidator
from django.urls import reverse

# --- User Management ---

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        # Ensure superuser defaults match the SQL schema expectations if needed
        extra_fields.setdefault('role', 'admin') # Map 'role' to user_type or similar

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        # Adjust role mapping if necessary
        user = self.create_user(username, email, password, **extra_fields)
        # Ensure any additional default fields from SQL are set if not handled by create_user
        user.date_joined = timezone.now() # Explicitly set date_joined if needed
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    # Match SQL schema for custom_user table
    class Meta:
        db_table = 'custom_user'
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    # Define fields as per SQL schema
    # 'id' is created automatically by Django as PK unless specified otherwise
    password = models.CharField(max_length=128) # Mapped from SQL
    last_login = models.DateTimeField(blank=True, null=True) # Mapped from SQL
    is_superuser = models.BooleanField(default=False) # Mapped from SQL
    username = models.CharField(max_length=150, unique=True) # Mapped from SQL
    first_name = models.CharField(max_length=150) # Mapped from SQL
    last_name = models.CharField(max_length=150) # Mapped from SQL
    email = models.EmailField(max_length=254, unique=True) # Ensure email is unique if needed
    is_staff = models.BooleanField(default=False) # Mapped from SQL
    is_active = models.BooleanField(default=True) # Mapped from SQL (default differs)
    date_joined = models.DateTimeField(default=timezone.now) # Mapped from SQL

    # Role field from SQL
    ROLE_CHOICES = (
        ('user', 'Пользователь'),
        ('staff', 'Сотрудник'),
        ('admin', 'Администратор'),
        # Add other roles if necessary based on application logic
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email'] # username and password are required by default

    def __str__(self):
        return self.username

    # Add other methods from AbstractUser if needed (like get_full_name, get_short_name)
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()

    def get_short_name(self):
        return self.first_name

# --- Reader and Related Tables ---

class ReaderType(models.Model):
    class Meta:
        db_table = 'reader_types'
        verbose_name = 'Тип читателя'
        verbose_name_plural = 'Типы читателей'

    type_id = models.AutoField(primary_key=True)
    type_name = models.CharField(max_length=50)
    max_books_allowed = models.IntegerField()
    loan_period_days = models.IntegerField()
    can_use_reading_room = models.BooleanField(default=True)
    can_use_loan = models.BooleanField(default=True)
    fine_per_day = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('10.00'), verbose_name="Штраф за день просрочки (руб.)")

    def __str__(self):
        return self.type_name

class LibraryReader(models.Model):
    class Meta:
        db_table = 'library_readers'
        verbose_name = 'Читатель'
        verbose_name_plural = 'Читатели'

    STATUS_CHOICES = (
        ('active', 'Активен'),
        ('suspended', 'Приостановлен'),
        ('expelled', 'Исключен'),
    )

    reader_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='library_profile', db_column='user_id')
    reader_type = models.ForeignKey(ReaderType, on_delete=models.PROTECT, verbose_name="Тип читателя", db_column='reader_type_id')
    first_name = models.CharField(max_length=50, verbose_name="Имя")
    last_name = models.CharField(max_length=50, verbose_name="Фамилия")
    middle_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Отчество")
    library_card_number = models.CharField(max_length=20, unique=True, verbose_name="Номер чит. билета")
    registration_date = models.DateField(verbose_name="Дата регистрации")
    reader_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active', verbose_name="Статус")
    suspension_end_date = models.DateField(blank=True, null=True, verbose_name="Дата окончания приостановки")
    can_take_books_home = models.BooleanField(default=True, verbose_name="Разрешено брать книги на дом")

    def __str__(self):
        name = f"{self.last_name} {self.first_name}" + (f" {self.middle_name}" if self.middle_name else "")
        return f"{name} ({self.library_card_number})"

# --- Reader Subtype Tables ---

class StudentReader(models.Model):
    class Meta:
        db_table = 'student_readers'
        verbose_name = 'Читатель-студент'
        verbose_name_plural = 'Читатели-студенты'

    reader = models.OneToOneField(LibraryReader, primary_key=True, on_delete=models.CASCADE, related_name='student_profile')
    faculty = models.CharField(max_length=100, verbose_name="Факультет", blank=True, null=True)
    study_group = models.CharField(max_length=20, verbose_name="Группа", blank=True, null=True)
    course_number = models.IntegerField(verbose_name="Курс", blank=True, null=True)

    def __str__(self):
        return f"Студент: {self.reader}"

class TeacherReader(models.Model):
    class Meta:
        db_table = 'teacher_readers'
        verbose_name = 'Читатель-преподаватель/сотрудник'
        verbose_name_plural = 'Читатели-преподаватели/сотрудники'

    reader = models.OneToOneField(LibraryReader, primary_key=True, on_delete=models.CASCADE, related_name='teacher_profile')
    department = models.CharField(max_length=100, verbose_name="Кафедра/Отдел", blank=True, null=True)
    academic_degree = models.CharField(max_length=50, blank=True, null=True, verbose_name="Ученая степень")
    academic_title = models.CharField(max_length=50, blank=True, null=True, verbose_name="Ученое звание")
    position = models.CharField(max_length=100, blank=True, null=True, verbose_name="Должность")

    def __str__(self):
        return f"Преподаватель/Сотрудник: {self.reader}"

class TemporaryReader(models.Model):
    class Meta:
        db_table = 'temporary_readers'
        verbose_name = 'Временный читатель'
        verbose_name_plural = 'Временные читатели'

    TYPE_CHOICES = (
        ('FPC', 'Слушатель ФПК'),
        ('applicant', 'Абитуриент'),
        ('intern', 'Стажер'),
        # Add others if needed based on ReaderType
    )

    reader = models.OneToOneField(LibraryReader, primary_key=True, on_delete=models.CASCADE)
    reader_type = models.CharField(max_length=10, choices=TYPE_CHOICES) # Map ENUM to CharField

    def __str__(self):
        return f"Временный: {self.reader.last_name} {self.reader.first_name}"

# --- Library Infrastructure ---

class LibraryLocation(models.Model):
    class Meta:
        db_table = 'library_locations'
        verbose_name = 'Пункт выдачи'
        verbose_name_plural = 'Пункты выдачи'

    TYPE_CHOICES = (
        ('loan', 'Абонемент'),
        ('reading_room', 'Читальный зал'),
    )

    location_id = models.AutoField(primary_key=True)
    location_name = models.CharField(max_length=100)
    location_type = models.CharField(max_length=15, choices=TYPE_CHOICES)
    address = models.CharField(max_length=200)

    def __str__(self):
        return self.location_name

# --- Book Catalog ---

class BookCatalog(models.Model):
    class Meta:
        db_table = 'book_catalog'
        verbose_name = 'Книга (каталог)'
        verbose_name_plural = 'Книги (каталог)'

    STATUS_CHOICES = (
        ('available', 'Доступна'),
        ('lost', 'Утеряна'),
        ('damaged', 'Повреждена'),
    )

    book_id = models.AutoField(primary_key=True)
    book_title = models.CharField(max_length=200)
    isbn = models.CharField(max_length=13, unique=True, blank=True, null=True)
    publication_year = models.IntegerField(blank=True, null=True)
    publisher_name = models.CharField(max_length=100, blank=True, null=True)
    acquisition_date = models.DateField()
    book_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='available')
    authors = models.ManyToManyField('BookAuthor', through='BookAuthorRelation', related_name='books')

    def __str__(self):
        return self.book_title

class BookAuthor(models.Model):
    class Meta:
        db_table = 'book_authors'
        verbose_name = 'Автор'
        verbose_name_plural = 'Авторы'

    author_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.last_name} {self.first_name}"

class BookAuthorRelation(models.Model):
    class Meta:
        db_table = 'book_author_relations'
        unique_together = (('book', 'author'),) # Composite Primary Key in Django
        verbose_name = 'Связь книга-автор'
        verbose_name_plural = 'Связи книга-автор'

    book = models.ForeignKey(BookCatalog, on_delete=models.CASCADE, db_column='book_id')
    author = models.ForeignKey(BookAuthor, on_delete=models.CASCADE, db_column='author_id')

    def __str__(self):
        return f"{self.book.book_title} - {self.author}"

# --- Book Copies ---

class BookCopy(models.Model):
    class Meta:
        db_table = 'book_copies'
        verbose_name = 'Экземпляр книги'
        verbose_name_plural = 'Экземпляры книг'

    STATUS_CHOICES = (
        ('available', 'Доступен'),
        ('issued', 'Выдан'),
        ('lost', 'Утерян'),
        ('damaged', 'Поврежден'),
    )

    copy_id = models.AutoField(primary_key=True)
    book = models.ForeignKey(BookCatalog, on_delete=models.CASCADE, verbose_name="Книга (каталог)", related_name='copies', db_column='book_id')
    location = models.ForeignKey(LibraryLocation, on_delete=models.PROTECT, verbose_name="Пункт выдачи", db_column='location_id')
    inventory_number = models.CharField(max_length=50, unique=True, verbose_name="Инв. номер")
    copy_status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='available', verbose_name="Статус")
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Стоимость (руб.)", validators=[MinValueValidator(Decimal('0.01'))])

    def __str__(self):
        return f"{self.book.book_title} (Инв. №: {self.inventory_number})"

# --- Loans, Fines, Requests ---

class BookLoan(models.Model):
    class Meta:
        db_table = 'book_loans'
        verbose_name = 'Выдача книги'
        verbose_name_plural = 'Выдачи книг'

    STATUS_CHOICES = (
        ('active', 'Активна'),
        ('returned', 'Возвращена'),
        ('overdue', 'Просрочена'),
        ('lost', 'Утеряна'),
    )

    loan_id = models.AutoField(primary_key=True)
    reader = models.ForeignKey(LibraryReader, on_delete=models.PROTECT, db_column='reader_id')
    copy = models.ForeignKey(BookCopy, on_delete=models.PROTECT, db_column='copy_id')
    location = models.ForeignKey(LibraryLocation, on_delete=models.PROTECT, db_column='location_id')
    loan_date = models.DateField()
    due_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)
    loan_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return f"Выдача №{self.loan_id} ({self.copy}) читателю {self.reader}"

class InterlibraryRequest(models.Model):
    class Meta:
        db_table = 'interlibrary_requests'
        verbose_name = 'Запрос МБА'
        verbose_name_plural = 'Запросы МБА'

    STATUS_CHOICES = (
        ('pending', 'Ожидает'),
        ('approved', 'Одобрен (Ожидает заказа/отправки)'),
        ('rejected', 'Отклонен'),
        ('processing', 'В обработке (Заказан/Отправлен)'),
        ('received', 'Получен (В библиотеке)'),
        ('issued', 'Выдан читателю'),
        ('returned', 'Возвращен (Читателем)'),
        ('closed', 'Закрыт (Возвращен поставщику)'),
        ('cancelled', 'Отменен (Читателем)'), # Added for clarity
    )

    request_id = models.AutoField(primary_key=True)
    reader = models.ForeignKey(LibraryReader, on_delete=models.CASCADE, verbose_name="Читатель", db_column='reader_id')
    book = models.ForeignKey(BookCatalog, on_delete=models.CASCADE, verbose_name="Книга", db_column='book_id')
    request_date = models.DateField(default=timezone.now, verbose_name="Дата запроса")
    request_status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending', verbose_name="Статус запроса")
    required_by_date = models.DateField(blank=True, null=True, verbose_name="Требуется к дате")
    notes = models.TextField(blank=True, null=True, verbose_name="Примечания читателя")
    staff_notes = models.TextField(blank=True, null=True, verbose_name="Примечания сотрудника")
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Обработал сотрудник", related_name='processed_interlibrary_requests', limit_choices_to={'role__in': ['staff', 'admin']})
    processed_date = models.DateTimeField(null=True, blank=True, verbose_name="Дата обработки")

    def __str__(self):
        return f"Запрос МБА №{self.request_id} от {self.reader.last_name} на '{self.book.book_title}'"

class LibraryFine(models.Model):
    class Meta:
        db_table = 'library_fines'
        verbose_name = 'Штраф'
        verbose_name_plural = 'Штрафы'

    STATUS_CHOICES = (
        ('pending', 'Ожидает оплаты'),
        ('paid', 'Оплачен'),
        ('cancelled', 'Списан'),
    )
    REASON_CHOICES = (
        ('overdue', 'Просрочка возврата'),
        ('lost', 'Утеря книги'),
        ('damaged', 'Повреждение книги'),
    )

    fine_id = models.AutoField(primary_key=True)
    reader = models.ForeignKey(LibraryReader, on_delete=models.PROTECT, verbose_name="Читатель", db_column='reader_id')
    loan = models.ForeignKey(BookLoan, on_delete=models.SET_NULL, verbose_name="Выдача (если применимо)", db_column='loan_id', null=True, blank=True)
    request = models.ForeignKey(InterlibraryRequest, on_delete=models.PROTECT, verbose_name="Запрос МБА (если применимо)", db_column='request_id', null=True, blank=True)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма штрафа")
    fine_date = models.DateField(default=timezone.now, verbose_name="Дата штрафа")
    fine_status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending', verbose_name="Статус штрафа")
    fine_reason = models.CharField(max_length=10, choices=REASON_CHOICES, verbose_name="Причина штрафа")

    def __str__(self):
        return f"Штраф №{self.fine_id} для {self.reader.last_name} ({self.get_fine_reason_display()})"

# --- Registrations ---

class ReaderRegistration(models.Model):
    class Meta:
        db_table = 'reader_registrations'
        verbose_name = 'Регистрация читателя в пункте'
        verbose_name_plural = 'Регистрации читателей в пунктах'

    registration_id = models.AutoField(primary_key=True)
    reader = models.ForeignKey(LibraryReader, on_delete=models.CASCADE, db_column='reader_id')
    location = models.ForeignKey(LibraryLocation, on_delete=models.CASCADE, db_column='location_id')
    registration_date = models.DateField()
    registration_expiry_date = models.DateField()

    def __str__(self):
        return f"Регистрация {self.reader} в {self.location} до {self.registration_expiry_date}"

# --- Book Requests (User Orders) ---

class BookRequest(models.Model):
    class Meta:
        # Decide on a table name if you want to manage it via SQL later
        # db_table = 'book_requests'
        verbose_name = 'Запрос на книгу'
        verbose_name_plural = 'Запросы на книги'
        ordering = ['-request_date']

    STATUS_CHOICES = (
        ('pending', 'Ожидает подтверждения'),
        ('approved', 'Одобрен (Ожидает выдачи)'),
        ('rejected', 'Отклонен'),
        ('issued', 'Выдан'),
        ('cancelled', 'Отменен пользователем'),
    )

    request_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='book_requests')
    book = models.ForeignKey(BookCatalog, on_delete=models.CASCADE, related_name='requests')
    requested_location = models.ForeignKey(LibraryLocation, on_delete=models.PROTECT, verbose_name="Желаемый пункт выдачи")
    request_date = models.DateTimeField(default=timezone.now)
    desired_start_date = models.DateField(null=True, blank=True, verbose_name="Желаемая дата начала")
    desired_end_date = models.DateField(null=True, blank=True, verbose_name="Желаемая дата окончания")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    loan = models.OneToOneField(BookLoan, on_delete=models.SET_NULL, null=True, blank=True, related_name='request_origin')
    processed_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='processed_requests', limit_choices_to={'role__in': ['staff', 'admin']})
    processed_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, null=True, verbose_name="Примечания сотрудника")

    def __str__(self):
        return f"Запрос №{self.request_id} от {self.user.username} на '{self.book.book_title}'"