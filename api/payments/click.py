from clickuz.views import ClickUzMerchantAPIView
from clickuz import ClickUz

from api.models import BalanceCharge, User


class OrderCheckAndPayment(ClickUz):
    def check_order(self, order_id: str, amount: str):
        charge = BalanceCharge.objects.filter(id=order_id)
        if charge.exists():
            charge = charge.first()
            if float(charge.amount) == float(amount):
                return self.ORDER_FOUND
            else:
                return self.INVALID_AMOUNT
        else:
            return self.ORDER_NOT_FOUN

    def successfully_payment(self, order_id: str, transaction: object):
        charge = BalanceCharge.objects.filter(id=order_id)
        if charge.exists():
            charge = charge.first()
            user = User.objects.get(id=charge.user.id)
            user.balance += charge.amount
            user.save()
            charge.completed = True
            charge.save()
            return True
        else:
            return False


class ClickView(ClickUzMerchantAPIView):
    VALIDATE_CLASS = OrderCheckAndPayment
