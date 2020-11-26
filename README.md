# Running this software
    Execute this command first to create one user of each role
        docker-compose run web python manage.py create_test_users

    Run tests
        docker-compose run web python manage.py test

    Run project
        docker-compose run web python manage.py migrate
        docker-compose run web python manage.py create_test_users
        docker-compose run --service-ports web

# Language and Framework
- The Api is built using Python, Django and uses rest_framework

# Password Hashing
- I have used PBKDF2 for hashing the passwords to increase the cost (time and resources) required to create (hence break) the hashes.
- The salts have been generated using "secret" python module.
- They are stored in database in the following format
        iterations$salt$hash

# Authentication
- For authentication, the HTTP_AUTHORIZATION header is used whose value will be "token <token>". In none of the APIs,
- User is asked "who is he"; rather, the token passes by user is used to determine who they are. Thereby preventing malicious users from impersonating as other users.
- The Authorization token is a random string generated using Python's "secret" module's token_urlsafe function.

# Database
- I have used postgresql. The username, password etc is specified in the dockerfile which can be loaded form env variable in production.

# API access protection
- In the api/permissions.py file, HasRoleAdmin, HasRoleAgent and HasRoleCustomer classed have been created.
- In every api, we can set them thereby easily setting up permissions and reducing chances of error.

# The List Loans API Endpoint
- This api applies filter to select only user's data from db when it finds that user is a customer.
- Then, it uses QueryParamFilter class in api/filters.py which accepts filter requests through query param.
- Filter params are like this : <column_name>__<operator>=value
- Its dynamic nature allows us to easily expand its features to support other type of columns and operators in future.

# Saving history of loan
- Classes LoanModel and LoanSnapshotModel inherit AbstractLoanModel. In a fairly low level part of code (overriding save() method in LoanModel),
- It is set to take a snapshot of LoanModel as soon as it is created/ updated. That lets us keep a history which can later be used to roll back.

# Testing
- Unit tests are written in api/tests.py
- Class DataBaseIntegrityTest checks for db integrity.
- Class ApiAccessTest actually calls the APIs to check if they are working as expected.
- I have written only one test case in the ApiAccessTest class, similar cases can be (must be) written for all the APIs.


# Sample requests and responses
    **Please refer docs/sample.txt**


# Notes
1. Edit user facility is available to agents. That means they can edit roles too and make themselves admins. I have written code to prevent it.
2. There should be a few more APIs like create user, delete user etc. I have not created them since it was not asked in the question.
3. I have also created a LoanPaymentModel which has columns amount, date and foreign key to LoanModel. But I have not created APIs to use it since it was not asked.
