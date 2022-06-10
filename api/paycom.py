from paycomuz.views import MerchantAPIView
from paycomuz import Paycom
from paycomuz.models import Transaction

from api.models import BalanceCharge


class CheckOrder(Paycom):
    def check_order(self, amount, account, *args, **kwargs):
        print(amount)
        print(account)
        charge = BalanceCharge.objects.filter(id=account["order_id"])
        if charge.exists():
            charge = charge.first()
            print(amount, charge.amount)
            if float(charge.amount) == float(amount):
                return self.ORDER_FOUND
            else:
                return self.INVALID_AMOUNT
        else:
            return self.ORDER_NOT_FOND
        
    def successfully_payment(self, account, transaction, *args, **kwargs):
        print(account)
        transaction = Transaction.objects.filter(_id=account["id"])
        if transaction.exists():
            transaction = transaction.first()
            print(transaction.order_key)
            charge = BalanceCharge.objects.filter(id=transaction.order_key)
            if charge.exists():
                charge = charge.first()
                charge.completed = True
                charge.save()
                if charge.user:
                    try:
                        user = User.objects.get(id=charge.user.id)
                        print(user.balance)
                        user.balance = user.balance + charge.amount
                        print(user.balance)
                        user.save()
                    except:
                        pass
                return True
            else:
                return False
        else:
            return False

    def cancel_payment(self, account, transaction, *args, **kwargs):
        print(account)
        transaction = Transaction.objects.filter(_id=account["id"])
        if transaction.exists():
            transaction = transaction.first()
            print(transaction.order_key)
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
