from django.db.models import Q


class QueryParamFilter:
    SUPPORTED_FIELD_TYPES = ('FloatField', 'CharField', 'IntegerField', 'DateField',)
    SUPPORTED_OPERATORS = ('exact', 'lt', 'gt', 'lte', 'gte', 'contains', 'icontains')
    model = None
    all_field_names = []

    def __init__(self, model):
        self.model = model
        self.all_field_names = [item.name for item in model._meta.fields]

    # translates operator provided in query param to the one which is acceptable to django orm apis
    @staticmethod
    def operator_to_orm_modifier(operator):
        if operator == 'exact':
            return ""
        else:
            return "__" + operator

    # returns eg CharField, BooleanField etc. Can be used to validate if given operator works with given field
    def get_validated_field_type(self, field_name):
        if field_name is None:
            return None
        field_type = self.model._meta.get_field(field_name).get_internal_type()
        return field_type if field_type in self.SUPPORTED_FIELD_TYPES else None

    # returns field_name or None
    def get_validated_field_name(self, name_with_operator):
        if "__" not in name_with_operator:
            return None
        name = name_with_operator.split("__")[0]
        return name if name in self.all_field_names else None

    # returns operator or None
    def get_validated_operator(self, name_with_operator):
        if "__" not in name_with_operator:
            return None
        operator = name_with_operator.split("__")[1]
        return operator if operator in self.SUPPORTED_OPERATORS else None

    # returns "Q" object to be used with "filter"
    def get_filter_statement(self, request_get):
        filter_statement = Q()
        for name_with_operator in request_get:
            field_name = self.get_validated_field_name(name_with_operator)
            operator = self.get_validated_operator(name_with_operator)
            field_type = self.get_validated_field_type(field_name)

            if field_name is None or operator is None or field_type is None:
                # don't raise error, just skip it
                print(f"Either field_name or operator is None; or, field type is unsupported "
                      f"for {name_with_operator}. Skipping.")
                continue

            data = {field_name + QueryParamFilter.operator_to_orm_modifier(operator): request_get[name_with_operator]}
            filter_statement &= Q(**data)

        return filter_statement
