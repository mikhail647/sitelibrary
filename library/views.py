from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from django.http import HttpResponse
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from .decorators import staff_required, admin_required, group_required
from .models import BookCatalog, BookLoan, BookCopy, LibraryReader, LibraryFine, CustomUser, ReaderType, BookRequest, LibraryLocation, InterlibraryRequest, StudentReader, TeacherReader
from .forms import BookLoanForm, RegistrationForm, BookRequestForm, InterlibraryRequestForm
from django.utils import timezone
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from django.contrib.auth import login, authenticate, logout
from django.views.decorators.http import require_POST
from decimal import Decimal
from django.db.models import Q, Count, Sum
import io
import os
from django.urls import reverse
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.fonts import addMapping
from django.db import transaction

@admin_required
def generate_report(request):
    """Generates a PDF report with enhanced library statistics and Cyrillic support using Times New Roman."""
    response = HttpResponse(content_type='application/pdf')
    filename = f"library_report_{datetime.now().strftime('%Y-%m-%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # --- Font Setup for Cyrillic using Standard Times New Roman ---
    # ReportLab has built-in support for standard PostScript fonts like Times New Roman
    font_name = 'Times-Roman'
    font_name_bold = 'Times-Bold'
    font_name_italic = 'Times-Italic'
    font_name_bold_italic = 'Times-BoldItalic'

    # Registering standard fonts isn't strictly necessary but ensures mappings work
    # No TTF files needed here
    try:
        # Ensure the standard fonts are mapped correctly for ReportLab's style system
        # pdfmetrics.registerFont(pdfmetrics.Font(font_name)) # Removed - Not needed for standard fonts
        # pdfmetrics.registerFont(pdfmetrics.Font(font_name_bold)) # Removed
        # pdfmetrics.registerFont(pdfmetrics.Font(font_name_italic)) # Removed
        # pdfmetrics.registerFont(pdfmetrics.Font(font_name_bold_italic)) # Removed

        # Mappings are still useful for styles
        addMapping(font_name, 0, 0, font_name) # Normal
        addMapping(font_name, 1, 0, font_name_bold) # Bold
        addMapping(font_name, 0, 1, font_name_italic) # Italic
        addMapping(font_name, 1, 1, font_name_bold_italic) # BoldItalic
    except Exception as e:
        # This is unlikely to fail for standard fonts, but good practice
        print(f"Warning: Could not map standard Times fonts ({e}). PDF might have font issues.")
        # Fallback to Helvetica if something unexpected happens
        font_name = 'Helvetica'
        font_name_bold = 'Helvetica-Bold'
        font_name_italic = 'Helvetica-Oblique'
        font_name_bold_italic = 'Helvetica-BoldOblique'
        addMapping('Helvetica', 0, 0, font_name)
        addMapping('Helvetica', 1, 0, font_name_bold)
        addMapping('Helvetica', 0, 1, font_name_italic)
        addMapping('Helvetica', 1, 1, font_name_bold_italic)

    # --- Styles using the registered font ---
    styles = getSampleStyleSheet()
    # Update styles to use the Times New Roman font names
    styles['h1'].fontName = font_name_bold
    styles['h2'].fontName = font_name_bold
    styles['h3'].fontName = font_name_bold
    styles['Normal'].fontName = font_name
    styles['Bullet'].fontName = font_name

    doc = SimpleDocTemplate(response, pagesize=A4)
    story = []

    # Use styles defined above
    title_style = styles['h1']
    title_style.alignment = 1 # Center align
    story.append(Paragraph(f"Отчет библиотеки по состоянию на {datetime.now().strftime('%Y-%m-%d %H:%M')}", title_style))
    story.append(Spacer(1, 0.3*inch))

    h2_style = styles['h2']
    h3_style = styles['h3']
    normal_style = styles['Normal']

    # Updated base table style using the font name
    base_table_style = [('GRID', (0,0), (-1,-1), 1, colors.darkgrey),
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ('FONTNAME', (0,0), (-1,-1), font_name)] # Apply normal font to all cells
    # Header specific style using bold font
    table_header_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), font_name_bold), # Use bold font for header
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
    ])

    # --- User Statistics ---
    story.append(Paragraph("Пользователи и Читатели", h2_style))
    total_users = CustomUser.objects.count()
    active_users = CustomUser.objects.filter(is_active=True).count()
    staff_users = CustomUser.objects.filter(role__in=['staff', 'admin'], is_active=True).count()
    total_readers = LibraryReader.objects.count()
    active_readers = LibraryReader.objects.filter(reader_status='active').count()
    suspended_readers = LibraryReader.objects.filter(reader_status='suspended').count()

    user_data = [
        ['Общее число пользователей', total_users],
        ['Активных пользователей', active_users],
        ['Активных сотрудников/админов', staff_users],
        ['Всего читательских билетов', total_readers],
        ['Активных читателей', active_readers],
        ['Приостановленных читателей', suspended_readers],
    ]
    user_table = Table(user_data, colWidths=[4*inch, 1.5*inch])
    user_table.setStyle(TableStyle(base_table_style))
    user_table.setStyle(table_header_style)
    story.append(user_table)
    story.append(Spacer(1, 0.2*inch))

    # --- Book Statistics ---
    story.append(Paragraph("Книжный фонд", h2_style))
    total_titles = BookCatalog.objects.count()
    total_copies = BookCopy.objects.count()
    copies_by_status = BookCopy.objects.values('copy_status').annotate(count=Count('copy_id')).order_by()
    # Convert status keys to display names if possible
    status_map = dict(BookCopy.STATUS_CHOICES)
    book_data = [
        ['Всего наименований книг', total_titles],
        ['Всего экземпляров', total_copies],
    ]
    book_data.extend([ [f" - Статус '{status_map.get(item['copy_status'], item['copy_status'])}'", item['count']] for item in copies_by_status])

    book_table = Table(book_data, colWidths=[4*inch, 1.5*inch])
    book_table.setStyle(TableStyle(base_table_style))
    book_table.setStyle(table_header_style)
    story.append(book_table)
    story.append(Spacer(1, 0.2*inch))

    # --- Loan Statistics ---
    story.append(Paragraph("Выдачи книг", h2_style))
    active_loans = BookLoan.objects.filter(loan_status='active').count()
    overdue_loans = BookLoan.objects.filter(loan_status='overdue').count()
    returned_loans_total = BookLoan.objects.filter(loan_status='returned').count()
    # Example: Loans in the last 30 days
    recent_loans = BookLoan.objects.filter(loan_date__gte=timezone.now().date() - timedelta(days=30)).count()

    loan_data = [
        ['Активные выдачи', active_loans],
        ['Просроченные выдачи', overdue_loans],
        ['Всего возвращено (история)', returned_loans_total],
        ['Выдано за последние 30 дней', recent_loans],
    ]
    loan_table = Table(loan_data, colWidths=[4*inch, 1.5*inch])
    loan_table.setStyle(TableStyle(base_table_style))
    loan_table.setStyle(table_header_style)
    story.append(loan_table)
    story.append(Spacer(1, 0.2*inch))

    # --- Fine Statistics ---
    story.append(Paragraph("Штрафы", h2_style))
    pending_fines_count = LibraryFine.objects.filter(fine_status='pending').count()
    pending_fines_sum = LibraryFine.objects.filter(fine_status='pending').aggregate(total=Sum('fine_amount'))['total'] or Decimal('0.00')
    paid_fines_count = LibraryFine.objects.filter(fine_status='paid').count()
    paid_fines_sum = LibraryFine.objects.filter(fine_status='paid').aggregate(total=Sum('fine_amount'))['total'] or Decimal('0.00')

    fine_data = [
        ['Неоплаченные штрафы (кол-во)', pending_fines_count],
        ['Неоплаченные штрафы (сумма)', f"{pending_fines_sum:.2f} руб."],
        ['Оплаченные штрафы (кол-во)', paid_fines_count],
        ['Оплаченные штрафы (сумма)', f"{paid_fines_sum:.2f} руб."],
    ]
    fine_table = Table(fine_data, colWidths=[4*inch, 1.5*inch])
    fine_table.setStyle(TableStyle(base_table_style))
    fine_table.setStyle(table_header_style)
    story.append(fine_table)
    story.append(Spacer(1, 0.2*inch))

    # --- Request Statistics ---
    story.append(Paragraph("Запросы пользователей на книги", h2_style))
    requests_by_status = BookRequest.objects.values('status').annotate(count=Count('request_id')).order_by()
    request_status_map = dict(BookRequest.STATUS_CHOICES)
    request_data = [[f"Статус '{request_status_map.get(item['status'], item['status'])}'", item['count']] for item in requests_by_status]
    if not request_data:
        story.append(Paragraph("Запросов пока не было.", normal_style))
    else:
        request_table = Table(request_data, colWidths=[4*inch, 1.5*inch])
        request_table.setStyle(TableStyle(base_table_style))
        request_table.setStyle(table_header_style)
        story.append(request_table)
        story.append(Spacer(1, 0.2*inch))

    # REMOVED Overdue Loans List Section

    doc.build(story)
    return response

def home_redirect(request):
    """Перенаправляет пользователя на соответствующую страницу в зависимости от роли"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.user.role == 'admin':
        return redirect('admin_dashboard')
    elif request.user.role == 'staff':
        return redirect('staff_dashboard')
    else:
        return redirect('user_dashboard')

@login_required
def user_dashboard(request):
    """Displays the book catalog for regular users."""
    available_books = BookCatalog.objects.filter(
        copies__copy_status='available'
    ).prefetch_related('authors').distinct().order_by('book_title')
    context = {'books': available_books}
    return render(request, 'user/dashboard.html', context)

@staff_required
def staff_dashboard(request):
    """Dashboard for staff members."""
    active_loans_count = BookLoan.objects.filter(loan_status='active').count()
    overdue_loans_count = BookLoan.objects.filter(loan_status='overdue').count()
    available_copies_count = BookCopy.objects.filter(copy_status='available').count()
    pending_fines_count = LibraryFine.objects.filter(fine_status='pending').count()
    context = {
        'active_loans_count': active_loans_count,
        'overdue_loans_count': overdue_loans_count,
        'available_copies_count': available_copies_count,
        'pending_fines_count': pending_fines_count,
    }
    return render(request, 'staff/dashboard.html', context)

@admin_required
def admin_dashboard(request):
    """Панель администратора"""
    total_users = CustomUser.objects.count()
    active_users = CustomUser.objects.filter(is_active=True).count()
    pending_activations = CustomUser.objects.filter(is_active=False, role__in=['admin', 'staff']).count()
    total_books = BookCatalog.objects.count()
    active_loans = BookLoan.objects.filter(loan_status='active').count()
    overdue_loans = BookLoan.objects.filter(loan_status='overdue').count()
    
    context = {
        'total_users': total_users,
        'active_users': active_users,
        'pending_activations': pending_activations,
        'total_books': total_books,
        'active_loans': active_loans,
        'overdue_loans': overdue_loans,
    }
    return render(request, 'admin/dashboard.html', context)

@staff_required
def issue_book(request):
    """Handles the book issuing process."""
    if request.method == 'POST':
        form = BookLoanForm(request.POST)
        if form.is_valid():
            loan = form.save(commit=False)
            reader = loan.reader
            copy = loan.copy

            # --- Permission Checks ---
            # 1. Check if the reader is allowed to take books home (per-reader setting overrides type)
            if not reader.can_take_books_home:
                 messages.error(request, f"Читателю '{reader}' не разрешено брать книги на дом (индивидуальная настройка). Выдача невозможна.")
                 return render(request, 'staff/issue_book.html', {'form': form})
            
            # 2. Check if reader type allows loan (redundant if can_take_books_home is False, but good secondary check)
            # if not reader.reader_type.can_use_loan:
            #     messages.error(request, f"Читатель категории '{reader.reader_type}' не может брать книги на абонемент. Выдача невозможна.")
            #     return render(request, 'staff/issue_book.html', {'form': form})

            # 3. Check reader status
            if reader.reader_status != 'active':
                status_display = dict(LibraryReader.STATUS_CHOICES).get(reader.reader_status, reader.reader_status)
                messages.error(request, f"Статус читателя: '{status_display}'. Выдача невозможна.")
                return render(request, 'staff/issue_book.html', {'form': form})

            # 4. Check loan limit
            active_loans_count = BookLoan.objects.filter(reader=reader, loan_status__in=['active', 'overdue']).count()
            if active_loans_count >= reader.reader_type.max_books_allowed:
                messages.error(request, f"Читатель достиг лимита ({reader.reader_type.max_books_allowed}) активных выдач.")
                return render(request, 'staff/issue_book.html', {'form': form})

            # 5. Check copy status
            if copy.copy_status != 'available':
                messages.error(request, f"Экземпляр '{copy}' недоступен для выдачи (статус: {copy.get_copy_status_display()}).")
                return render(request, 'staff/issue_book.html', {'form': form})
            # --- End Permission Checks ---

            # Proceed with loan creation
            loan.location = copy.location
            loan.loan_date = timezone.now().date()
            loan.due_date = loan.loan_date + timedelta(days=reader.reader_type.loan_period_days)
            loan.loan_status = 'active'
            loan.save()

            copy.copy_status = 'issued'
            copy.save()

            reader_full_name = f"{reader.first_name} {reader.last_name}"
            if reader.user:
                reader_full_name = reader.user.get_full_name() or reader.user.username
            messages.success(request, f"Книга '{copy.book.book_title}' (Инв. №{copy.inventory_number}) успешно выдана читателю {reader_full_name}.")
            return redirect('staff_active_loans')
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = BookLoanForm()

    return render(request, 'staff/issue_book.html', {'form': form})

@staff_required
def active_loans(request):
    """Displays a list of active and overdue loans with search and filtering."""
    loans_query = BookLoan.objects.filter(loan_status__in=['active', 'overdue']).select_related(
        'reader', 'copy__book', 'copy__location', 'reader__user'
    )

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        loans_query = loans_query.filter(
            Q(reader__first_name__icontains=search_query) |
            Q(reader__last_name__icontains=search_query) |
            Q(reader__library_card_number__icontains=search_query) |
            Q(copy__book__book_title__icontains=search_query) |
            Q(copy__inventory_number__icontains=search_query) |
            Q(reader__user__username__icontains=search_query) # Search by username if reader linked to user
        ).distinct()

    # Filtering by status (optional)
    status_filter = request.GET.get('status', '')
    if status_filter in ['active', 'overdue']:
        loans_query = loans_query.filter(loan_status=status_filter)

    loans = loans_query.order_by('due_date')

    context = {
        'loans': loans,
        'search_query': search_query, # Pass query back to template
        'status_filter': status_filter, # Pass filter back to template
    }
    return render(request, 'staff/active_loans.html', context)

@staff_required
def return_book(request, loan_id):
    """Handles the book returning process and creates fines if overdue."""
    loan = get_object_or_404(BookLoan, pk=loan_id, loan_status__in=['active', 'overdue'])
    copy = loan.copy
    reader = loan.reader

    is_overdue = loan.due_date < timezone.now().date()

    loan.return_date = timezone.now().date()
    loan.loan_status = 'returned'
    loan.save()

    copy.copy_status = 'available'
    copy.save()

    if is_overdue:
        overdue_days = (loan.return_date - loan.due_date).days
        fine_per_day = reader.reader_type.fine_per_day if hasattr(reader.reader_type, 'fine_per_day') else Decimal('10.00')
        fine_amount = Decimal(overdue_days) * fine_per_day

        if fine_amount > 0:
            fine, created = LibraryFine.objects.get_or_create(
                reader=reader,
                loan=loan,
                fine_reason='overdue',
                defaults={
                    'fine_amount': fine_amount,
                    'fine_status': 'pending',
                    'fine_date': timezone.now().date()
                }
            )
            if created:
                messages.warning(request, f"Книга '{copy.book.book_title}' возвращена с просрочкой ({overdue_days} дн.). Начислен штраф: {fine_amount:.2f} руб.")
            else:
                messages.warning(request, f"Книга '{copy.book.book_title}' возвращена с просрочкой. Штраф ({fine.fine_amount:.2f} руб.) уже был зарегистрирован.")
        else:
             messages.success(request, f"Книга '{copy.book.book_title}' (Инв. №{copy.inventory_number}) успешно возвращена (без штрафа за просрочку).")
    else:
        messages.success(request, f"Книга '{copy.book.book_title}' (Инв. №{copy.inventory_number}) успешно возвращена.")

    return redirect('staff_active_loans')

@staff_required
@require_POST
def return_multiple_books(request):
    """Handles returning multiple books selected via checkboxes."""
    loan_ids = request.POST.getlist('loan_ids') # Get list of selected loan IDs

    if not loan_ids:
        messages.error(request, "Не выбрано ни одной выдачи для возврата.")
        return redirect('staff_active_loans')

    returned_count = 0
    fine_count = 0
    error_count = 0

    # Process each selected loan ID
    loans_to_return = BookLoan.objects.filter(pk__in=loan_ids, loan_status__in=['active', 'overdue'])

    for loan in loans_to_return:
        try:
            copy = loan.copy
            reader = loan.reader
            is_overdue = loan.due_date < timezone.now().date()

            # Update Loan status
            loan.return_date = timezone.now().date()
            loan.loan_status = 'returned'
            loan.save()

            # Update Copy status
            copy.copy_status = 'available'
            copy.save()

            returned_count += 1

            # Create Fine if overdue
            if is_overdue:
                overdue_days = (loan.return_date - loan.due_date).days
                fine_per_day = Decimal('10.00') # Default fine, consider getting from ReaderType
                if hasattr(reader.reader_type, 'fine_per_day'):
                    fine_per_day = reader.reader_type.fine_per_day

                fine_amount = Decimal(overdue_days) * fine_per_day
                if fine_amount > 0:
                    fine, created = LibraryFine.objects.get_or_create(
                        reader=reader,
                        loan=loan,
                        fine_reason='overdue',
                        defaults={
                            'fine_amount': fine_amount,
                            'fine_status': 'pending',
                            'fine_date': timezone.now().date()
                        }
                    )
                    if created:
                        fine_count += 1
                        # Optionally add individual messages, but might be too many
                        # messages.warning(request, f"Штраф {fine_amount:.2f} руб. начислен для выдачи №{loan.loan_id}")
        except Exception as e:
            # Log the error and inform the staff
            print(f"Error returning loan ID {loan.loan_id}: {e}") # Basic logging
            messages.error(request, f"Ошибка при возврате выдачи №{loan.loan_id}. Обратитесь к администратору.")
            error_count += 1

    # Display summary message
    if returned_count > 0:
        msg = f"Успешно возвращено книг: {returned_count}." 
        if fine_count > 0:
            msg += f" Начислено штрафов за просрочку: {fine_count}."
        messages.success(request, msg)
    if error_count > 0:
        messages.error(request, f"Не удалось вернуть книг: {error_count}.")

    return redirect('staff_active_loans')

# Registration View
def register(request):
    if request.user.is_authenticated:
        messages.warning(request, 'Вы уже вошли в систему.')
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        elif request.user.role == 'staff':
            return redirect('staff_dashboard')
        elif request.user.role == 'user':
            return redirect('user_dashboard')
        else:
            return redirect('home')

    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])

            # Determine Reader Type and Role based on form input (e.g., hidden field or logic)
            # For now, we'll hardcode a basic logic for demonstration
            # Assume we have a way to determine intended_reader_type_name
            # A dropdown for ReaderType might be better in the form.
            # Example: Determine based on email domain or a selected profile type
            
            # Simplified Example: Let's add a basic selection (not ideal UX)
            # This should ideally come from the form itself
            profile_type_selection = request.POST.get('profile_type', 'student') # Need to add this to template

            reader_type = None
            user_role = 'user' # Default role
            needs_activation = False
            reader_profile_model = None
            profile_data = {}

            try:
                if profile_type_selection == 'student':
                    reader_type = ReaderType.objects.get(type_name='Студент')
                    reader_profile_model = StudentReader
                    profile_data = {
                        'faculty': form.cleaned_data.get('faculty'),
                        'study_group': form.cleaned_data.get('study_group'),
                        'course_number': form.cleaned_data.get('course_number'),
                    }
                elif profile_type_selection == 'teacher':
                    reader_type = ReaderType.objects.get(type_name='Преподаватель')
                    reader_profile_model = TeacherReader
                    user_role = 'user' # Or 'staff' depending on policy
                    profile_data = {
                        'department': form.cleaned_data.get('department'),
                        'position': form.cleaned_data.get('position'),
                        'academic_degree': form.cleaned_data.get('academic_degree'),
                        'academic_title': form.cleaned_data.get('academic_title'),
                    }
                elif profile_type_selection == 'staff': # Explicit staff registration
                    reader_type = ReaderType.objects.get(type_name='Сотрудник')
                    reader_profile_model = TeacherReader # Staff use Teacher profile for department/position
                    user_role = 'staff'
                    needs_activation = True
                    profile_data = { # Staff might fill department/position too
                        'department': form.cleaned_data.get('department'),
                        'position': form.cleaned_data.get('position'),
                    }
                else: # Default to 'Обычный читатель' if unknown type
                    reader_type = ReaderType.objects.get(type_name='Обычный читатель')
                    user_role = 'user'

            except ReaderType.DoesNotExist:
                 messages.error(request, f'Ошибка регистрации: Не найден тип читателя для профиля "{profile_type_selection}". Обратитесь к администратору.')
                 return render(request, 'registration/register.html', {'form': form})

            user.role = user_role
            user.is_active = not needs_activation # Activate immediately unless staff/admin
            user.save()

            # Create LibraryReader record
            try:
                card_prefix = reader_type.type_name[:3].upper()
                card_number = f"{card_prefix}-{user.id:05d}-{timezone.now().strftime('%y%m')}"
                library_reader = LibraryReader.objects.create(
                    user=user,
                    reader_type=reader_type,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    library_card_number=card_number,
                    registration_date=timezone.now().date(),
                    reader_status='active' # Start as active, admin can suspend if needed
                    # can_take_books_home is determined by reader_type.can_use_loan by default
                )

                # Create specific profile (Student/Teacher) if applicable
                if reader_profile_model and profile_data:
                    # Filter out None values before creating profile
                    filtered_profile_data = {k: v for k, v in profile_data.items() if v is not None and v != ''}
                    if filtered_profile_data: # Only create if there's data
                        reader_profile_model.objects.create(
                            reader=library_reader, 
                            **filtered_profile_data
                        )

                if needs_activation:
                    messages.success(request, 'Регистрация прошла успешно! Ваша учетная запись сотрудника ожидает активации администратором.')
                else:
                    messages.success(request, 'Регистрация прошла успешно! Теперь вы можете войти в систему.')
                return redirect('login')

            except Exception as e: # Catch potential errors during reader/profile creation
                # Clean up created user if reader creation failed
                user.delete()
                messages.error(request, f'Произошла ошибка при создании профиля читателя: {e}. Попробуйте еще раз или обратитесь к администратору.')
                # Log the error e
                print(f"Error creating reader profile: {e}")
                return render(request, 'registration/register.html', {'form': form})

        else:
            # Collect and display form errors
            error_list = []
            for field, errors in form.errors.items():
                label = form.fields[field].label if field in form.fields else field.replace('_', ' ').capitalize()
                error_list.append(f"{label}: {errors.as_text()}")
            messages.error(request, "Пожалуйста, исправьте ошибки в форме: \n" + "\n".join(error_list))
            # Re-render the form with errors
            return render(request, 'registration/register.html', {'form': form})

    else: # GET request
        form = RegistrationForm()
    # Pass initial context (empty form on GET)
    return render(request, 'registration/register.html', {'form': form})

def is_admin_user(user):
    return user.is_authenticated and user.role == 'admin'

@user_passes_test(is_admin_user)
def activate_users_list(request):
    """Displays a list of inactive staff/admin users for activation."""
    users_to_activate = CustomUser.objects.filter(
        is_active=False, role__in=['staff', 'admin']
    ).order_by('date_joined')
    context = {'users_to_activate': users_to_activate}
    return render(request, 'admin/activate_users.html', context)

@user_passes_test(is_admin_user)
@require_POST
def activate_user(request, user_id):
    """Activates a specific user."""
    user_to_activate = get_object_or_404(CustomUser, pk=user_id, is_active=False, role__in=['staff', 'admin'])
    user_to_activate.is_active = True
    user_to_activate.save()

    try:
        reader_profile = LibraryReader.objects.get(user=user_to_activate)
        if reader_profile.reader_status != 'active':
            reader_profile.reader_status = 'active'
            reader_profile.save()
    except LibraryReader.DoesNotExist:
        pass

    messages.success(request, f"Пользователь '{user_to_activate.username}' успешно активирован.")
    return redirect('admin_activate_users')

@staff_required
def manage_fines(request):
    """Displays pending fines and allows marking them as paid, with search/filter."""
    fines_query = LibraryFine.objects.filter(fine_status='pending').select_related(
        'reader', 'loan', 'reader__user', 'loan__copy__book'
    )

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        fines_query = fines_query.filter(
            Q(reader__first_name__icontains=search_query) |
            Q(reader__last_name__icontains=search_query) |
            Q(reader__library_card_number__icontains=search_query) |
            Q(loan__copy__book__book_title__icontains=search_query) |
            Q(loan__loan_id__icontains=search_query) |
            Q(reader__user__username__icontains=search_query)
        ).distinct()

    # Filtering by reason (optional)
    reason_filter = request.GET.get('reason', '')
    if reason_filter in [choice[0] for choice in LibraryFine.REASON_CHOICES]:
        fines_query = fines_query.filter(fine_reason=reason_filter)

    pending_fines = fines_query.order_by('fine_date')

    context = {
        'fines': pending_fines,
        'search_query': search_query,
        'reason_filter': reason_filter,
        'reason_choices': LibraryFine.REASON_CHOICES # Pass choices to template
    }
    return render(request, 'staff/manage_fines.html', context)

@staff_required
@require_POST
def pay_fine(request, fine_id):
    """Marks a fine as paid."""
    fine_to_pay = get_object_or_404(LibraryFine, pk=fine_id, fine_status='pending')
    fine_to_pay.fine_status = 'paid'
    fine_to_pay.save()

    reader_name = f"{fine_to_pay.reader.first_name} {fine_to_pay.reader.last_name}"
    if fine_to_pay.reader.user:
        reader_name = fine_to_pay.reader.user.get_full_name() or fine_to_pay.reader.user.username

    messages.success(request, f"Штраф №{fine_to_pay.fine_id} для {reader_name} отмечен как оплаченный.")
    return redirect('manage_fines')

@login_required
def my_fines(request):
    """Displays pending fines for the current logged-in user."""
    user_fines = LibraryFine.objects.none()
    reader = None
    try:
        reader = LibraryReader.objects.get(user=request.user)
        user_fines = LibraryFine.objects.filter(reader=reader, fine_status='pending').select_related(
            'loan__copy__book'
        ).order_by('fine_date')
    except LibraryReader.DoesNotExist:
        messages.info(request, "Профиль читателя не найден. Штрафы не могут быть отображены.")
    except AttributeError:
        messages.error(request, "Ошибка при доступе к данным пользователя.")

    context = {'fines': user_fines, 'reader': reader}
    return render(request, 'user/my_fines.html', context)

@staff_required
def manage_requests(request):
    """Displays pending book requests for staff approval/rejection."""
    requests_query = BookRequest.objects.filter(status='pending').select_related(
        'user', 'book', 'requested_location'
    )

    # Filtering by location
    location_filter = request.GET.get('location', '')
    # Store selected location in session for persistence
    if location_filter:
        request.session['staff_location_filter'] = location_filter
    elif 'staff_location_filter' in request.session:
        location_filter = request.session['staff_location_filter'] # Use stored filter

    if location_filter:
        requests_query = requests_query.filter(requested_location__location_id=location_filter)

    pending_requests = requests_query.order_by('request_date')
    locations = LibraryLocation.objects.all()

    context = {
        'requests': pending_requests,
        'locations': locations,
        'location_filter': location_filter, # Pass filter back to template
    }
    return render(request, 'staff/manage_requests.html', context)

@staff_required
@require_POST
def approve_request(request, request_id):
    """Approve a book request."""
    book_request = get_object_or_404(BookRequest, pk=request_id, status='pending')
    book_request.status = 'approved'
    book_request.processed_by = request.user
    book_request.processed_date = timezone.now()
    book_request.save()
    messages.success(request, f"Запрос №{book_request.request_id} на книгу '{book_request.book.book_title}' одобрен.")
    # Redirect back with filter preserved if possible
    redirect_url = reverse('staff_manage_requests')
    if 'staff_location_filter' in request.session:
        redirect_url += f"?location={request.session['staff_location_filter']}"
    return redirect(redirect_url)

@staff_required
@require_POST
def reject_request(request, request_id):
    """Reject a book request."""
    book_request = get_object_or_404(BookRequest, pk=request_id, status='pending')
    # Optional: Add logic to capture rejection reason from a form/modal
    rejection_notes = request.POST.get('notes', 'Причина не указана.')
    book_request.status = 'rejected'
    book_request.processed_by = request.user
    book_request.processed_date = timezone.now()
    book_request.notes = rejection_notes # Store rejection reason
    book_request.save()
    messages.warning(request, f"Запрос №{book_request.request_id} на книгу '{book_request.book.book_title}' отклонен.")
    # Redirect back with filter preserved if possible
    redirect_url = reverse('staff_manage_requests')
    if 'staff_location_filter' in request.session:
        redirect_url += f"?location={request.session['staff_location_filter']}"
    return redirect(redirect_url)

# --- User Book Request Views --- #

@login_required
def request_book(request):
    """Handles the user's book request form submission."""
    try:
        reader_profile = LibraryReader.objects.get(user=request.user)
    except LibraryReader.DoesNotExist:
        messages.error(request, "Ваш профиль читателя не найден. Невозможно создать запрос.")
        return redirect('user_dashboard')

    if request.method == 'POST':
        form = BookRequestForm(request.POST)
        if form.is_valid():
            location = form.cleaned_data['requested_location']
            book_to_request = form.cleaned_data['book']

            # Check if reader can take books home if location is a loan point
            # Prioritize the individual setting
            if location.location_type == 'loan' and not reader_profile.can_take_books_home:
                messages.error(request,
                                 f"Вам не разрешено заказывать книги на абонемент '{location.location_name}' (индивидуальная настройка). "
                                 f"Пожалуйста, выберите читальный зал.")
                return render(request, 'user/request_book.html', {'form': form})
            
            # Optional secondary check (less critical if individual setting is checked first)
            # elif location.location_type == 'loan' and not reader_profile.reader_type.can_use_loan:
            #     messages.error(request,
            #                      f"Читатели вашей категории ('{reader_profile.reader_type}') не могут заказывать книги на абонемент '{location.location_name}'. "
            #                      f"Пожалуйста, выберите читальный зал.")
            #     return render(request, 'user/request_book.html', {'form': form})

            # Check if user already has an active request for this book
            existing_request = BookRequest.objects.filter(
                user=request.user,
                book=book_to_request,
                status__in=['pending', 'approved']
            ).exists()

            if existing_request:
                messages.warning(request, f"У вас уже есть активный запрос на книгу '{book_to_request.book_title}'.")
            else:
                book_request = form.save(commit=False)
                book_request.user = request.user
                book_request.save()
                messages.success(request, f"Ваш запрос на книгу '{book_request.book.book_title}' в пункт '{location.location_name}' успешно создан.")
                return redirect('user_my_requests')
    else: # GET request
        form = BookRequestForm()

    context = {'form': form}
    return render(request, 'user/request_book.html', context)


@login_required
def my_requests(request):
    """Displays the current user's book requests."""
    user_requests = BookRequest.objects.filter(user=request.user).select_related(
        'book', 'requested_location', 'loan'
    ).order_by('-request_date')

    context = {'requests': user_requests}
    return render(request, 'user/my_requests.html', context)

# --- Interlibrary Loan (ILL / МБА) Views for User --- #

@login_required
def my_interlibrary_requests(request):
    """Displays the current user's Interlibrary Loan requests."""
    ill_requests = InterlibraryRequest.objects.none()
    reader = None
    try:
        # Ensure the user has a reader profile to link requests to
        reader = LibraryReader.objects.get(user=request.user)
        ill_requests = InterlibraryRequest.objects.filter(reader=reader).select_related(
            'book', 'processed_by'
        ).order_by('-request_date')
    except LibraryReader.DoesNotExist:
        messages.warning(request, "Профиль читателя не найден. Запросы МБА недоступны.")
    except AttributeError:
        messages.error(request, "Ошибка при доступе к данным пользователя.")

    context = {'requests': ill_requests, 'reader': reader}
    return render(request, 'user/my_ill_requests.html', context)

@login_required
def create_interlibrary_request(request):
    """Handles the creation of a new Interlibrary Loan request."""
    try:
        reader_profile = LibraryReader.objects.get(user=request.user)
    except LibraryReader.DoesNotExist:
        messages.error(request, "Профиль читателя не найден. Невозможно создать запрос МБА.")
        return redirect('user_dashboard')

    if request.method == 'POST':
        form = InterlibraryRequestForm(request.POST)
        if form.is_valid():
            # Check if an active ILL request for this book already exists
            existing_request = InterlibraryRequest.objects.filter(
                reader=reader_profile,
                book=form.cleaned_data['book'],
                request_status__in=['pending', 'approved', 'processing', 'received', 'issued']
            ).exists()

            if existing_request:
                messages.warning(request, f"У вас уже есть активный запрос МБА на книгу '{form.cleaned_data['book'].book_title}'.")
            else:
                ill_request = form.save(commit=False)
                ill_request.reader = reader_profile
                # request_date and status have defaults set in the model
                ill_request.save()
                messages.success(request, f"Ваш запрос МБА на книгу '{ill_request.book.book_title}' успешно создан.")
                return redirect('user_my_ill_requests')
        # If form is not valid, it will fall through
    else: # GET request
        form = InterlibraryRequestForm()

    context = {'form': form}
    return render(request, 'user/create_ill_request.html', context)

# --- Interlibrary Loan (ILL / МБА) Views for Staff --- #

@staff_required
def staff_manage_ill_requests(request):
    """Displays ILL requests for staff management."""
    # Initially filter by statuses that require staff action
    default_statuses = ['pending', 'approved', 'processing', 'received']
    status_filter = request.GET.getlist('status', default_statuses)

    ill_requests_query = InterlibraryRequest.objects.select_related(
        'reader', 'book', 'processed_by', 'reader__user'
    )

    # Filter by selected statuses
    if status_filter:
        ill_requests_query = ill_requests_query.filter(request_status__in=status_filter)

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        ill_requests_query = ill_requests_query.filter(
            Q(reader__first_name__icontains=search_query) |
            Q(reader__last_name__icontains=search_query) |
            Q(reader__library_card_number__icontains=search_query) |
            Q(book__book_title__icontains=search_query) |
            Q(request_id__icontains=search_query) |
            Q(reader__user__username__icontains=search_query)
        ).distinct()

    ill_requests = ill_requests_query.order_by('request_date')
    status_choices = InterlibraryRequest.STATUS_CHOICES

    context = {
        'requests': ill_requests,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': status_choices,
    }
    return render(request, 'staff/manage_ill_requests.html', context)

@staff_required
@require_POST
def update_ill_request_status(request, request_id):
    """Updates the status of an ILL request."""
    ill_request = get_object_or_404(InterlibraryRequest, pk=request_id)
    new_status = request.POST.get('status')

    if not new_status or new_status not in [choice[0] for choice in InterlibraryRequest.STATUS_CHOICES]:
        messages.error(request, "Недопустимый статус.")
        return redirect('staff_manage_ill_requests')

    # Basic update logic, can be expanded with checks
    ill_request.request_status = new_status
    ill_request.processed_by = request.user
    ill_request.processed_date = timezone.now()

    # Optional: Add staff notes if provided
    staff_notes = request.POST.get('staff_notes')
    if staff_notes:
        ill_request.staff_notes = staff_notes

    ill_request.save()

    status_display = dict(InterlibraryRequest.STATUS_CHOICES).get(new_status, new_status)
    messages.success(request, f"Статус запроса МБА №{ill_request.request_id} обновлен на '{status_display}'.")

    # Redirect back, possibly preserving filters (more complex)
    # For simplicity, redirecting to the base management view
    return redirect('staff_manage_ill_requests')

@staff_required
@require_POST # Use POST for actions that change state
def staff_check_suspensions(request):
    """Checks for expired suspensions and reactivates readers."""
    today = timezone.now().date()
    updated_count = 0
    try:
        with transaction.atomic(): # Ensure all updates succeed or fail together
            expired_suspensions = LibraryReader.objects.select_for_update().filter(
                reader_status='suspended',
                suspension_end_date__isnull=False,
                suspension_end_date__lt=today
            )
            
            readers_updated_info = [] # Optional: Store info for message
            for reader in expired_suspensions:
                reader.reader_status = 'active'
                reader.suspension_end_date = None
                reader.save()
                updated_count += 1
                readers_updated_info.append(f"{reader.last_name} {reader.first_name}")
        
        if updated_count > 0:
            # reader_list = ", ".join(readers_updated_info)
            messages.success(request, f'Проверка завершена. Активировано читателей: {updated_count}.') #{reader_list}')
        else:
            messages.info(request, 'Проверка завершена. Читателей с истекшим сроком приостановки не найдено.')
            
    except Exception as e:
        messages.error(request, f'Ошибка при проверке приостановок: {e}')
        # Log the error e
        print(f"Error checking suspensions: {e}")

    # Redirect back to the dashboard or another appropriate staff page
    return redirect('staff_dashboard')