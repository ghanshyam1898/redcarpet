from django.db.models import Q
from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

from api.permissions import *
from .filters import QueryParamFilter
from .models import LoanModel
from .serializers import UserSerializer, LoanSerializer


class StandardPagination(LimitOffsetPagination):
    default_limit = 20


class ListUsers(generics.ListAPIView):
    permission_classes = (HasRoleAdmin | HasRoleAgent,)
    serializer_class = UserSerializer
    model = serializer_class.Meta.model
    pagination_class = StandardPagination

    def get_queryset(self):
        return self.model.objects.all()


# Have marked ROLE AS NON EDITABLE FIELD to prevent agents from making themselves admins
class GetOrEditUser(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = (HasRoleAdmin | HasRoleAgent,)
    serializer_class = UserSerializer
    model = serializer_class.Meta.model
    pagination_class = StandardPagination
    lookup_field = 'username'

    def get_queryset(self):
        return self.model.objects.all()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        print(request.data)
        print(serializer.validated_data)
        self.perform_update(serializer)
        return Response(serializer.data)


class CreateNewLoan(generics.CreateAPIView):
    permission_classes = (HasRoleAgent,)
    serializer_class = LoanSerializer
    model = serializer_class.Meta.model


class EditLoan(generics.UpdateAPIView):
    permission_classes = (HasRoleAgent,)
    serializer_class = LoanSerializer
    model = serializer_class.Meta.model
    lookup_field = 'id'

    def get_queryset(self):
        return self.model.objects.all()

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

        # Once approved, loans cannot be edited
        if instance.status == LoanModel.LOAN_STATUS_APPROVED:
            raise ValidationError("Loan cannot be edited after being approved")

        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        print(request.data)
        print(serializer.validated_data)
        self.perform_update(serializer)
        return Response(serializer.data)


class ApproveLoan(APIView):
    permission_classes = (HasRoleAdmin,)

    def post(self, request):
        loan_id = request.data.get("loan_id")
        try:
            loan_id = int(loan_id)
        except (ValueError, TypeError):
            return Response({"error": "Please supply correct loan id"}, status=400)

        try:
            loan = LoanModel.objects.get(id=loan_id)
            loan.status = LoanModel.LOAN_STATUS_APPROVED
        except LoanModel.DoesNotExist:
            return Response({"error": f"Loan with id {loan_id} does not exist"}, status=404)

        return Response({"message": "Done"})


# accepts filters like this : ?emi_value__exact=20&emi_type__contains=type&loan_start_date__lt=2020-12-13
class ListLoans(generics.ListAPIView):
    permission_classes = (HasRoleAdmin | HasRoleAgent | HasRoleCustomer,)
    serializer_class = LoanSerializer
    model = serializer_class.Meta.model
    pagination_class = StandardPagination

    def get_queryset(self):
        query_param_filter = QueryParamFilter(self.model)
        filters = query_param_filter.get_filter_statement(self.request.GET)

        # if the user is customer, let them see their own loans only
        current_user = User.get_user_by_token(self.request)
        if current_user.role == User.ROLE_CUSTOMER:
            filters &= Q(user=current_user)

        return self.model.objects.filter(filters)
