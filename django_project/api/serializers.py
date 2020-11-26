from rest_framework import serializers

from accounts.models import User
from api.models import LoanModel, LoanPaymentModel


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "role", "first_name", "last_name")
        read_only_fields = ['id', 'role']


class LoanSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    username = serializers.CharField(write_only=True)
    # total_payment_till_date = serializers.SerializerMethodField()
    # current_balance = serializers.SerializerMethodField()

    class Meta:
        model = LoanModel
        read_only_fields = ['id', 'record_updated_timestamp', 'status']
        fields = '__all__'

    def create(self, validated_data):
        username = validated_data.pop("username", "")
        validated_data['user'] = User.objects.get(username=username)
        post = super(LoanSerializer, self).create(validated_data)
        return post

    # def get_total_payment_till_date(self, obj):
    #     return sum([item.amount for item in LoanPaymentModel.objects.filter(loan=obj)])
    #
    # def get_current_balance(self, obj):
    #     return "amount"
