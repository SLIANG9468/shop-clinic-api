from app.extensions import ma
from app.models import Customers

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customers #Creates a schema that validates the data as defined by our Customers Model
#       include_fk = True

customer_schema = CustomerSchema() #Creating an instance of my schema that I can actually use to validate, deserialize, and serialze JSON
customers_schema = CustomerSchema(many = True)