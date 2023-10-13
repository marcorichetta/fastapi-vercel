from marshmallow import Schema, fields, ValidationError


class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    url = fields.Url(required=True)
    description = fields.Str()
    price = fields.Float()
    userid = fields.Int(required=True)


class AddProductModelSchema(Schema):
    name = fields.Str(required=True)
    url = fields.Url(required=True)
    description = fields.Str()
    price = fields.Float()
    userid = fields.Int(required=True)


class UpdateProductModelSchema(Schema):
    name = fields.Str()
    url = fields.Url()
    description = fields.Str()
    price = fields.Float()
