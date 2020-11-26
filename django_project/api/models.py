from django.db import models

from accounts.models import User


class AbstractLoanModel(models.Model):
    LOAN_STATUS_NEW = "new"
    LOAN_STATUS_REJECTED = "rejected"
    LOAN_STATUS_APPROVED = "approved"

    LOAN_STATUS_CHOICES = (
        (LOAN_STATUS_NEW, LOAN_STATUS_NEW,),
        (LOAN_STATUS_APPROVED, LOAN_STATUS_APPROVED,),
        (LOAN_STATUS_REJECTED, LOAN_STATUS_REJECTED,),
    )

    EMI_TYPE_ADVANCE = "Advance"
    EMI_TYPE_ARREARS = "Arrears"

    EMI_TYPE_CHOICES = (
        (EMI_TYPE_ADVANCE, EMI_TYPE_ADVANCE,),
        (EMI_TYPE_ARREARS, EMI_TYPE_ARREARS,),
    )

    LOAN_TYPE_PERSONAL_LOAN = "Personal loan"
    LOAN_TYPE_HOME_EQUITY_LOAN = "Home equity loan"
    LOAN_TYPE_SMALL_BUSINESS_LOAN = "Business loan"

    LOAN_TYPE_CHOICES = (
        (LOAN_TYPE_PERSONAL_LOAN, LOAN_TYPE_PERSONAL_LOAN,),
        (LOAN_TYPE_SMALL_BUSINESS_LOAN, LOAN_TYPE_SMALL_BUSINESS_LOAN,),
        (LOAN_TYPE_HOME_EQUITY_LOAN, LOAN_TYPE_HOME_EQUITY_LOAN,),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    emi_value = models.FloatField()
    emi_type = models.CharField(max_length=30, choices=EMI_TYPE_CHOICES)
    interest_rate = models.FloatField()
    payment_recurrence_days = models.FloatField()
    processing_charge = models.FloatField()
    type_of_loan = models.CharField(max_length=40, choices=LOAN_TYPE_CHOICES)
    scheme = models.CharField(max_length=30)
    total_period_of_loan_days = models.IntegerField()
    collateral = models.CharField(max_length=50)
    status = models.CharField(max_length=20, default=LOAN_STATUS_NEW)
    loan_start_date = models.DateField()


class LoanSnapshotModel(AbstractLoanModel):
    timestamp = models.DateTimeField(auto_now_add=True)


class LoanModel(AbstractLoanModel):
    def save(self, **kwargs):
        super(LoanModel, self).save()

        # save a copy of data for the history
        columns = [item.name for item in AbstractLoanModel._meta.fields]
        columns.remove('id')
        data = dict()
        for column in columns:
            data[column] = getattr(self, column)

        LoanSnapshotModel.objects.create(**data)


class LoanPaymentModel(models.Model):
    loan = models.ForeignKey(LoanModel, on_delete=models.CASCADE)
    amount = models.FloatField()
    payment_date = models.DateField(auto_now_add=True)
