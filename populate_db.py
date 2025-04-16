import os
import django
import random
import argparse
from decimal import Decimal
from datetime import timedelta, date

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libraryproject.settings')
django.setup()

# Import Faker and your models AFTER django.setup()
try:
    from faker import Faker
except ImportError:
    print("Faker library not found. Please install it: pip install Faker")
    exit()

from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.conf import settings
from library.models import (
    BookAuthor, LibraryLocation, ReaderType, CustomUser, LibraryReader,
    BookCatalog, BookCopy, BookLoan, LibraryFine, InterlibraryRequest,
    BookRequest, StudentReader, TeacherReader, TemporaryReader, ReaderRegistration
)
from django.db import transaction, IntegrityError

# --- Configuration ---
# Default values - can be overridden by command line arguments
DEFAULT_CONFIG = {
    'NUM_AUTHORS': 150,
    'NUM_BOOKS': 500,
    'MIN_COPIES_PER_BOOK': 1,
    'MAX_COPIES_PER_BOOK': 5,
    'NUM_LOCATIONS': 3,
    'NUM_READERS': 1000,  # Minimum number of readers
    'NUM_LOANS_PER_READER': 5,  # Average number of loans per reader
    'PCT_STUDENTS': 0.60,  # Percentage of readers who are students
    'PCT_TEACHERS': 0.25,  # Percentage of readers who are teachers/staff
    'PCT_TEMPORARY': 0.10,  # Percentage of readers who are temporary
    'PCT_LOANS_OVERDUE': 0.15,
    'PCT_LOANS_LOST': 0.02,
    'PCT_LOANS_RETURNED': 0.80,  # Percentage of non-lost loans that are returned
    'FINE_CHANCE_OVERDUE': 0.8,  # Chance an overdue loan gets a fine
    'NUM_BOOK_REQUESTS': 200,
    'NUM_INTERLIBRARY_REQUESTS': 50,
    'BATCH_SIZE': 100,  # Default batch size for creation operations
    'LOCALE': 'ru_RU'  # Default locale for Faker
}

# Set up command line arguments
parser = argparse.ArgumentParser(description='Populate the library database with realistic test data.')
parser.add_argument('--authors', type=int, help='Number of authors to create')
parser.add_argument('--books', type=int, help='Number of books to create')
parser.add_argument('--readers', type=int, help='Number of readers to create')
parser.add_argument('--loans', type=int, help='Number of loans per reader (average)')
parser.add_argument('--batch-size', type=int, help='Batch size for creation operations')
parser.add_argument('--locale', type=str, help='Locale for Faker (e.g., ru_RU, en_US)')
parser.add_argument('--create-authors', action='store_true', help='Create authors')
parser.add_argument('--create-books', action='store_true', help='Create books and copies')
parser.add_argument('--create-readers', action='store_true', help='Create users and readers')
parser.add_argument('--create-loans', action='store_true', help='Create loans and fines')
parser.add_argument('--create-requests', action='store_true', help='Create book requests')
parser.add_argument('--create-interlibrary', action='store_true', help='Create interlibrary requests')
parser.add_argument('--create-all', action='store_true', help='Create all data types')

# Parse arguments
args = parser.parse_args()

# Update configuration with command line arguments if provided
config = DEFAULT_CONFIG.copy()
if args.authors:
    config['NUM_AUTHORS'] = args.authors
if args.books:
    config['NUM_BOOKS'] = args.books
if args.readers:
    config['NUM_READERS'] = args.readers
if args.loans:
    config['NUM_LOANS_PER_READER'] = args.loans
if args.batch_size:
    config['BATCH_SIZE'] = args.batch_size
if args.locale:
    config['LOCALE'] = args.locale

# Initialize Faker with configured locale
fake = Faker(config['LOCALE'])

# Create all by default if no specific creation flags are set
create_all = args.create_all or not any([
    args.create_authors, args.create_books, args.create_readers,
    args.create_loans, args.create_requests, args.create_interlibrary
])

print("Starting database population script...")
print(f"Configuration: {config}")

@transaction.atomic
def create_locations():
    print("Creating Library Locations...")
    locations = []
    location_types = [('loan', 'Абонемент'), ('reading_room', 'Читальный зал')]
    existing_count = LibraryLocation.objects.count()
    if existing_count >= config['NUM_LOCATIONS']:
        print(f"Already have {existing_count} locations. Skipping creation.")
        return list(LibraryLocation.objects.all())

    for i in range(config['NUM_LOCATIONS'] - existing_count):
        loc_type_choice = random.choice(location_types)
        locations.append(LibraryLocation(
            location_name=f"{loc_type_choice[1]} #{i + 1} ({fake.city()})",
            location_type=loc_type_choice[0],
            address=fake.address()
        ))
    LibraryLocation.objects.bulk_create(locations)
    print(f"Created {len(locations)} new locations.")
    return list(LibraryLocation.objects.all())

@transaction.atomic
def create_authors():
    print("Creating Book Authors...")
    authors = []
    existing_count = BookAuthor.objects.count()
    if existing_count >= config['NUM_AUTHORS']:
        print(f"Already have {existing_count} authors. Skipping creation.")
        return list(BookAuthor.objects.all())

    # Process in batches
    remaining_to_create = config['NUM_AUTHORS'] - existing_count
    batch_size = min(config['BATCH_SIZE'], remaining_to_create)
    
    for batch_start in range(0, remaining_to_create, batch_size):
        batch_end = min(batch_start + batch_size, remaining_to_create)
        batch_count = batch_end - batch_start
        
        print(f"Creating authors batch {batch_start+1}-{batch_end} of {remaining_to_create}...")
        batch_authors = []
        
        for _ in range(batch_count):
            batch_authors.append(BookAuthor(
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                middle_name=fake.middle_name() if random.random() < 0.9 else None  # Most Russians have patronymics
            ))
        
        created = BookAuthor.objects.bulk_create(batch_authors)
        authors.extend(created)
        print(f"Created {len(created)} authors in this batch.")
    
    return list(BookAuthor.objects.all())

@transaction.atomic
def create_books_and_copies(authors, locations):
    print("Creating Books and Copies...")
    books = []
    copies = []
    book_author_relations = []

    existing_books_count = BookCatalog.objects.count()
    if existing_books_count >= config['NUM_BOOKS']:
        print(f"Already have {existing_books_count} books. Skipping creation.")
        return list(BookCatalog.objects.all()), list(BookCopy.objects.all())

    book_statuses = [s[0] for s in BookCatalog._meta.get_field('book_status').choices]
    copy_statuses = [s[0] for s in BookCopy._meta.get_field('copy_status').choices if s[0] != 'issued'] # Don't create as 'issued' initially

    created_books_count = 0
    attempt = 0
    max_attempts = config['NUM_BOOKS'] * 2 # Avoid infinite loops if ISBNs clash often

    while created_books_count < (config['NUM_BOOKS'] - existing_books_count) and attempt < max_attempts:
        attempt += 1
        isbn = fake.isbn13() if random.random() < 0.9 else None # Some books might not have ISBN
        book_title = fake.catch_phrase() + " " + fake.word().capitalize() # Generate somewhat plausible titles

        # Check for uniqueness before creating
        if (isbn and BookCatalog.objects.filter(isbn=isbn).exists()) or \
           BookCatalog.objects.filter(book_title=book_title).exists():
             print(f"Skipping duplicate book (ISBN: {isbn}, Title: {book_title})")
             continue

        book = BookCatalog(
            book_title=book_title,
            isbn=isbn,
            publication_year=fake.year(),
            publisher_name=fake.company(),
            acquisition_date=fake.date_between(start_date='-5y', end_date='today'),
            book_status=random.choice(book_statuses) if random.random() > 0.05 else 'available' # Mostly available
        )
        books.append(book)
        created_books_count += 1

    # Bulk create books first to get IDs
    created_books = BookCatalog.objects.bulk_create(books)
    print(f"Created {len(created_books)} new books.")

    # Now create copies and author relations
    all_books = list(BookCatalog.objects.all()) # Get all books including pre-existing ones
    inventory_number_start = BookCopy.objects.count() + 1 # Basic way to generate unique inventory numbers

    for book in all_books: # Iterate over all books
        # Assign Authors
        num_authors = random.randint(1, 3)
        book_authors = random.sample(authors, min(num_authors, len(authors)))
        for author in book_authors:
             # Using through model's Manager requires explicit book_id and author_id
             book_author_relations.append(
                 BookCatalog.authors.through(book_id=book.pk, author_id=author.pk)
             )


        # Create Copies
        num_copies = random.randint(config['MIN_COPIES_PER_BOOK'], config['MAX_COPIES_PER_BOOK'])
        for i in range(num_copies):
            copies.append(BookCopy(
                book=book,
                inventory_number=f"INV-{inventory_number_start + len(copies)}",
                copy_status=random.choice(copy_statuses) if book.book_status == 'available' else book.book_status,
                location=random.choice(locations),
                cost=Decimal(random.uniform(100.0, 2000.0)) if random.random() < 0.8 else None
            ))

    # Bulk create relations and copies
    try:
        BookCatalog.authors.through.objects.bulk_create(book_author_relations, ignore_conflicts=True)
        print(f"Created {len(book_author_relations)} book-author relations.")
    except IntegrityError as e:
        print(f"Warning: Could not create some book-author relations (possibly duplicates): {e}")

    created_copies = BookCopy.objects.bulk_create(copies)
    print(f"Created {len(created_copies)} new book copies.")

    return all_books, list(BookCopy.objects.all()) # Return all copies


@transaction.atomic
def create_users_and_readers(reader_types):
    print("Creating Users and Readers...")
    existing_readers_count = LibraryReader.objects.count()
    if existing_readers_count >= config['NUM_READERS']:
        print(f"Already have {existing_readers_count} readers. Skipping creation.")
        return list(CustomUser.objects.filter(role='user')), list(LibraryReader.objects.all())

    # Fetch reader type objects once
    reader_type_map = {rt.type_name: rt for rt in reader_types}
    student_type = reader_type_map.get('Студент')
    teacher_type = reader_type_map.get('Сотрудник')
    temp_fpc_type = reader_type_map.get('Слушатель ФПК')
    temp_app_type = reader_type_map.get('Абитуриент')
    temp_int_type = reader_type_map.get('Стажер')
    default_type = reader_type_map.get('Обычный читатель')

    if not default_type:
        print("Error: 'Обычный читатель' ReaderType not found. Ensure migration 0003 ran correctly.")
        return [], []

    # Pre-hash the default password
    hashed_password = make_password('password123')

    # Process in batches
    remaining_to_create = config['NUM_READERS'] - existing_readers_count
    batch_size = min(config['BATCH_SIZE'], remaining_to_create)
    
    all_users = []
    all_readers = []
    
    for batch_start in range(0, remaining_to_create, batch_size):
        batch_end = min(batch_start + batch_size, remaining_to_create)
        batch_count = batch_end - batch_start
        
        print(f"Creating users/readers batch {batch_start+1}-{batch_end} of {remaining_to_create}...")
        
        users = []
        readers_info = []
        generated_usernames = set()
        generated_emails = set()
        generated_card_numbers = set()
        
        # Generate batch data
        created_count = 0
        attempt = 0
        max_attempts = batch_count * 3
        
        while created_count < batch_count and attempt < max_attempts:
            attempt += 1
            first_name = fake.first_name()
            last_name = fake.last_name()
            middle_name = fake.middle_name() if random.random() < 0.9 else None
            
            # More realistic Russian usernames
            username_base = f"{last_name.lower()}_{first_name.lower()[0]}"
            if random.random() < 0.5 and middle_name:
                username_base += middle_name.lower()[0]
            username = f"{username_base}{random.randint(1, 999)}"
            
            # More realistic email - use Russian transliteration for email
            email_base = username_base.replace('_', '.')
            email_domains = ['mail.ru', 'yandex.ru', 'gmail.com', 'rambler.ru', 'list.ru', 'bk.ru', 'inbox.ru']
            email = f"{email_base}@{random.choice(email_domains)}"
            
            # Library card with institution prefix
            library_card_number = f"LIB-{random.randint(100000, 999999)}{batch_start + created_count}"
            
            # Avoid duplicates preemptively
            if (CustomUser.objects.filter(username=username).exists() or username in generated_usernames or
                CustomUser.objects.filter(email=email).exists() or email in generated_emails or
                LibraryReader.objects.filter(library_card_number=library_card_number).exists() or 
                library_card_number in generated_card_numbers):
                continue
            
            generated_usernames.add(username)
            generated_emails.add(email)
            generated_card_numbers.add(library_card_number)
            
            # Create User
            user = CustomUser(
                username=username,
                password=hashed_password,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_staff=False,
                is_active=True,
                role='user'
            )
            users.append(user)
            
            # Decide reader type with realistic distribution
            rand_val = random.random()
            reader_type_instance = default_type
            profile_type = 'default'
            
            if student_type and rand_val < config['PCT_STUDENTS']:
                reader_type_instance = student_type
                profile_type = 'student'
            elif teacher_type and rand_val < config['PCT_STUDENTS'] + config['PCT_TEACHERS']:
                reader_type_instance = teacher_type
                profile_type = 'teacher'
            elif (temp_fpc_type or temp_app_type or temp_int_type) and rand_val < config['PCT_STUDENTS'] + config['PCT_TEACHERS'] + config['PCT_TEMPORARY']:
                possible_temp_types = [t for t in [temp_fpc_type, temp_app_type, temp_int_type] if t]
                if possible_temp_types:
                    reader_type_instance = random.choice(possible_temp_types)
                    profile_type = 'temporary'
            
            # Registration date - more realistic distribution with seasons
            # More registrations at the beginning of academic year (Sep-Oct) and after New Year
            month_weights = [5, 3, 4, 4, 3, 2, 2, 3, 10, 7, 4, 5]  # Jan-Dec weights
            registration_year = random.choice([timezone.now().year - 3, timezone.now().year - 2, timezone.now().year - 1, timezone.now().year])
            registration_month = random.choices(range(1, 13), weights=month_weights, k=1)[0]
            
            if registration_month in [9, 10]:  # Start of academic year
                registration_day = random.randint(1, 10)  # First days of Sep/Oct have more registrations
            else:
                registration_day = random.randint(1, 28)
                
            registration_date = date(registration_year, registration_month, registration_day)
            
            # Create Reader info for batch creation
            reader_obj = LibraryReader(
                # user will be set after users are created
                first_name=first_name,
                last_name=last_name,
                middle_name=middle_name,
                library_card_number=library_card_number,
                registration_date=registration_date,
                reader_status='active' if random.random() > 0.1 else random.choice(['inactive', 'suspended']),
                suspension_end_date=None,
                reader_type=reader_type_instance,
                can_take_books_home=reader_type_instance.can_use_loan if reader_type_instance else True
            )
            
            readers_info.append({
                'reader_obj': reader_obj, 
                'profile_type': profile_type, 
                'temp_type_name': reader_type_instance.type_name if profile_type == 'temporary' else None,
                'user_username': username,  # Store username for later mapping
                'card_number': library_card_number  # Store card number for later mapping
            })
            
            created_count += 1
        
        print(f"Generated {len(users)} users and {len(readers_info)} readers for batch.")
        
        # Bulk create users first
        CustomUser.objects.bulk_create(users)
        
        # Re-fetch users to get their PKs
        batch_usernames = [u.username for u in users]
        fetched_users = CustomUser.objects.filter(username__in=batch_usernames)
        user_map = {user.username: user for user in fetched_users}
        
        # Assign user PKs to reader objects
        readers_to_create = []
        valid_reader_info = []
        
        for reader_info in readers_info:
            username = reader_info['user_username']
            user_obj = user_map.get(username)
            
            if user_obj and user_obj.pk:
                reader_info['reader_obj'].user_id = user_obj.pk
                readers_to_create.append(reader_info['reader_obj'])
                valid_reader_info.append(reader_info)
            else:
                print(f"Warning: Could not find created user for username {username}. Skipping reader.")
        
        # Bulk create readers
        created_readers = LibraryReader.objects.bulk_create(readers_to_create)
        
        # Re-fetch readers to get their PKs
        batch_card_numbers = [r['card_number'] for r in valid_reader_info]
        fetched_readers = LibraryReader.objects.filter(library_card_number__in=batch_card_numbers)
        reader_map = {reader.library_card_number: reader for reader in fetched_readers}
        
        # Create reader profiles
        student_profiles = []
        teacher_profiles = []
        temporary_profiles = []
        
        faculties = ['Инженерный', 'Экономический', 'Гуманитарный', 'Медицинский', 'Юридический',
                    'Исторический', 'Физический', 'Математический', 'Химический', 'Биологический']
        departments = ['Кафедра физики', 'Отдел кадров', 'Бухгалтерия', 'Кафедра истории', 'IT отдел',
                      'Кафедра литературы', 'Научная лаборатория', 'Учебная часть', 'Методический отдел']
        positions = ['Профессор', 'Доцент', 'Ассистент', 'Инженер', 'Лаборант', 'Сотрудник', 
                    'Старший преподаватель', 'Методист', 'Руководитель группы']
        degrees = ['Кандидат наук', 'Доктор наук']
        titles = ['Доцент', 'Профессор']
        
        for reader_info in valid_reader_info:
            card_number = reader_info['card_number']
            fetched_reader = reader_map.get(card_number)
            
            if not fetched_reader or not fetched_reader.pk:
                print(f"Warning: Could not find created reader with card {card_number}. Skipping profile.")
                continue
            
            profile_type = reader_info['profile_type']
            
            if profile_type == 'student':
                # More realistic student data
                faculty = random.choice(faculties)
                # Study groups follow patterns specific to Russian universities
                group_prefix = faculty[:2].upper()
                course_number = random.randint(1, 5)
                group_suffix = random.randint(1, 4)  # Group number within course
                study_group = f"{group_prefix}-{course_number}{group_suffix}"
                
                student_profiles.append(StudentReader(
                    reader_id=fetched_reader.pk,
                    faculty=faculty,
                    study_group=study_group,
                    course_number=course_number
                ))
            elif profile_type == 'teacher':
                # More realistic teacher/staff data
                department = random.choice(departments)
                position = random.choice(positions)
                
                # Academic credentials are more common for higher positions
                has_degree = position in ['Профессор', 'Доцент', 'Старший преподаватель']
                academic_degree = random.choice(degrees) if has_degree or random.random() < 0.3 else None
                
                has_title = position in ['Профессор', 'Доцент']
                academic_title = random.choice(titles) if has_title or random.random() < 0.2 else None
                
                teacher_profiles.append(TeacherReader(
                    reader_id=fetched_reader.pk,
                    department=department,
                    position=position,
                    academic_degree=academic_degree,
                    academic_title=academic_title,
                ))
            elif profile_type == 'temporary':
                temp_type_choice = 'FPC'  # Default
                if reader_info['temp_type_name'] == 'Слушатель ФПК': temp_type_choice = 'FPC'
                elif reader_info['temp_type_name'] == 'Абитуриент': temp_type_choice = 'applicant'
                elif reader_info['temp_type_name'] == 'Стажер': temp_type_choice = 'intern'
                
                temporary_profiles.append(TemporaryReader(
                    reader_id=fetched_reader.pk,
                    reader_type=temp_type_choice
                ))
        
        # Bulk create profiles in batches
        if student_profiles:
            StudentReader.objects.bulk_create(student_profiles)
            print(f"Created {len(student_profiles)} student profiles in this batch.")
        
        if teacher_profiles:
            TeacherReader.objects.bulk_create(teacher_profiles)
            print(f"Created {len(teacher_profiles)} teacher profiles in this batch.")
        
        if temporary_profiles:
            TemporaryReader.objects.bulk_create(temporary_profiles)
            print(f"Created {len(temporary_profiles)} temporary profiles in this batch.")
        
        # Add to overall results
        all_users.extend(fetched_users)
        all_readers.extend(fetched_readers)
    
    print(f"Total users created: {len(all_users)}")
    print(f"Total readers created: {len(all_readers)}")
    
    return list(CustomUser.objects.filter(role='user')), list(LibraryReader.objects.all())

@transaction.atomic
def create_loans_and_fines(readers, copies, locations):
    print("Creating Book Loans and Fines...")
    
    if not readers or not copies:
        print("No readers or copies available to create loans.")
        return
        
    # Filter for eligible readers and available copies
    readers_eligible_for_loan = [r for r in readers if r.reader_type and r.reader_type.can_use_loan and r.reader_status == 'active']
    available_copies = [copy for copy in copies if copy.copy_status == 'available']
    
    if not available_copies:
        print("No available copies to issue.")
        return
    if not readers_eligible_for_loan:
        print("No readers eligible for loans.")
        return
    
    loan_statuses = [s[0] for s in BookLoan._meta.get_field('loan_status').choices]
    fine_statuses = [s[0] for s in LibraryFine._meta.get_field('fine_status').choices]
    fine_reasons = {
        'overdue': 'overdue',
        'lost': 'lost',
        'damaged': 'damaged'
    }
    
    total_loans_to_create = int(len(readers_eligible_for_loan) * config['NUM_LOANS_PER_READER'])
    print(f"Target: approximately {total_loans_to_create} loans")
    
    # Process in batches
    created_loan_count = 0
    batch_size = min(config['BATCH_SIZE'], total_loans_to_create)
    issued_copy_ids = set()  # Track copies already issued
    
    while created_loan_count < total_loans_to_create and available_copies:
        batch_loans = []
        batch_copies_to_update = []
        batch_size = min(batch_size, total_loans_to_create - created_loan_count, len(available_copies))
        
        if batch_size <= 0:
            break
            
        print(f"Creating loans batch {created_loan_count+1}-{created_loan_count+batch_size} of {total_loans_to_create}...")
        
        for _ in range(batch_size):
            if not available_copies:
                break
                
            reader = random.choice(readers_eligible_for_loan)
            copy_to_loan = random.choice(available_copies)
            location = copy_to_loan.location
            
            # Remove copy from available list
            available_copies.remove(copy_to_loan)
            issued_copy_ids.add(copy_to_loan.pk)
            
            # Create realistic loan parameters
            loan_period = reader.reader_type.loan_period_days if reader.reader_type else 14
            
            # More realistic date distribution - higher loan frequency during semester
            # Fewer loans during summer and holidays
            current_date = timezone.now().date()
            month = current_date.month
            
            # Weight by month (academic calendar)
            if 9 <= month <= 11 or 2 <= month <= 4:  # Peak periods
                max_days_ago = min(loan_period * 3, 90)  # Busier periods have more recent loans
            elif month in [12, 1, 5]:  # Medium periods
                max_days_ago = min(loan_period * 2, 60)
            else:  # Summer and other slow periods
                max_days_ago = min(loan_period, 30)
                
            loan_date = fake.date_time_between(
                start_date=f'-{max_days_ago}d', 
                end_date='now', 
                tzinfo=timezone.get_current_timezone()
            )
            
            due_date = loan_date + timedelta(days=loan_period)
            return_date = None
            loan_status = 'active'
            
            # Determine loan status
            current_time = timezone.now()
            is_overdue = current_time > due_date
            is_lost = random.random() < config['PCT_LOANS_LOST']
            
            if is_lost:
                loan_status = 'lost'
                copy_to_loan.copy_status = 'lost'
            elif is_overdue:
                if random.random() < config['PCT_LOANS_RETURNED']:  # Returned but late
                    loan_status = 'returned'
                    # Return date is between due date and current date
                    return_date = fake.date_time_between(
                        start_date=due_date,
                        end_date=current_time, 
                        tzinfo=timezone.get_current_timezone()
                    )
                    copy_to_loan.copy_status = 'available'
                else:  # Still overdue, not returned
                    loan_status = 'overdue'
                    copy_to_loan.copy_status = 'issued'
            elif random.random() < config['PCT_LOANS_RETURNED']:  # Returned on time
                loan_status = 'returned'
                # Return date is between loan date and due date
                return_date = fake.date_time_between(
                    start_date=loan_date + timedelta(days=1),
                    end_date=due_date, 
                    tzinfo=timezone.get_current_timezone()
                )
                copy_to_loan.copy_status = 'available'
            else:  # Active, not yet due or returned
                loan_status = 'active'
                copy_to_loan.copy_status = 'issued'
                
            batch_copies_to_update.append(copy_to_loan)
            
            loan = BookLoan(
                reader=reader,
                copy=copy_to_loan,
                location=location,
                loan_date=loan_date.date(),
                due_date=due_date.date(),
                return_date=return_date.date() if return_date else None,
                loan_status=loan_status
            )
            batch_loans.append(loan)
            
        # Create loans in batch
        created_loans = BookLoan.objects.bulk_create(batch_loans)
        created_loan_count += len(created_loans)
        print(f"Created {len(created_loans)} loans in this batch.")
        
        # Update copy statuses
        print(f"Updating {len(batch_copies_to_update)} book copy statuses...")
        for copy_instance in batch_copies_to_update:
            BookCopy.objects.filter(pk=copy_instance.pk).update(copy_status=copy_instance.copy_status)
            
        # Create fines in a separate step
        print("Processing fines for loans...")
        create_fines_for_loans(created_loans)
    
    print(f"Total loans created: {created_loan_count}")

@transaction.atomic
def create_fines_for_loans(loans):
    """Separate function to create fines for the loans that were just created"""
    fine_statuses = [s[0] for s in LibraryFine._meta.get_field('fine_status').choices]
    fine_reasons = {
        'overdue': 'overdue',
        'lost': 'lost',
        'damaged': 'damaged'
    }
    
    batch_fines = []
    current_time = timezone.now()
    
    for loan in loans:
        # Skip if not eligible for fine
        if loan.loan_status not in ['overdue', 'lost', 'returned']:
            continue
            
        fine_reason = None
        if loan.loan_status == 'overdue' and random.random() < config['FINE_CHANCE_OVERDUE']:
            fine_reason = fine_reasons['overdue']
        elif loan.loan_status == 'lost':
            fine_reason = fine_reasons['lost']
        elif loan.loan_status == 'returned' and loan.return_date and loan.return_date > loan.due_date and random.random() < config['FINE_CHANCE_OVERDUE']:
            fine_reason = fine_reasons['overdue']  # Returned late
            
        if not fine_reason:
            continue
            
        fine_amount = Decimal(0)
        reader = loan.reader
        fine_per_day = reader.reader_type.fine_per_day if reader.reader_type else Decimal('10.00')
        
        if fine_reason == fine_reasons['overdue'] and not loan.return_date:  # Still overdue
            days_overdue = (current_time.date() - loan.due_date).days
            fine_amount = max(Decimal(0), Decimal(days_overdue) * fine_per_day)
        elif fine_reason == fine_reasons['overdue'] and loan.return_date:  # Returned late
            days_overdue = (loan.return_date - loan.due_date).days
            fine_amount = max(Decimal(0), Decimal(days_overdue) * fine_per_day)
        elif fine_reason == fine_reasons['lost']:
            # For lost books, check if the copy has a cost
            copy = loan.copy
            if copy and copy.cost:
                fine_amount = copy.cost * Decimal(random.uniform(1.0, 1.5))  # Cost plus penalty
            else:
                fine_amount = Decimal(random.uniform(500.0, 3000.0))  # Default fine if cost unknown
                
        if fine_amount > 0:
            # Create realistic fine distribution
            # Higher chance of being pending for recent fines
            fine_date = loan.return_date if loan.return_date else current_time.date()
            days_since_fine = (current_time.date() - fine_date).days
            
            # Newer fines are more likely to be pending
            if days_since_fine < 7:
                fine_status_prob = {'pending': 0.8, 'paid': 0.1, 'partially_paid': 0.1}
            elif days_since_fine < 30:
                fine_status_prob = {'pending': 0.5, 'paid': 0.3, 'partially_paid': 0.2}
            else:
                fine_status_prob = {'pending': 0.3, 'paid': 0.6, 'partially_paid': 0.1}
                
            fine_status = random.choices(
                list(fine_status_prob.keys()),
                weights=list(fine_status_prob.values()),
                k=1
            )[0]
            
            # Create the fine with LOAN_ID directly, not the loan object
            fine = LibraryFine(
                reader_id=loan.reader_id,  # Use FK directly
                loan_id=loan.pk,  # Use FK directly 
                fine_amount=fine_amount.quantize(Decimal("0.01")),
                fine_date=fine_date,
                fine_status=fine_status,
                fine_reason=fine_reason,
                notes=f"Автоматически сгенерированный штраф ({fine_reason})."
            )
            batch_fines.append(fine)
    
    # Bulk create fines
    if batch_fines:
        LibraryFine.objects.bulk_create(batch_fines)
        print(f"Created {len(batch_fines)} library fines.")
    else:
        print("No fines created for this batch of loans.")

@transaction.atomic
def create_book_requests(users, books, locations):
    print("Creating Book Requests...")
    
    if not users or not books or not locations:
        print("Need users, books, and locations to create book requests.")
        return
        
    staff_users = list(CustomUser.objects.filter(role__in=['staff', 'admin']))
    
    # Get all request statuses 
    request_statuses = [s[0] for s in BookRequest._meta.get_field('status').choices]
    
    # More realistic status distribution
    status_weights = {
        'pending': 0.3,      # Many requests start pending
        'approved': 0.2,     # Some get approved
        'issued': 0.25,      # Most approved requests get issued
        'returned': 0.15,    # Some have completed the cycle
        'cancelled': 0.05,   # Few are cancelled
        'rejected': 0.05     # Few are rejected
    }
    
    # Calculate total requests to create
    num_requests = min(config['NUM_BOOK_REQUESTS'], len(users) * len(books))
    existing_requests = BookRequest.objects.count()
    remaining_to_create = max(0, num_requests - existing_requests)
    
    if remaining_to_create <= 0:
        print(f"Already have {existing_requests} book requests. Skipping creation.")
        return
        
    print(f"Creating {remaining_to_create} book requests...")
    batch_size = min(config['BATCH_SIZE'], remaining_to_create)
    total_created = 0
    
    for batch_start in range(0, remaining_to_create, batch_size):
        batch_end = min(batch_start + batch_size, remaining_to_create)
        batch_count = batch_end - batch_start
        
        print(f"Creating book requests batch {batch_start+1}-{batch_end} of {remaining_to_create}...")
        requests = []
        
        # Define time periods with weights for more realistic request patterns
        time_periods = {
            'very_recent': {'days_ago': 7, 'weight': 0.3},
            'recent': {'days_ago': 30, 'weight': 0.4},
            'medium': {'days_ago': 90, 'weight': 0.2},
            'old': {'days_ago': 180, 'weight': 0.1}
        }
        
        created_count = 0
        attempt = 0
        max_attempts = batch_count * 3
        
        while created_count < batch_count and attempt < max_attempts:
            attempt += 1
            
            # Select user and book with preference for active readers and available books
            user = random.choice(users)
            
            # More popular books get more requests
            books_by_popularity = sorted(books, key=lambda _: random.random())
            book_weights = [0.9 ** i for i in range(len(books_by_popularity))]
            book_index = random.choices(range(len(books_by_popularity)), weights=book_weights[:len(books_by_popularity)], k=1)[0]
            book = books_by_popularity[book_index]
            
            location = random.choice(locations)
            
            # Select time period for request
            period_name = random.choices(
                list(time_periods.keys()),
                weights=[p['weight'] for p in time_periods.values()],
                k=1
            )[0]
            days_ago = time_periods[period_name]['days_ago']
            
            # Generate request date with realistic distribution
            if period_name == 'very_recent':
                # More weight to very recent days
                request_date = fake.date_time_between(
                    start_date=f'-{days_ago}d', 
                    end_date='now', 
                    tzinfo=timezone.get_current_timezone()
                )
            else:
                request_date = fake.date_time_between(
                    start_date=f'-{days_ago}d', 
                    end_date=f'-{max(1, int(days_ago * 0.2))}d', 
                    tzinfo=timezone.get_current_timezone()
                )
                
            # Select status with weights
            status = random.choices(
                list(status_weights.keys()),
                weights=list(status_weights.values()),
                k=1
            )[0]
            
            # Adjust status based on time period
            # Very recent requests are more likely to be pending
            if period_name == 'very_recent' and random.random() < 0.7:
                status = 'pending'
            # Old requests shouldn't be pending
            elif period_name == 'old' and status == 'pending':
                status = random.choice(['approved', 'rejected', 'cancelled', 'returned'])
                
            processed_by = None
            processed_date = None
            notes = None
            
            # Add processing details for non-pending statuses
            if status != 'pending':
                if staff_users:
                    processed_by = random.choice(staff_users)
                    
                # Processing happens between request date and now
                processed_date = fake.date_time_between(
                    start_date=request_date,
                    end_date=timezone.now(),
                    tzinfo=timezone.get_current_timezone()
                )
                
                # Add notes for certain statuses
                if status == 'rejected':
                    rejection_reasons = [
                        "Книга недоступна в настоящее время",
                        "Все экземпляры выданы",
                        "Книга находится на реставрации",
                        "Нет в наличии в запрошенном филиале",
                        "Книга зарезервирована для учебного процесса"
                    ]
                    notes = random.choice(rejection_reasons)
                elif status == 'returned' and random.random() < 0.2:
                    notes = "Книга возвращена в хорошем состоянии"
                
            # Check for potentially conflicting requests
            if BookRequest.objects.filter(user=user, book=book, status='pending').exists():
                continue  # Skip if user already has pending request for this book
                
            # Create the request
            requests.append(BookRequest(
                user=user,
                book=book,
                requested_location=location,
                request_date=request_date,
                status=status,
                processed_by=processed_by,
                processed_date=processed_date,
                notes=notes
            ))
            created_count += 1
            
        # Bulk create requests
        created = BookRequest.objects.bulk_create(requests)
        total_created += len(created)
        print(f"Created {len(created)} book requests in this batch.")
        
    print(f"Total book requests created: {total_created}")

@transaction.atomic
def create_interlibrary_requests(readers, books):
    print("Creating Interlibrary Requests...")
    
    if not readers or not books:
        print("Need readers and books to create interlibrary requests.")
        return
        
    staff_users = list(CustomUser.objects.filter(role__in=['staff', 'admin']))
    
    # Get all request statuses
    request_statuses = [s[0] for s in InterlibraryRequest._meta.get_field('request_status').choices]
    
    # More realistic status distribution
    status_weights = {
        'pending': 0.25,
        'approved': 0.15,
        'processing': 0.20,
        'received': 0.15,
        'issued': 0.10,
        'returned': 0.05,
        'cancelled': 0.05,
        'rejected': 0.05
    }
    
    # Calculate total requests to create
    num_requests = min(config['NUM_INTERLIBRARY_REQUESTS'], len(readers) * len(books))
    existing_requests = InterlibraryRequest.objects.count()
    remaining_to_create = max(0, num_requests - existing_requests)
    
    if remaining_to_create <= 0:
        print(f"Already have {existing_requests} interlibrary requests. Skipping creation.")
        return
        
    print(f"Creating {remaining_to_create} interlibrary requests...")
    batch_size = min(config['BATCH_SIZE'], remaining_to_create)
    total_created = 0
    
    # External library names for realistic staff notes
    external_libraries = [
        "Библиотека МГУ",
        "РГБ",
        "Научная библиотека СПбГУ",
        "Библиотека им. Ленина",
        "ГПНТБ России",
        "Библиотека РАН",
        "Областная библиотека"
    ]
    
    for batch_start in range(0, remaining_to_create, batch_size):
        batch_end = min(batch_start + batch_size, remaining_to_create)
        batch_count = batch_end - batch_start
        
        print(f"Creating interlibrary requests batch {batch_start+1}-{batch_end} of {remaining_to_create}...")
        requests = []
        
        # Realistic time periods for requests
        # Interlibrary requests take longer to process
        time_periods = {
            'very_recent': {'days_ago': 14, 'weight': 0.3},
            'recent': {'days_ago': 60, 'weight': 0.4},
            'medium': {'days_ago': 120, 'weight': 0.2},
            'old': {'days_ago': 240, 'weight': 0.1}
        }
        
        created_count = 0
        attempt = 0
        max_attempts = batch_count * 3
        
        while created_count < batch_count and attempt < max_attempts:
            attempt += 1
            
            # More likely to be faculty/researchers for interlibrary loans
            reader_weights = []
            for reader in readers:
                if hasattr(reader, 'teacherreader') and reader.teacherreader:
                    reader_weights.append(3.0)  # Teachers more likely
                elif reader.reader_type and reader.reader_type.type_name == 'Студент':
                    reader_weights.append(1.0)  # Students less likely
                else:
                    reader_weights.append(0.5)  # Others least likely
                    
            reader_index = random.choices(range(len(readers)), weights=reader_weights[:len(readers)], k=1)[0]
            reader = readers[reader_index]
            
            # Book selection - prefer books not in the catalog for interlibrary loan
            book = random.choice(books)
            
            # Select time period for request
            period_name = random.choices(
                list(time_periods.keys()),
                weights=[p['weight'] for p in time_periods.values()],
                k=1
            )[0]
            days_ago = time_periods[period_name]['days_ago']
            
            # Generate request date
            request_date = fake.date_between(start_date=f'-{days_ago}d', end_date='today')
            
            # Select status with weighted distribution
            status = random.choices(
                list(status_weights.keys()),
                weights=list(status_weights.values()),
                k=1
            )[0]
            
            # Adjust status based on time period
            if period_name == 'very_recent' and random.random() < 0.7:
                status = 'pending'
            elif period_name == 'old' and status == 'pending':
                status = random.choice(['approved', 'rejected', 'cancelled', 'returned'])
                
            processed_by = None
            processed_date = None
            staff_notes = None
            
            # More realistic required_by_date
            required_by_date = None
            if random.random() < 0.6:  # Most requests have a deadline
                if status == 'pending':
                    # For pending requests, due date is in the future
                    required_by_date = fake.date_between(
                        start_date='today',
                        end_date='+60d'
                    )
                else:
                    # For processed requests, due date might be in the past
                    days_from_request = random.randint(14, 90)
                    required_by_date = request_date + timedelta(days=days_from_request)
            
            # Add processing details for non-pending statuses
            if status != 'pending' and status != 'cancelled':
                if staff_users:
                    processed_by = random.choice(staff_users)
                    
                # Processing happens a few days after request
                min_days = 1
                max_days = min(14, (timezone.now().date() - request_date).days)
                if max_days > min_days:
                    days_after_request = random.randint(min_days, max_days)
                    processed_date = request_date + timedelta(days=days_after_request)
                else:
                    processed_date = request_date + timedelta(days=1)
                
                # Add realistic staff notes
                if status == 'approved':
                    external_lib = random.choice(external_libraries)
                    staff_notes = f"Запрос отправлен в {external_lib}. Ожидаемое время доставки 7-14 дней."
                elif status == 'processing':
                    staff_notes = f"Книга найдена в {random.choice(external_libraries)}. Ожидается доставка."
                elif status == 'rejected':
                    rejection_reasons = [
                        "Книга недоступна в библиотеках-партнерах",
                        "Отказано в выдаче сторонней библиотекой",
                        "Книга доступна только для чтения в читальном зале библиотеки-владельца",
                        "Книга находится на реставрации",
                        "Редкое издание, не выдается по МБА"
                    ]
                    staff_notes = random.choice(rejection_reasons)
                
            # Reader notes are more likely for academic/research requests
            reader_notes = None
            if random.random() < 0.4:
                if hasattr(reader, 'teacherreader') and reader.teacherreader:
                    academic_notes = [
                        "Нужна для научной работы",
                        f"Требуется для исследования по теме {fake.sentence()}",
                        "Необходима для подготовки курса лекций",
                        "Срочно нужна для завершения статьи",
                        f"Для работы над {fake.word()} {fake.word()}"
                    ]
                    reader_notes = random.choice(academic_notes)
                else:
                    general_notes = [
                        "Нужна для дипломной работы",
                        "Для подготовки к экзамену",
                        "Не нашел в основном фонде библиотеки",
                        "Необходима для курсовой работы"
                    ]
                    reader_notes = random.choice(general_notes)
                    
            # Check for potentially conflicting requests
            if InterlibraryRequest.objects.filter(
                reader=reader, 
                book=book, 
                request_status__in=['pending', 'approved', 'processing']).exists():
                continue
                
            # Create the request
            requests.append(InterlibraryRequest(
                reader=reader,
                book=book,
                request_date=request_date,
                request_status=status,
                required_by_date=required_by_date,
                notes=reader_notes,
                processed_by=processed_by,
                processed_date=processed_date,
                staff_notes=staff_notes
            ))
            created_count += 1
            
        # Bulk create requests
        created = InterlibraryRequest.objects.bulk_create(requests)
        total_created += len(created)
        print(f"Created {len(created)} interlibrary requests in this batch.")
        
    print(f"Total interlibrary requests created: {total_created}")

# --- Main Execution ---
if __name__ == '__main__':
    start_time = timezone.now()
    print(f"Script started at: {start_time}")

    # Ensure default reader types exist (or create them if migration didn't)
    # This part assumes the 0003 migration successfully created the types.
    # If not, you'd need to add code here to create them similar to the migration.
    reader_types = list(ReaderType.objects.all())
    if not reader_types:
        print("Error: No ReaderType objects found. Please run migration '0003_create_default_reader_types' first.")
        exit()
    else:
        print(f"Found {len(reader_types)} ReaderType objects.")

    # Create data based on command line arguments or create_all flag
    locations = []
    authors = []
    books = []
    copies = []
    users = []
    readers = []

    if create_all or args.create_authors:
        locations = create_locations()
        authors = create_authors()

    if create_all or args.create_books:
        books, copies = create_books_and_copies(authors, locations)

    if create_all or args.create_readers:
        users, readers = create_users_and_readers(reader_types)

    if create_all or args.create_loans:
        create_loans_and_fines(readers, copies, locations)

    if create_all or args.create_requests:
        create_book_requests(users, books, locations)

    if create_all or args.create_interlibrary:
        create_interlibrary_requests(readers, books)

    end_time = timezone.now()
    print(f"Script finished at: {end_time}")
    print(f"Total execution time: {end_time - start_time}")
    print("Database population complete.") 