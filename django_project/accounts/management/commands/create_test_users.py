from django.core.management.base import BaseCommand

from accounts.models import User, AuthToken
from accounts.password_utils import make_password


class Command(BaseCommand):
    def handle(self, *args, **options):
        # create the admin user
        admin = User.get_or_create_user(
            username="admin@admin.com",
            password=make_password("admin"),
            role=User.ROLE_ADMIN,
            first_name="admin fn",
            last_name="admin ln"
        )

        agent = User.get_or_create_user(
            username="agent@agent.com",
            password=make_password("agent"),
            role=User.ROLE_AGENT,
            first_name="agent fn",
            last_name="agent ln"
        )

        customer = User.get_or_create_user(
            username="customer@customer.com",
            password=make_password("customer"),
            role=User.ROLE_CUSTOMER,
            first_name="customer fn",
            last_name="customer ln"
        )

        # create a tokens
        object = AuthToken(
            user=admin,
            token="11111"
        )
        object.save()
        admin_token = object.token

        object = AuthToken(
            user=agent,
            token="22222"
        )
        object.save()
        agent_token = object.token

        object = AuthToken(
            user=customer,
            token="33333"
        )

        object.save()
        customer_token = object.token

        print(f"Token for admin {admin.username} created : {admin_token}")
        print(f"Token for agent {agent.username} created : {agent_token}")
        print(f"Token for customer {customer.username} created : {customer_token}")
