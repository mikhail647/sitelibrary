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
from django.conf import settings # Import settings

@admin_required
def generate_report(request):
    """Generates a PDF report with enhanced library statistics and Cyrillic support using embedded Times New Roman fonts."""
    response = HttpResponse(content_type='application/pdf')
    filename = f"library_report_{datetime.now().strftime('%Y-%m-%d')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'

    # --- Font Setup for Cyrillic using embedded Times New Roman TTFs ---
    font_name = 'TimesNewRomanPSMT' # Custom name for your regular TTF
    font_name_italic = 'TimesNewRomanPSMT-Italic' # Custom name for your italic TTF
    font_name_bold = 'TimesNewRomanPSMT-Bold' # Custom name for your bold TTF
    # Assume BoldItalic maps to Bold for now, unless you have a specific TTF
    font_name_bold_italic = 'TimesNewRomanPSMT-Bold' 

    # Paths to your uploaded TTF files
    font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'timesnewromanpsmt.ttf')
    font_path_italic = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'timesnewromanps_italicmt.ttf')
    font_path_bold = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'timesbd.ttf')

    # --- DEBUGGING --- 
    print(f"[PDF Report] Attempting to load font from: {font_path}")
    font_exists = os.path.exists(font_path)
    print(f"[PDF Report] Font file exists at path: {font_exists}")
    print(f"[PDF Report] Attempting to load italic font from: {font_path_italic}")
    font_italic_exists = os.path.exists(font_path_italic)
    print(f"[PDF Report] Italic font file exists at path: {font_italic_exists}")
    print(f"[PDF Report] Attempting to load bold font from: {font_path_bold}")
    font_bold_exists = os.path.exists(font_path_bold)
    print(f"[PDF Report] Bold font file exists at path: {font_bold_exists}")
    # --- END DEBUGGING ---

    registered_successfully = False
    try:
        # Check if all required TTF files exist
        if font_exists and font_italic_exists and font_bold_exists:
            # Register the TTF files you provided
            pdfmetrics.registerFont(TTFont(font_name, font_path))
            pdfmetrics.registerFont(TTFont(font_name_italic, font_path_italic))
            pdfmetrics.registerFont(TTFont(font_name_bold, font_path_bold))

            # Map the base font name to the specific TTF variants
            addMapping(font_name, 0, 0, font_name) # Normal -> Your regular TTF
            addMapping(font_name, 0, 1, font_name_italic) # Italic -> Your italic TTF
            addMapping(font_name, 1, 0, font_name_bold) # Bold -> Your bold TTF
            addMapping(font_name, 1, 1, font_name_bold_italic) # BoldItalic -> Your bold TTF (as fallback)
            registered_successfully = True
            print(f"[PDF Report] Successfully registered {font_name}, {font_name_italic}, and {font_name_bold} fonts")
        else:
            missing = []
            if not font_exists: missing.append(font_path)
            if not font_italic_exists: missing.append(font_path_italic)
            if not font_bold_exists: missing.append(font_path_bold)
            print(f"[PDF Report] Font file(s) not found: {missing}. Falling back to Helvetica.")
            # No error raise here, fallback will happen

    except Exception as e:
        print(f"[PDF Report] Error registering or mapping fonts ({e}). Falling back to Helvetica.")

    # Fallback if TTF registration failed
    if not registered_successfully:
        font_name = 'Helvetica'
        font_name_bold = 'Helvetica-Bold'
        font_name_italic = 'Helvetica-Oblique'
        font_name_bold_italic = 'Helvetica-BoldOblique'
        # Ensure base Helvetica styles are used
        addMapping('Helvetica', 0, 0, font_name)
        addMapping('Helvetica', 1, 0, font_name_bold)
        addMapping('Helvetica', 0, 1, font_name_italic)
        addMapping('Helvetica', 1, 1, font_name_bold_italic)


    # --- Styles using the registered font (TimesNewRomanPSMT or Helvetica fallback) ---
    styles = getSampleStyleSheet()
    # Use the specific bold name for headers, your regular TTF name for normal text
    styles['h1'].fontName = font_name_bold
    styles['h2'].fontName = font_name_bold
    styles['h3'].fontName = font_name_bold
    styles['Normal'].fontName = font_name
    styles['Bullet'].fontName = font_name
    # If you need specific italic style:
    # styles.add(ParagraphStyle(name='ItalicStyle', parent=styles['Normal'], fontName=font_name_italic))

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
    """Handles the book issuing process, optionally pre-filled from a BookRequest."""
    book_request = None
    reader_profile = None # Define reader_profile here
    initial_data = {}
    copy_queryset = BookCopy.objects.filter(copy_status='available').select_related('book', 'location')
    request_id = request.GET.get('request_id')
    is_from_request_flag = False # Flag to pass to form

    if request_id:
        try:
            book_request = get_object_or_404(BookRequest, pk=request_id, status='approved')
            reader_profile = get_object_or_404(LibraryReader, user=book_request.user)
            initial_data = {'reader': reader_profile}
            copy_queryset = BookCopy.objects.filter(
                book=book_request.book,
                location=book_request.requested_location,
                copy_status='available'
            ).select_related('book', 'location')
            is_from_request_flag = True # Set flag for form

        except LibraryReader.DoesNotExist:
            messages.error(request, f"Не найден профиль читателя для пользователя '{book_request.user.username}', связанного с запросом №{request_id}.")
            return redirect('staff_manage_requests')
        except BookRequest.DoesNotExist:
             messages.error(request, f"Запрос №{request_id} не найден или не одобрен.")
             return redirect('staff_manage_requests')
        except Exception as e:
            messages.error(request, f"Произошла ошибка при загрузке данных из запроса №{request_id}: {e}")
            print(f"Error pre-filling issue form from request {request_id}: {e}")
            return redirect('staff_manage_requests')

    if request.method == 'POST':
        # Determine if POST is from a request
        post_request_id = request.POST.get('request_id')
        is_post_from_request = bool(post_request_id)
        form_kwargs = {
            'is_from_request': is_post_from_request,
            'copy_queryset': copy_queryset # Pass potentially filtered queryset
        }
        # If POST is from request, provide initial reader data as well
        if is_post_from_request:
            try:
                # Fetch reader again for POST context
                breq = BookRequest.objects.get(pk=post_request_id)
                reader_for_post = LibraryReader.objects.get(user=breq.user)
                form_kwargs['initial'] = {'reader': reader_for_post}
            except (BookRequest.DoesNotExist, LibraryReader.DoesNotExist):
                # Handle error case - request ID was in POST but data is missing?
                 messages.error(request, f"Ошибка: Не удалось найти данные для запроса №{post_request_id} при отправке формы.")
                 return redirect('staff_manage_requests')

        form = BookLoanForm(request.POST, **form_kwargs)

        if form.is_valid():
            loan = form.save(commit=False)
            # Fetch the reader manually if it came from a request (since it's disabled)
            if is_post_from_request:
                # We already fetched reader_for_post, use it
                loan.reader = reader_for_post
            else:
                # This case should work normally as reader is in cleaned_data
                 loan.reader = form.cleaned_data['reader']

            # Ensure copy is assigned (should be in cleaned_data)
            if 'copy' in form.cleaned_data:
                 loan.copy = form.cleaned_data['copy']
            else:
                 # This shouldn't happen if the form is valid, but as a safeguard:
                 messages.error(request, "Ошибка: Экземпляр книги не был выбран.")
                 context = {'form': form, 'request_id': post_request_id}
                 return render(request, 'staff/issue_book.html', context)

            # --- Permission Checks (Use loan.reader) ---
            if not loan.reader.can_take_books_home:
                 messages.error(request, f"Читателю '{loan.reader}' не разрешено брать книги на дом (индивидуальная настройка). Выдача невозможна.")
                 context = {'form': form, 'request_id': post_request_id}
                 return render(request, 'staff/issue_book.html', context)

            if loan.reader.reader_status != 'active':
                status_display = dict(LibraryReader.STATUS_CHOICES).get(loan.reader.reader_status, loan.reader.reader_status)
                messages.error(request, f"Статус читателя: '{status_display}'. Выдача невозможна.")
                context = {'form': form, 'request_id': post_request_id}
                return render(request, 'staff/issue_book.html', context)

            active_loans_count = BookLoan.objects.filter(reader=loan.reader, loan_status__in=['active', 'overdue']).count()
            if active_loans_count >= loan.reader.reader_type.max_books_allowed:
                messages.error(request, f"Читатель достиг лимита ({loan.reader.reader_type.max_books_allowed}) активных выдач.")
                context = {'form': form, 'request_id': post_request_id}
                return render(request, 'staff/issue_book.html', context)

            # --- Copy Status Check (Use loan.copy) ---
            if loan.copy.copy_status != 'available':
                messages.error(request, f"Экземпляр '{loan.copy}' недоступен для выдачи (статус: {loan.copy.get_copy_status_display()}).")
                context = {'form': form, 'request_id': post_request_id}
                # Re-populate form with correct queryset for copy
                if is_post_from_request:
                     try:
                         breq = BookRequest.objects.get(pk=post_request_id)
                         form.fields['copy'].queryset = BookCopy.objects.filter(
                             book=breq.book, location=breq.requested_location, copy_status='available'
                         ).select_related('book', 'location')
                         # Keep reader disabled
                         form.fields['reader'].initial = loan.reader # Set initial again for display
                         form.fields['reader'].widget.attrs['disabled'] = True
                     except (BookRequest.DoesNotExist, LibraryReader.DoesNotExist):
                          form.fields['copy'].queryset = BookCopy.objects.filter(copy_status='available').select_related('book', 'location')
                else:
                     form.fields['copy'].queryset = BookCopy.objects.filter(copy_status='available').select_related('book', 'location')
                return render(request, 'staff/issue_book.html', context)
            # --- End Permission Checks ---

            loan.location = loan.copy.location # Use copy's location
            loan.loan_date = timezone.now().date()
            loan.due_date = loan.loan_date + timedelta(days=loan.reader.reader_type.loan_period_days)
            loan.loan_status = 'active'
            loan.save()

            copy = loan.copy # Get the actual copy instance that was saved with the loan
            copy.copy_status = 'issued'
            copy.save()

            # --- Update BookRequest if issued from a request ---
            if post_request_id:
                try:
                    original_request = BookRequest.objects.get(pk=post_request_id, status='approved')
                    original_request.status = 'issued'
                    original_request.loan = loan
                    original_request.processed_by = request.user
                    original_request.processed_date = timezone.now()
                    original_request.save()
                    messages.success(request, f"Книга '{copy.book.book_title}' успешно выдана читателю {loan.reader} по запросу №{post_request_id}.")
                except BookRequest.DoesNotExist:
                    messages.warning(request, f"Книга '{copy.book.book_title}' выдана читателю {loan.reader}, но не удалось обновить исходный запрос №{post_request_id} (не найден или уже обработан).")
                except Exception as e:
                    messages.error(request, f"Книга '{copy.book.book_title}' выдана, но произошла ошибка при обновлении запроса №{post_request_id}: {e}")
                    print(f"Error updating request {post_request_id} after loan {loan.loan_id} creation: {e}")
            else:
                 reader_full_name = f"{loan.reader.first_name} {loan.reader.last_name}"
                 if loan.reader.user:
                     reader_full_name = loan.reader.user.get_full_name() or loan.reader.user.username
                 messages.success(request, f"Книга '{copy.book.book_title}' (Инв. №{copy.inventory_number}) успешно выдана читателю {reader_full_name}.")

            return redirect('staff_active_loans')
        else:
            # Form is invalid
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
            # Pass request_id back to template if it was in the POST
            context = {'form': form, 'request_id': request.POST.get('request_id')}
            # Ensure reader field is disabled again if necessary for re-rendering
            if request.POST.get('request_id'):
                form.fields['reader'].widget.attrs['disabled'] = True
            return render(request, 'staff/issue_book.html', context)

    else: # GET request
        form_kwargs = {
            'is_from_request': is_from_request_flag,
            'copy_queryset': copy_queryset
        }
        if is_from_request_flag:
             form_kwargs['initial'] = initial_data

        form = BookLoanForm(**form_kwargs)

    # Pass request_id (from GET) to template for hidden input
    context = {'form': form, 'request_id': request_id}
    return render(request, 'staff/issue_book.html', context)

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
    """Displays pending and approved book requests for staff approval/issuing."""
    # Fetch requests that are either pending or approved
    requests_query = BookRequest.objects.filter(status__in=['pending', 'approved']).select_related(
        'user', 'book', 'requested_location'
    )

    # Filtering by location (keep existing logic)
    location_filter = request.GET.get('location', '')
    if location_filter:
        request.session['staff_location_filter'] = location_filter
    elif 'staff_location_filter' in request.session:
        location_filter = request.session['staff_location_filter']

    if location_filter:
        requests_query = requests_query.filter(requested_location__location_id=location_filter)

    # Order requests, maybe pending first then approved?
    active_requests = requests_query.order_by('status', 'request_date') # Pending first

    locations = LibraryLocation.objects.all()

    context = {
        'requests': active_requests, # Renamed for clarity
        'locations': locations,
        'location_filter': location_filter,
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