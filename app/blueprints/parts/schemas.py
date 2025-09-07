from app.extensions import ma
from app.models import Parts

class PartSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Parts #Creates a schema that validates the data as defined by our Parts Model
#       include_fk = True

part_schema = PartSchema() #Creating an instance of my schema that I can actually use to validate, deserialize, and serialze JSON
parts_schema = PartSchema(many = True)