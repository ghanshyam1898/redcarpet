from django.db import IntegrityError
from django.test import Client
from django.test import TestCase

from accounts.models import *
from api.models import LoanModel, AbstractLoanModel, LoanSnapshotModel


class DataBaseIntegrityTest(TestCase):
    def setUp(self):
        # create admin user
        self.admin_user = User.get_or_create_user(
            username="admin@admin.com",
            password=make_password("admin"),
            role=User.ROLE_ADMIN,
            first_name="admin fn",
            last_name="admin ln"
        )

        # create admin token
        self.admin_token = AuthToken.get_or_create_token(self.admin_user)

    def test_user_table_integrity(self):
        # Should raise error. This user was already created during setup.
        with self.assertRaises(IntegrityError):
            User.objects.create(
                username="admin@admin.com",
                password=make_password("admin"),
                role=User.ROLE_ADMIN
            )

    def test_loan_history_feature(self):
        LoanModel.objects.create(
            user=self.admin_user,
            emi_value=20.0,
            emi_type=AbstractLoanModel.EMI_TYPE_ADVANCE,
            interest_rate=12.0,
            payment_recurrence_days=30,
            processing_charge=1000,
            type_of_loan=AbstractLoanModel.LOAN_TYPE_HOME_EQUITY_LOAN,
            scheme="Ujala yogana",
            total_period_of_loan_days=3650,
            collateral="House as collateral",
            loan_start_date="2020-12-12"
        )

        # check if first snapshot was created
        self.assertEqual(LoanSnapshotModel.objects.count(), 1)
        loan = LoanModel.objects.first()
        loan.loan_start_date = "2020-12-13"
        loan.save()  # update an entry

        self.assertEqual(LoanSnapshotModel.objects.count(), 2)  # check if 2nd snapshot was created


class ApiAccessTest(TestCase):
    def setUp(self):
        self.api_client = Client()

        self.admin_user = User.get_or_create_user(
            username="admin@admin.com",
            password=make_password("admin"),
            role=User.ROLE_ADMIN,
            first_name="admin fn",
            last_name="admin ln"
        )

        self.agent_user = User.get_or_create_user(
            username="agent@agent.com",
            password=make_password("agent"),
            role=User.ROLE_AGENT
        )

        self.customer_user = User.get_or_create_user(
            username="customer@customer.com",
            password=make_password("customer"),
            role=User.ROLE_CUSTOMER
        )

        # create a tokens
        self.admin_token = AuthToken.get_or_create_token(self.admin_user)
        self.agent_token = AuthToken.get_or_create_token(self.agent_user)
        self.customer_token = AuthToken.get_or_create_token(self.customer_user)

        loan_data = {"user": self.customer_user, "emi_value": 20.0, "emi_type": AbstractLoanModel.EMI_TYPE_ADVANCE,
                     "interest_rate": 12.0, "payment_recurrence_days": 30, "processing_charge": 1000,
                     "type_of_loan": AbstractLoanModel.LOAN_TYPE_HOME_EQUITY_LOAN, "scheme": "Ujala yogana",
                     "total_period_of_loan_days": 3650, "collateral": "House as collateral",
                     "loan_start_date": "2020-12-12"}

        # create a loan for customer
        LoanModel.objects.create(**loan_data)

        # create a loan for admin
        loan_data["user"] = self.admin_user
        LoanModel.objects.create(**loan_data)

    def get_sum_of_response_data_count_through_paginated_api(self, start_page, headers):
        next_page = start_page
        total_count = 0
        while next_page is not None:
            response = self.api_client.get(next_page, follow=True, **headers)
            self.assertEqual(response.status_code, 200)
            total_count += response.json()['count']
            next_page = response.json()['next']

        return total_count

    def test_list_users(self):
        headers = dict()
        # test as admin
        headers["HTTP_AUTHORIZATION"] = f"token {self.admin_token}"
        response = self.api_client.get("/api/list_users", follow=True, **headers)
        self.assertEqual(response.status_code, 200)

        # test as agent
        headers["HTTP_AUTHORIZATION"] = f"token {self.agent_token}"
        response = self.api_client.get("/api/list_users", follow=True, **headers)
        self.assertEqual(response.status_code, 200)

        # test as customer
        headers["HTTP_AUTHORIZATION"] = f"token {self.customer_token}"
        response = self.api_client.get("/api/list_users", follow=True, **headers)
        self.assertEqual(response.status_code, 403)  # customers are forbidden from listing users

    def test_list_loans(self):
        headers = dict()
        # test as admin
        headers["HTTP_AUTHORIZATION"] = f"token {self.admin_token}"
        self.assertEqual(self.get_sum_of_response_data_count_through_paginated_api("/api/list_loans", headers),
                         LoanModel.objects.all().count())  # all loans returned

        # test as agent
        headers["HTTP_AUTHORIZATION"] = f"token {self.agent_token}"
        self.assertEqual(self.get_sum_of_response_data_count_through_paginated_api("/api/list_loans", headers),
                         LoanModel.objects.all().count())  # all loans returned

        # test as customer
        headers["HTTP_AUTHORIZATION"] = f"token {self.customer_token}"
        self.assertEqual(self.get_sum_of_response_data_count_through_paginated_api("/api/list_loans", headers),
                         LoanModel.objects.filter(user=self.customer_user).count())  # loans for only customer returned

    # similarly, we can write tests for other apis too
