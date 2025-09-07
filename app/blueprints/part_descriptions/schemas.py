from app.extensions import ma
from app.models import Part_descriptions

class Part_descriptionsSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Part_descriptions #Creates a schema that validates the data as defined by our Part_descriptions Model
#       include_fk = True

part_description_schema = Part_descriptionsSchema() #Creating an instance of my schema that I can actually use to validate, deserialize, and serialze JSON
part_descriptions_schema = Part_descriptionsSchema(many = True)