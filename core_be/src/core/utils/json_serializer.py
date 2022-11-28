from django.core.serializers.json import DjangoJSONEncoder, Serializer as JsonSerializer
from prices import Money

MONEY_TYPE = "Money"

class Serializer(JsonSerializer):
    def _init_options(self):
        super()._init_options()
        self.json_kwargs["cls"] = CustomJsonEncoder


class CustomJsonEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, Money):
            return {"_type": MONEY_TYPE, "amount": obj.amount, "currency": obj.currency}
        return super().default(obj)
