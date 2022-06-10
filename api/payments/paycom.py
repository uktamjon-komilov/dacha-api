from paycomuz.views import MerchantAPIView
from paycomuz import Paycom
from paycomuz.models import Transaction

from api.models import BalanceCharge, User


class CheckOrder(Paycom):
    def check_order(self, amount, account, *args, **kwargs):
        charge = BalanceCharge.objects.filter(id=account["order_id"])
        if charge.exists():
            charge = charge.first()
            print(float(charge.amount))
            print(float(amount) / 100)
            if float(charge.amount) == float(amount) / 100:
                return self.ORDER_FOUND
            else:
                return self.INVALID_AMOUNT
        else:
            return self.ORDER_NOT_FOND


    def successfully_payment(self, account, transaction, *args, **kwargs):
        transaction = Transaction.objects.filter(_id=account["id"])
        if transaction.exists():
            transaction = transaction.first()
            charge = BalanceCharge.objects.filter(id=transaction.order_key)
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
        else:
            return False


    def cancel_payment(self, account, transaction, *args, **kwargs):
        transaction = Transaction.objects.filter(_id=account["id"])
        if transaction.exists():
            transaction = transaction.first()
            charge = BalanceCharge.objects.filter(id=transaction.order_key)
            if charge.exists():
                charge = charge.first()
                charge.delete()
                return True
            else:
                return False
        else:
            return False


class PaycomView(MerchantAPIView):
    VALIDATE_CLASS = CheckOrder
