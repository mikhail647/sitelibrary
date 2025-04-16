import os
import django
import random
from decimal import Decimal
from datetime import timedelta, date

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'libraryproject.settings') # Replace 'libraryproject.settings' with your actual settings module path
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

fake = Faker('ru_RU') # Use Russian locale for more realistic names, etc.

# --- Configuration ---
NUM_AUTHORS = 150
NUM_BOOKS = 500
MIN_COPIES_PER_BOOK = 1
MAX_COPIES_PER_BOOK = 5
NUM_LOCATIONS = 3
NUM_READERS = 1000 # Minimum number of readers
NUM_LOANS_PER_READER = 5 # Average number of loans per reader
PCT_STUDENTS = 0.60 # Percentage of readers who are students
PCT_TEACHERS = 0.25 # Percentage of readers who are teachers/staff
PCT_TEMPORARY = 0.10 # Percentage of readers who are temporary
# Remaining are 'Обычный читатель'
PCT_LOANS_OVERDUE = 0.15
PCT_LOANS_LOST = 0.02
PCT_LOANS_RETURNED = 0.80 # Percentage of non-lost loans that are returned
FINE_CHANCE_OVERDUE = 0.8 # Chance an overdue loan gets a fine
NUM_BOOK_REQUESTS = 200
NUM_INTERLIBRARY_REQUESTS = 50
# --- End Configuration ---

print("Starting database population script...")

@transaction.atomic
def create_locations():
    print("Creating Library Locations...")
    locations = []
    location_types = [('loan', 'Абонемент'), ('reading_room', 'Читальный зал')]
    existing_count = LibraryLocation.objects.count()
    if existing_count >= NUM_LOCATIONS:
        print(f"Already have {existing_count} locations. Skipping creation.")
        return list(LibraryLocation.objects.all())

    for i in range(NUM_LOCATIONS - existing_count):
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
    if existing_count >= NUM_AUTHORS:
        print(f"Already have {existing_count} authors. Skipping creation.")
        return list(BookAuthor.objects.all())

    for _ in range(NUM_AUTHORS - existing_count):
        authors.append(BookAuthor(
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            middle_name=fake.middle_name() if random.random() < 0.5 else None
        ))
    BookAuthor.objects.bulk_create(authors)
    print(f"Created {len(authors)} new authors.")
    return list(BookAuthor.objects.all())

@transaction.atomic
def create_books_and_copies(authors, locations):
    print("Creating Books and Copies...")
    books = []
    copies = []
    book_author_relations = []

    existing_books_count = BookCatalog.objects.count()
    if existing_books_count >= NUM_BOOKS:
        print(f"Already have {existing_books_count} books. Skipping creation.")
        return list(BookCatalog.objects.all()), list(BookCopy.objects.all())

    book_statuses = [s[0] for s in BookCatalog._meta.get_field('book_status').choices]
    copy_statuses = [s[0] for s in BookCopy._meta.get_field('copy_status').choices if s[0] != 'issued'] # Don't create as 'issued' initially

    created_books_count = 0
    attempt = 0
    max_attempts = NUM_BOOKS * 2 # Avoid infinite loops if ISBNs clash often

    while created_books_count < (NUM_BOOKS - existing_books_count) and attempt < max_attempts:
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
        num_copies = random.randint(MIN_COPIES_PER_BOOK, MAX_COPIES_PER_BOOK)
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
    users = []
    readers = []
    student_profiles = []
    teacher_profiles = []
    temporary_profiles = []
    reader_registrations = []

    existing_readers_count = LibraryReader.objects.count()
    if existing_readers_count >= NUM_READERS:
        print(f"Already have {existing_readers_count} readers. Skipping creation.")
        return list(CustomUser.objects.filter(role='user')), list(LibraryReader.objects.all())

    roles = [r[0] for r in CustomUser._meta.get_field('role').choices]
    reader_statuses = [s[0] for s in LibraryReader._meta.get_field('reader_status').choices]
    temp_reader_types = [t[0] for t in TemporaryReader._meta.get_field('reader_type').choices]
    faculties = ['Инженерный', 'Экономический', 'Гуманитарный', 'Медицинский', 'Юридический']
    departments = ['Кафедра физики', 'Отдел кадров', 'Бухгалтерия', 'Кафедра истории', 'IT отдел']
    positions = ['Профессор', 'Доцент', 'Ассистент', 'Инженер', 'Лаборант', 'Сотрудник']
    degrees = ['Кандидат наук', 'Доктор наук']
    titles = ['Доцент', 'Профессор']


    created_count = 0
    attempt = 0
    max_attempts = int(NUM_READERS * 1.5) # Allow for some username/card number clashes

    # Fetch reader type objects once
    reader_type_map = {rt.type_name: rt for rt in reader_types}
    student_type = reader_type_map.get('Студент')
    teacher_type = reader_type_map.get('Сотрудник') # Assuming TeacherReader uses 'Сотрудник' type
    temp_fpc_type = reader_type_map.get('Слушатель ФПК')
    temp_app_type = reader_type_map.get('Абитуриент')
    temp_int_type = reader_type_map.get('Стажер')
    default_type = reader_type_map.get('Обычный читатель')

    if not default_type:
        print("Error: 'Обычный читатель' ReaderType not found. Ensure migration 0003 ran correctly.")
        return [], [] # Cannot proceed without default type

    # --- Keep track of generated unique fields in this run ---
    generated_usernames = set()
    generated_emails = set()
    generated_card_numbers = set()
    # --- End track ---

    needed_readers = NUM_READERS - existing_readers_count
    print(f"Attempting to create {needed_readers} new readers...")

    # --- Pre-hash the default password --- 
    hashed_password = make_password('password123')
    print("Pre-hashed default password.") # Added print
    # --- End pre-hash ---

    while created_count < needed_readers and attempt < max_attempts:
        attempt += 1
        if attempt % 100 == 0: # Print every 100 attempts
            print(f"  Attempt {attempt}/{max_attempts}, Created {created_count}/{needed_readers} readers...")
        first_name = fake.first_name()
        last_name = fake.last_name()
        username = f"{fake.user_name()}{random.randint(1, 999)}"
        email = fake.email() # Generate email
        library_card_number = f"LIB-{random.randint(100000, 999999)}{created_count + existing_readers_count}" # Make card number more unique

        # Avoid duplicates preemptively (check DB and current batch)
        if CustomUser.objects.filter(username=username).exists() or username in generated_usernames or \
           CustomUser.objects.filter(email=email).exists() or email in generated_emails or \
           LibraryReader.objects.filter(library_card_number=library_card_number).exists() or library_card_number in generated_card_numbers:
            print(f"Skipping duplicate user/reader (Username: {username}, Email: {email}, Card: {library_card_number})")
            continue

        # --- Add generated fields to sets ---
        generated_usernames.add(username)
        generated_emails.add(email)
        generated_card_numbers.add(library_card_number)
        # --- End add ---

        # Create User first
        user = CustomUser(
            username=username,
            password=hashed_password, # Use pre-hashed password
            email=email, # Use generated email
            first_name=first_name,
            last_name=last_name,
            is_staff=False,
            is_active=True,
            role='user' # Default to user role for readers
        )
        users.append(user)

        # Decide reader type
        rand_val = random.random()
        reader_type_instance = default_type
        profile_type = 'default' # To track which profile list to add to

        if student_type and rand_val < PCT_STUDENTS:
            reader_type_instance = student_type
            profile_type = 'student'
        elif teacher_type and rand_val < PCT_STUDENTS + PCT_TEACHERS:
            reader_type_instance = teacher_type
            profile_type = 'teacher'
        elif (temp_fpc_type or temp_app_type or temp_int_type) and rand_val < PCT_STUDENTS + PCT_TEACHERS + PCT_TEMPORARY:
            possible_temp_types = [t for t in [temp_fpc_type, temp_app_type, temp_int_type] if t]
            if possible_temp_types:
                 reader_type_instance = random.choice(possible_temp_types)
                 profile_type = 'temporary'


        # Create Reader linked to User (after user is saved)
        reader = LibraryReader(
            # user will be set after users are created
            first_name=first_name,
            last_name=last_name,
            middle_name=fake.middle_name() if random.random() < 0.6 else None,
            library_card_number=library_card_number,
            registration_date=fake.date_between(start_date='-3y', end_date='today'),
            reader_status=random.choice(reader_statuses) if random.random() > 0.1 else 'active',
            suspension_end_date=None, # Add logic later if needed
            reader_type=reader_type_instance,
            can_take_books_home=reader_type_instance.can_use_loan if reader_type_instance else True
        )
        readers.append({'reader_obj': reader, 'profile_type': profile_type, 'temp_type_name': reader_type_instance.type_name if profile_type == 'temporary' else None})
        created_count += 1


    print(f"Finished generating {len(users)} users and {len(readers)} readers in memory.")
    # Bulk create users first
    print("Starting bulk create for Users...")
    CustomUser.objects.bulk_create(users) # Just execute, don't rely on return value immediately
    print(f"Finished bulk create request for {len(users)} users.") # Simplified print

    # --- Re-fetch users to ensure PKs are available --- 
    print("Re-fetching users from database to get PKs...")
    generated_username_list = [u.username for u in users] # Get usernames from original list
    # Fetch users matching the generated usernames
    fetched_users = CustomUser.objects.filter(username__in=generated_username_list)
    user_map = {user.username: user for user in fetched_users} # Map usernames to FETCHED user objects
    print(f"Fetched {len(user_map)} users from DB.")
    # --- End re-fetch ---

    # Assign user PKs to reader objects before creating readers
    print("Assigning User PKs to Reader objects...") # Added print
    readers_to_create_final = []
    valid_reader_info = [] # Store info for readers that get a valid user_id

    # Iterate through the ORIGINAL user list to maintain order relative to readers list
    for i, user_in_memory in enumerate(users):
        reader_info = readers[i] # Get the corresponding reader info
        username = user_in_memory.username # Use username from original user object

        # user_obj = user_map.get(username) # Original lookup
        user_obj_fetched = user_map.get(username) # Look up in the FETCHED map

        # Ensure the user object was created and has a PK
        # if user_obj and user_obj.pk:
        if user_obj_fetched and user_obj_fetched.pk: # Check fetched object
            # Assign the user's primary key directly to the reader object
            reader_info['reader_obj'].user_id = user_obj_fetched.pk
            readers_to_create_final.append(reader_info['reader_obj'])
            valid_reader_info.append(reader_info) # Keep track of valid ones for profiles
        else:
             # print(f"Warning: Could not find created user or user PK for username {username}. Skipping reader.")
             print(f"Warning: Could not find FETCHED user or user PK for username {username}. Skipping reader.") # Modified warning

    print(f"Attempting to bulk create {len(readers_to_create_final)} readers...")
    # Bulk create only the readers that have a valid user_id assigned
    created_readers = LibraryReader.objects.bulk_create(readers_to_create_final)
    print(f"Created {len(created_readers)} new readers.")

    # Re-fetch might be safer if bulk_create doesn't return full objects reliably
    # reader_map = {reader.library_card_number: reader for reader in created_readers}
    # Let's try using the returned objects first, assuming they have PKs
    reader_map = {reader.library_card_number: reader for reader in created_readers}

    # Now create specific profiles using the IDs from created_readers
    # Use valid_reader_info which corresponds to the successfully created readers
    print("Preparing profiles for created readers...") # Added print
    for reader_info in valid_reader_info:
        # Find the corresponding CREATED reader object using the map
        created_reader_obj = reader_map.get(reader_info['reader_obj'].library_card_number)
        if not created_reader_obj:
             print(f"Warning: Could not find created reader in map for card {reader_info['reader_obj'].library_card_number}")
             continue

        profile_type = reader_info['profile_type']

        if profile_type == 'student':
            student_profiles.append(StudentReader(
                # reader=created_reader_obj, # Use the object from the map
                reader_id=created_reader_obj.pk, # Assign reader PK directly
                faculty=random.choice(faculties),
                study_group=f"GR-{random.randint(100, 999)}",
                course_number=random.randint(1, 5)
            ))
        elif profile_type == 'teacher':
             teacher_profiles.append(TeacherReader(
                 # reader=created_reader_obj, # Use the object from the map
                 reader_id=created_reader_obj.pk, # Assign reader PK directly
                 department=random.choice(departments),
                 position=random.choice(positions),
                 academic_degree=random.choice(degrees) if random.random() < 0.4 else None,
                 academic_title=random.choice(titles) if random.random() < 0.3 else None,
             ))
        elif profile_type == 'temporary':
            temp_type_choice = 'FPC' # Default
            if reader_info['temp_type_name'] == 'Слушатель ФПК': temp_type_choice = 'FPC'
            elif reader_info['temp_type_name'] == 'Абитуриент': temp_type_choice = 'applicant'
            elif reader_info['temp_type_name'] == 'Стажер': temp_type_choice = 'intern'

            temporary_profiles.append(TemporaryReader(
                 # reader=created_reader_obj, # Use the object from the map
                 reader_id=created_reader_obj.pk, # Assign reader PK directly
                 reader_type=temp_type_choice
            ))

    # Bulk create profiles
    print("Starting bulk create for Student Profiles...")
    StudentReader.objects.bulk_create(student_profiles)
    print(f"Created {len(student_profiles)} student profiles.")
    print("Starting bulk create for Teacher Profiles...")
    TeacherReader.objects.bulk_create(teacher_profiles)
    print(f"Created {len(teacher_profiles)} teacher profiles.")
    print("Starting bulk create for Temporary Profiles...")
    TemporaryReader.objects.bulk_create(temporary_profiles)
    print(f"Created {len(temporary_profiles)} temporary profiles.")

    # Create registrations (optional, example for all readers at one location)
    # You might want more complex logic here
    # all_locations = list(LibraryLocation.objects.all())
    # if all_locations:
    #     location_for_registration = random.choice(all_locations)
    #     print(f"Creating registrations at location {location_for_registration.location_name}")
    #     for reader in LibraryReader.objects.all(): # All readers including old ones
    #         reader_registrations.append(ReaderRegistration(
    #             reader=reader,
    #             location=location_for_registration,
    #             registration_date=reader.registration_date,
    #             registration_expiry_date=reader.registration_date + timedelta(days=365) # Example expiry
    #         ))
    #     ReaderRegistration.objects.bulk_create(reader_registrations, ignore_conflicts=True)
    #     print(f"Created {len(reader_registrations)} reader registrations.")


    return list(CustomUser.objects.filter(role='user')), list(LibraryReader.objects.all())

@transaction.atomic
def create_loans_and_fines(readers, copies, locations):
    print("Creating Book Loans and Fines...")
    loans = []
    fines = []
    copies_to_update = []
    issued_copy_ids = set() # Track copies already issued in this run

    if not readers or not copies:
        print("No readers or copies available to create loans.")
        return

    loan_statuses = [s[0] for s in BookLoan._meta.get_field('loan_status').choices]
    fine_statuses = [s[0] for s in LibraryFine._meta.get_field('fine_status').choices]
    fine_reasons = {
        'overdue': 'overdue',
        'lost': 'lost',
        'damaged': 'damaged'
    }

    available_copies = [copy for copy in copies if copy.copy_status == 'available' and copy.pk not in issued_copy_ids]
    readers_eligible_for_loan = [r for r in readers if r.reader_type and r.reader_type.can_use_loan and r.reader_status == 'active']

    if not available_copies:
        print("No available copies to issue.")
        return
    if not readers_eligible_for_loan:
        print("No readers eligible for loans.")
        return


    total_loans_to_create = int(len(readers_eligible_for_loan) * NUM_LOANS_PER_READER)
    print(f"Attempting to create approx {total_loans_to_create} loans...")

    created_loan_count = 0
    while created_loan_count < total_loans_to_create and available_copies:
        reader = random.choice(readers_eligible_for_loan)
        copy_to_loan = random.choice(available_copies)
        location = copy_to_loan.location # Loan happens at copy's location

        loan_period = reader.reader_type.loan_period_days if reader.reader_type else 14 # Default loan period
        loan_date = fake.date_time_between(start_date=f'-{loan_period*2}d', end_date='now', tzinfo=timezone.get_current_timezone())
        due_date = loan_date + timedelta(days=loan_period)
        return_date = None
        loan_status = 'active'

        # Determine loan status
        current_time = timezone.now()
        is_overdue = current_time > due_date
        is_lost = random.random() < PCT_LOANS_LOST

        if is_lost:
            loan_status = 'lost'
            copy_to_loan.copy_status = 'lost'
            copies_to_update.append(copy_to_loan)
        elif is_overdue:
             if random.random() < PCT_LOANS_RETURNED: # Returned but late
                 loan_status = 'returned'
                 return_date = fake.date_time_between(start_date=due_date + timedelta(days=1), end_date=current_time, tzinfo=timezone.get_current_timezone())
                 copy_to_loan.copy_status = 'available' # Returned, so available
                 copies_to_update.append(copy_to_loan)
             else: # Still overdue, not returned
                 loan_status = 'overdue'
                 copy_to_loan.copy_status = 'issued' # Still issued
                 copies_to_update.append(copy_to_loan) # Update status just in case
        elif random.random() < PCT_LOANS_RETURNED: # Returned on time
            loan_status = 'returned'
            return_date = fake.date_time_between(start_date=loan_date + timedelta(days=1), end_date=due_date, tzinfo=timezone.get_current_timezone())
            copy_to_loan.copy_status = 'available'
            copies_to_update.append(copy_to_loan)
        else: # Active, not yet due or returned
            loan_status = 'active'
            copy_to_loan.copy_status = 'issued'
            copies_to_update.append(copy_to_loan)


        loan = BookLoan(
            reader=reader,
            copy=copy_to_loan,
            location=location,
            loan_date=loan_date.date(),
            due_date=due_date.date(),
            return_date=return_date.date() if return_date else None,
            loan_status=loan_status
        )
        loans.append(loan)

        # Mark copy as used in this run and remove from available list
        issued_copy_ids.add(copy_to_loan.pk)
        available_copies.remove(copy_to_loan)
        created_loan_count += 1

        # Potentially create fine
        fine_reason = None
        if loan_status == 'overdue' and random.random() < FINE_CHANCE_OVERDUE:
             fine_reason = fine_reasons['overdue']
        elif loan_status == 'lost':
             fine_reason = fine_reasons['lost']
        # Add logic for 'damaged' if needed

        if fine_reason:
            fine_amount = Decimal(0)
            fine_per_day = reader.reader_type.fine_per_day if reader.reader_type else Decimal('10.00')

            if fine_reason == fine_reasons['overdue'] and not return_date: # Still overdue
                days_overdue = (current_time.date() - due_date.date()).days
                fine_amount = max(Decimal(0), Decimal(days_overdue) * fine_per_day)
            elif fine_reason == fine_reasons['overdue'] and return_date: # Returned late
                 days_overdue = (return_date.date() - due_date.date()).days
                 fine_amount = max(Decimal(0), Decimal(days_overdue) * fine_per_day)
            elif fine_reason == fine_reasons['lost'] and copy_to_loan.cost:
                 fine_amount = copy_to_loan.cost * Decimal(random.uniform(1.0, 1.5)) # Fine is cost + penalty
            elif fine_reason == fine_reasons['lost']:
                 fine_amount = Decimal(random.uniform(500.0, 3000.0)) # Default fine if cost unknown

            if fine_amount > 0:
                fine = LibraryFine(
                    reader=reader,
                    loan=loan, # Will be assigned after loan is saved
                    fine_amount=fine_amount.quantize(Decimal("0.01")),
                    fine_date=return_date.date() if return_date else current_time.date(), # Date fine was determined
                    fine_status=random.choice(fine_statuses) if random.random() > 0.3 else 'pending', # Mostly pending
                    fine_reason=fine_reason,
                    notes=f"Автоматически сгенерированный штраф ({fine_reason})."
                )
                fines.append({'fine_obj': fine, 'loan_ref': loan}) # Keep reference to loan obj

    # Bulk create loans first
    created_loans = BookLoan.objects.bulk_create(loans)
    print(f"Created {len(created_loans)} book loans.")
    loan_map = {(loan.reader_id, loan.copy_id, loan.loan_date): loan for loan in created_loans} # Create a map to find loans

    # Assign loan PKs to fines
    fines_to_create = []
    for fine_info in fines:
        loan_ref = fine_info['loan_ref']
        # Find the created loan object based on its attributes (less reliable than sequence, but bulk_create doesn't guarantee order)
        created_loan = loan_map.get((loan_ref.reader_id, loan_ref.copy_id, loan_ref.loan_date))
        if created_loan:
             fine_info['fine_obj'].loan = created_loan
             fines_to_create.append(fine_info['fine_obj'])
        else:
            print(f"Warning: Could not find matching created loan for fine (Reader: {loan_ref.reader_id}, Copy: {loan_ref.copy_id}, Date: {loan_ref.loan_date})")


    # Bulk create fines
    LibraryFine.objects.bulk_create(fines_to_create)
    print(f"Created {len(fines_to_create)} library fines.")

    # Bulk update copy statuses
    if copies_to_update:
         # Group updates by status to potentially optimize
         # This simple approach updates one by one effectively, but within a transaction
         print(f"Updating status for {len(copies_to_update)} book copies...")
         updated_count = 0
         for copy_instance in copies_to_update:
             # Ensure we only update fields that changed to minimize DB load
             # In this simple case, we only track 'copy_status'
             BookCopy.objects.filter(pk=copy_instance.pk).update(copy_status=copy_instance.copy_status)
             updated_count +=1
         print(f"Updated {updated_count} copy statuses.")


@transaction.atomic
def create_book_requests(users, books, locations):
    print("Creating Book Requests...")
    requests = []

    if not users or not books or not locations:
        print("Need users, books, and locations to create book requests.")
        return

    staff_users = list(CustomUser.objects.filter(role__in=['staff', 'admin'])) # Get staff/admin for processing
    request_statuses = [s[0] for s in BookRequest._meta.get_field('status').choices]

    num_requests = min(NUM_BOOK_REQUESTS, len(users) * len(books)) # Realistic limit
    created_count = 0
    attempt = 0
    max_attempts = num_requests * 2

    while created_count < num_requests and attempt < max_attempts:
        attempt += 1
        user = random.choice(users)
        book = random.choice(books)
        location = random.choice(locations)
        status = random.choice(request_statuses)
        processed_by = None
        processed_date = None
        notes = None

        # Some statuses imply processing
        if status not in ['pending', 'cancelled']:
            if staff_users:
                processed_by = random.choice(staff_users)
            processed_date = fake.date_time_between(start_date='-30d', end_date='now', tzinfo=timezone.get_current_timezone())
            if status == 'rejected' or random.random() < 0.2:
                 notes = fake.sentence() # Add a note for rejected or some processed requests

        # Check for potentially conflicting requests (simple check)
        # if BookRequest.objects.filter(user=user, book=book, status__in=['pending', 'approved', 'issued']).exists():
        #     continue # Skip if user already has an active request for this book

        requests.append(BookRequest(
            user=user,
            book=book,
            requested_location=location,
            request_date=fake.date_time_between(start_date='-60d', end_date='now', tzinfo=timezone.get_current_timezone()),
            status=status,
            processed_by=processed_by,
            processed_date=processed_date,
            notes=notes
            # loan field is tricky to populate here without complex matching logic
        ))
        created_count += 1

    BookRequest.objects.bulk_create(requests)
    print(f"Created {len(requests)} book requests.")


@transaction.atomic
def create_interlibrary_requests(readers, books):
    print("Creating Interlibrary Requests...")
    requests = []

    if not readers or not books:
        print("Need readers and books to create interlibrary requests.")
        return

    staff_users = list(CustomUser.objects.filter(role__in=['staff', 'admin']))
    request_statuses = [s[0] for s in InterlibraryRequest._meta.get_field('request_status').choices]

    num_requests = min(NUM_INTERLIBRARY_REQUESTS, len(readers) * len(books))
    created_count = 0
    attempt = 0
    max_attempts = num_requests * 2

    while created_count < num_requests and attempt < max_attempts:
        attempt += 1
        reader = random.choice(readers)
        book = random.choice(books) # In reality, these might be books *not* in the catalog
        status = random.choice(request_statuses)
        processed_by = None
        processed_date = None
        staff_notes = None

        # Some statuses imply processing
        if status not in ['pending', 'cancelled']:
             if staff_users:
                 processed_by = random.choice(staff_users)
             processed_date = fake.date_time_between(start_date='-30d', end_date='now', tzinfo=timezone.get_current_timezone())
             if status == 'rejected' or random.random() < 0.2:
                 staff_notes = fake.sentence()

        # Check for potentially conflicting requests (simple check)
        # if InterlibraryRequest.objects.filter(reader=reader, book=book, request_status__in=['pending', 'approved', 'processing', 'received', 'issued']).exists():
        #      continue

        requests.append(InterlibraryRequest(
            reader=reader,
            book=book,
            request_date=fake.date_between(start_date='-90d', end_date='today'),
            request_status=status,
            required_by_date=fake.date_between(start_date='today', end_date='+30d') if random.random() < 0.5 else None,
            notes=fake.paragraph(nb_sentences=2) if random.random() < 0.3 else None, # Reader notes
            processed_by=processed_by,
            processed_date=processed_date,
            staff_notes=staff_notes # Staff notes
        ))
        created_count += 1

    InterlibraryRequest.objects.bulk_create(requests)
    print(f"Created {len(requests)} interlibrary requests.")


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

    # Create base data
    locations = create_locations()
    authors = create_authors()

    # Create books and copies
    books, copies = create_books_and_copies(authors, locations)

    # Create users and readers
    users, readers = create_users_and_readers(reader_types)

    # Create loans and fines
    create_loans_and_fines(readers, copies, locations)

    # Add more function calls here for BookRequest, InterlibraryRequest if needed
    create_book_requests(users, books, locations)
    create_interlibrary_requests(readers, books)

    end_time = timezone.now()
    print(f"Script finished at: {end_time}")
    print(f"Total execution time: {end_time - start_time}")
    print("Database population complete.") 