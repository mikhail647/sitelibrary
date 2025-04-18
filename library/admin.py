from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils import timezone
from decimal import Decimal
from .models import (
    CustomUser, BookCatalog, BookAuthor, BookAuthorRelation, BookCopy,
    LibraryLocation, ReaderType, LibraryReader, StudentReader,
    TeacherReader, TemporaryReader, BookLoan, LibraryFine,
    ReaderRegistration, InterlibraryRequest
)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительно', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Дополнительно', {'fields': ('role',)}),
    )
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_editable = ('is_active', 'role')

# --- Инлайны для профилей читателей --- #
class StudentReaderInline(admin.StackedInline):
    model = StudentReader
    can_delete = False
    verbose_name_plural = 'Профиль студента'
    fk_name = 'reader'
    fields = ('faculty', 'study_group', 'course_number')

class TeacherReaderInline(admin.StackedInline):
    model = TeacherReader
    can_delete = False
    verbose_name_plural = 'Профиль преподавателя/сотрудника'
    fk_name = 'reader'
    fields = ('department', 'position', 'academic_degree', 'academic_title')

class TemporaryReaderInline(admin.StackedInline):
    model = TemporaryReader
    can_delete = False
    verbose_name_plural = 'Профиль временного читателя'
    fk_name = 'reader'
    fields = ('reader_type',)

@admin.register(LibraryReader)
class LibraryReaderAdmin(admin.ModelAdmin):
    list_display = (
        'reader_id', 'get_full_name', 'library_card_number', 'reader_type',
        'reader_status', 'suspension_end_date', 'can_take_books_home', 'registration_date'
    )
    list_filter = ('reader_type', 'reader_status', 'can_take_books_home', 'registration_date', 'suspension_end_date')
    search_fields = ('reader_id', 'first_name', 'last_name', 'middle_name', 'library_card_number', 'user__username')
    list_select_related = ('user', 'reader_type')
    inlines = [StudentReaderInline, TeacherReaderInline, TemporaryReaderInline]
    fieldsets = (
        (None, {
            'fields': ('user', 'library_card_number', 'reader_type',)
        }),
        ('Персональные данные', {
            'fields': ('last_name', 'first_name', 'middle_name')
        }),
        ('Статус и разрешения', {
            'fields': ('reader_status', 'suspension_end_date', 'can_take_books_home', 'registration_date')
        }),
    )
    raw_id_fields = ('user',)
    list_editable = ('reader_status', 'suspension_end_date', 'can_take_books_home')
    actions = ['check_suspension_status']

    def get_full_name(self, obj):
        if obj.user:
            return obj.user.get_full_name() or obj.user.username
        name = f"{obj.last_name} {obj.first_name}" + (f" {obj.middle_name}" if obj.middle_name else "")
        return name
    get_full_name.short_description = 'ФИО / Логин'

    def get_inline_instances(self, request, obj=None):
        inline_instances = []
        if obj:
            if hasattr(obj, 'student_profile'):
                inline_instances.append(StudentReaderInline(self.model, self.admin_site))
            elif hasattr(obj, 'teacher_profile'):
                inline_instances.append(TeacherReaderInline(self.model, self.admin_site))
            elif hasattr(obj, 'temporaryreader'):
                inline_instances.append(TemporaryReaderInline(self.model, self.admin_site))
        return inline_instances

    def check_suspension_status(self, request, queryset):
        today = timezone.now().date()
        updated_count = 0
        expired_suspensions = queryset.filter(
            reader_status='suspended',
            suspension_end_date__isnull=False,
            suspension_end_date__lt=today
        )
        for reader in expired_suspensions:
            reader.reader_status = 'active'
            reader.suspension_end_date = None
            reader.save()
            updated_count += 1
        
        if updated_count > 0:
            self.message_user(request, f'{updated_count} читателей активировано после истечения срока приостановки.')
        else:
            self.message_user(request, 'Не найдено читателей с истекшим сроком приостановки для активации.')
            
    check_suspension_status.short_description = "Проверить и снять приостановку (у кого истек срок)"

@admin.register(ReaderType)
class ReaderTypeAdmin(admin.ModelAdmin):
    list_display = ('type_name', 'max_books_allowed', 'loan_period_days', 'can_use_loan', 'can_use_reading_room', 'fine_per_day')
    search_fields = ('type_name',)

class BookAuthorRelationInline(admin.TabularInline):
    model = BookAuthorRelation
    extra = 1
    verbose_name = "Автор"
    verbose_name_plural = "Авторы"

class BookCopyInline(admin.TabularInline):
    model = BookCopy
    extra = 1
    fields = ('inventory_number', 'location', 'copy_status', 'cost')
    readonly_fields = ()
    verbose_name = "Экземпляр"
    verbose_name_plural = "Экземпляры"
    fk_name = "book"

@admin.register(BookCatalog)
class BookCatalogAdmin(admin.ModelAdmin):
    list_display = ('book_title', 'publication_year', 'publisher_name', 'isbn', 'get_authors_list', 'get_available_copies_count')
    list_filter = ('publication_year',)
    search_fields = ('book_title', 'isbn', 'authors__last_name', 'authors__first_name')
    inlines = [BookAuthorRelationInline, BookCopyInline]

    def get_authors_list(self, obj):
        return ", ".join([str(author) for author in obj.authors.all()])
    get_authors_list.short_description = 'Авторы'

    def get_available_copies_count(self, obj):
        return obj.copies.filter(copy_status='available').count()
    get_available_copies_count.short_description = 'Доступно экземпляров'

@admin.register(BookAuthor)
class BookAuthorAdmin(admin.ModelAdmin):
    list_display = ('author_id', 'first_name', 'last_name', 'middle_name')
    search_fields = ('first_name', 'last_name')

@admin.register(BookCopy)
class BookCopyAdmin(admin.ModelAdmin):
    list_display = ('inventory_number', 'book', 'location', 'copy_status', 'cost')
    list_filter = ('copy_status', 'location')
    search_fields = ('inventory_number', 'book__book_title', 'book__isbn')
    list_select_related = ('book', 'location')
    list_editable = ('copy_status',)
    actions = ['mark_lost', 'mark_damaged', 'mark_written_off']

    def mark_lost(self, request, queryset):
        fine_created_count = 0
        already_lost_count = 0
        updated_count = 0
        cost_missing_count = 0
        no_loan_found_count = 0

        for copy in queryset:
            if copy.copy_status == 'lost':
                already_lost_count += 1
                continue

            # --- Check cost first ---
            if copy.cost is None or copy.cost <= 0:
                # Mark as lost even without cost, but prevent fine creation
                copy.copy_status = 'lost'
                copy.save()
                updated_count += 1
                cost_missing_count += 1
                # Find active loan *only* to update its status if it exists
                active_loan = BookLoan.objects.filter(copy=copy, loan_status__in=['active', 'overdue']).first()
                if active_loan:
                    active_loan.loan_status = 'lost'
                    active_loan.save()
                continue # Skip fine creation

            # --- Cost exists, proceed with normal logic ---
            copy.copy_status = 'lost'
            copy.save()
            updated_count += 1

            active_loan = BookLoan.objects.filter(copy=copy, loan_status__in=['active', 'overdue']).first()

            if active_loan and active_loan.reader:
                fine_amount = copy.cost * 10 # 10x fine as per ТЗ
                LibraryFine.objects.create(
                    reader=active_loan.reader,
                    loan=active_loan,
                    fine_amount=fine_amount,
                    fine_reason='lost',
                    fine_status='pending',
                    notes=f"Штраф за утерю книги '{copy.book.book_title}' (Инв. №: {copy.inventory_number})"
                )
                active_loan.loan_status = 'lost'
                active_loan.save()
                fine_created_count += 1
            else:
                # Copy marked lost, cost exists, but no active loan found
                no_loan_found_count += 1

        message_parts = []
        if updated_count > 0:
            message_parts.append(f"{updated_count} копий отмечено как утерянные.")
        if fine_created_count > 0:
            message_parts.append(f"Создано {fine_created_count} штрафов (10x стоимость).")
        if cost_missing_count > 0:
            message_parts.append(f"{cost_missing_count} копий утеряно, но штраф не создан (стоимость не указана).")
        if no_loan_found_count > 0 and cost_missing_count == 0: # Avoid double reporting if cost was missing
             message_parts.append(f"{no_loan_found_count} копий утеряно без активной выдачи (штраф не создан).")
        if already_lost_count > 0:
            message_parts.append(f"{already_lost_count} копий уже были утеряны.")
        
        if not message_parts: # Handle case where only already lost items were selected
             message_parts.append("Не выбрано копий для изменения статуса на 'утерянный'.")
             
        self.message_user(request, " ".join(message_parts))
    mark_lost.short_description = "Отметить утерянным (+ штраф 10x, если есть стоимость и активная выдача)"

    def mark_damaged(self, request, queryset):
        fine_created_count = 0
        already_damaged_count = 0
        updated_count = 0
        cost_missing_count = 0
        no_loan_found_count = 0

        for copy in queryset:
            if copy.copy_status == 'damaged':
                already_damaged_count += 1
                continue

            # Mark damaged regardless of cost or loan
            copy.copy_status = 'damaged'
            copy.save()
            updated_count += 1

            # Check if cost allows fine creation
            if copy.cost is None or copy.cost <= 0:
                cost_missing_count += 1
                continue # Skip fine creation if no cost

            # Cost exists, try to find loan and reader
            fine_amount = copy.cost * Decimal('0.5') # 50% fine for damage
            active_loan = BookLoan.objects.filter(copy=copy, loan_status__in=['active', 'overdue']).first()

            if active_loan and active_loan.reader:
                LibraryFine.objects.create(
                    reader=active_loan.reader,
                    loan=active_loan, # Link fine to the loan
                    fine_amount=fine_amount,
                    fine_reason='damaged',
                    fine_status='pending',
                    notes=f"Штраф за повреждение книги '{copy.book.book_title}' (Инв. №: {copy.inventory_number})"
                )
                # Do NOT change loan status for damage, book might still be usable/returned
                # if active_loan: # This check is redundant here
                #    pass
                fine_created_count += 1
            else:
                # Damaged, cost exists, but no active loan
                no_loan_found_count += 1

        message_parts = []
        if updated_count > 0:
             message_parts.append(f"{updated_count} копий отмечено как поврежденные.")
        if fine_created_count > 0:
             message_parts.append(f"Создано {fine_created_count} штрафов (50% стоимости).")
        if cost_missing_count > 0:
             message_parts.append(f"{cost_missing_count} копий повреждено, но штраф не создан (стоимость не указана).")
        if no_loan_found_count > 0 and cost_missing_count == 0: # Avoid double reporting
            message_parts.append(f"{no_loan_found_count} копий повреждено без активной выдачи (штраф не создан).")
        if already_damaged_count > 0:
             message_parts.append(f"{already_damaged_count} копий уже были повреждены.")

        if not message_parts: # Handle case where only already damaged items were selected
             message_parts.append("Не выбрано копий для изменения статуса на 'поврежденный'.")
             
        self.message_user(request, " ".join(message_parts))
    mark_damaged.short_description = "Отметить поврежденным (+ штраф 50%, если есть стоимость и активная выдача)"

    def mark_written_off(self, request, queryset):
        # Check if copy is currently issued before writing off
        issued_copies = queryset.filter(copy_status='issued')
        if issued_copies.exists():
             inv_numbers = ", ".join([c.inventory_number for c in issued_copies])
             self.message_user(request, f"Ошибка: Нельзя списать выданные экземпляры ({inv_numbers}). Сначала верните их.", level='error')
             return # Stop the action

        # Proceed with writing off only non-issued copies
        write_off_queryset = queryset.exclude(copy_status='issued')
        updated_count = write_off_queryset.update(copy_status='written_off')
        self.message_user(request, f"{updated_count} копий отмечено как списанные.")
    mark_written_off.short_description = "Отметить списанным (нельзя списать выданные)"

@admin.register(BookLoan)
class BookLoanAdmin(admin.ModelAdmin):
    list_display = ('loan_id', 'reader', 'copy', 'loan_date', 'due_date', 'return_date', 'loan_status')
    list_filter = ('loan_status', 'loan_date', 'due_date', 'location')
    search_fields = (
        'reader__last_name', 'reader__first_name', 'reader__library_card_number',
        'copy__inventory_number', 'copy__book__book_title'
    )
    date_hierarchy = 'loan_date'
    list_select_related = ('reader', 'copy', 'copy__book', 'location', 'reader__user')
    raw_id_fields = ('reader', 'copy')

@admin.register(LibraryFine)
class LibraryFineAdmin(admin.ModelAdmin):
    list_display = ('fine_id', 'reader', 'loan', 'fine_amount', 'fine_reason', 'fine_date', 'fine_status', 'notes')
    list_filter = ('fine_status', 'fine_date', 'fine_reason', 'reader__reader_type')
    search_fields = ('reader__last_name', 'reader__first_name', 'loan__loan_id', 'loan__copy__inventory_number')
    list_select_related = ('reader', 'loan', 'request', 'reader__user', 'loan__copy')
    raw_id_fields = ('reader', 'loan', 'request')
    list_editable = ('fine_status',)
    date_hierarchy = 'fine_date'

@admin.register(InterlibraryRequest)
class InterlibraryRequestAdmin(admin.ModelAdmin):
    list_display = ('request_id', 'reader', 'book', 'request_date', 'request_status', 'processed_by', 'processed_date')
    list_filter = ('request_status', 'request_date', 'reader__reader_type')
    search_fields = ('reader__last_name', 'reader__first_name', 'book__book_title', 'processed_by__username')
    date_hierarchy = 'request_date'
    list_select_related = ('reader', 'book', 'reader__user', 'processed_by')
    raw_id_fields = ('reader', 'book', 'processed_by')
    list_editable = ('request_status',)
    fieldsets = (
        ('Информация о запросе', {
            'fields': ('reader', 'book', 'request_date', 'required_by_date', 'request_status')
        }),
        ('Обработка запроса', {
            'classes': ('collapse',),
            'fields': ('processed_by', 'processed_date', 'staff_notes')
        }),
        ('Примечания читателя', {
            'classes': ('collapse',),
            'fields': ('notes',)
        }),
    )
    readonly_fields = ('request_date',)

    actions = ['mark_approved', 'mark_rejected', 'mark_processing', 'mark_received', 'mark_issued', 'mark_returned', 'mark_closed']

    def mark_status(self, request, queryset, status_code, status_name):
        updated_count = 0
        for req in queryset:
            req.request_status = status_code
            if status_code != 'pending':
                req.processed_by = request.user
                req.processed_date = timezone.now()
            req.save()
            updated_count += 1
        self.message_user(request, f'{updated_count} запросов МБА отмечено как "{status_name}".')

    def mark_approved(self, request, queryset):
        self.mark_status(request, queryset, 'approved', 'Одобрен')
    mark_approved.short_description = "Отметить статус: Одобрен"

    def mark_rejected(self, request, queryset):
        self.mark_status(request, queryset, 'rejected', 'Отклонен')
    mark_rejected.short_description = "Отметить статус: Отклонен"

    def mark_processing(self, request, queryset):
        self.mark_status(request, queryset, 'processing', 'В обработке')
    mark_processing.short_description = "Отметить статус: В обработке"

    def mark_received(self, request, queryset):
        self.mark_status(request, queryset, 'received', 'Получен (в библиотеке)')
    mark_received.short_description = "Отметить статус: Получен (в библиотеке)"

    def mark_issued(self, request, queryset):
        self.mark_status(request, queryset, 'issued', 'Выдан читателю')
    mark_issued.short_description = "Отметить статус: Выдан читателю"

    def mark_returned(self, request, queryset):
        self.mark_status(request, queryset, 'returned', 'Возвращен (читателем)')
    mark_returned.short_description = "Отметить статус: Возвращен (читателем)"

    def mark_closed(self, request, queryset):
        self.mark_status(request, queryset, 'closed', 'Закрыт')
    mark_closed.short_description = "Отметить статус: Закрыт"

@admin.register(LibraryLocation)
class LibraryLocationAdmin(admin.ModelAdmin):
    list_display = ('location_id', 'location_name', 'location_type', 'address')
    list_filter = ('location_type',)
    search_fields = ('location_name', 'address')

@admin.register(ReaderRegistration)
class ReaderRegistrationAdmin(admin.ModelAdmin):
    list_display = ('registration_id', 'reader', 'location', 'registration_date', 'registration_expiry_date')
    list_filter = ('location', 'registration_date', 'registration_expiry_date')
    search_fields = ('reader__last_name', 'reader__first_name', 'location__location_name')
    date_hierarchy = 'registration_date'
    list_select_related = ('reader', 'location', 'reader__user')
    raw_id_fields = ('reader', 'location')