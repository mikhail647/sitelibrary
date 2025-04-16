from celery import shared_task
from django.utils import timezone
from .models import BookLoan

@shared_task
def check_overdue_loans():
    loans = BookLoan.objects.filter(loan_status='active')
    for loan in loans:
        if hasattr(loan, 'check_overdue'):
            loan.check_overdue()
        else:
            if loan.due_date < timezone.now().date():
                loan.loan_status = 'overdue'
                loan.save()
            print(f"Warning: BookLoan model does not have a check_overdue method. Checked loan {loan.loan_id}.")
            pass