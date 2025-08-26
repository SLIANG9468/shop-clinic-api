from app.extensions import ma
from app.models import Mechanics

class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanics #Creates a schema that validates the data as defined by our Mechanics Model
#       include_fk = True

mechanic_schema = MechanicSchema() #Creating an instance of my schema that I can actually use to validate, deserialize, and serialze JSON
mechanics_schema = MechanicSchema(many = True)