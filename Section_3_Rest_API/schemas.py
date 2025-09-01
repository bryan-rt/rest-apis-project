from marshmallow import Schema, fields

# “Plain” shapes used for nesting in responses
class PlainItemSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)      # loadable
    price = fields.Float(required=True)   # loadable

class PlainStoreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)      # loadable

class PlainTagSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()      # loadable

# Full schemas used by endpoints
class ItemSchema(PlainItemSchema):
    # client sends a store_id; we don’t accept a nested store on input
    store_id = fields.Int(required=True, load_only=True)
    # but we can include store details on output
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)

class ItemUpdateSchema(Schema):
    name = fields.Str()
    price = fields.Float()
    store_id = fields.Int()

class StoreSchema(PlainStoreSchema):
    # include items on output if you like
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)

class TagSchema(PlainTagSchema):
    # client sends a store_id; we don’t accept a nested store on input
    store_id = fields.Int(load_only=True)
    # but we can include store details on output
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)


class TagAndItemSchema(Schema):
    message = fields.Str()
    item = fields.Nested(ItemSchema())
    tag = fields.Nested(TagSchema())

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)

class UserRegisterSchema(Schema):
    username = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)