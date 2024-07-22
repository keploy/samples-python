from marshmallow import Schema, fields


class CreateTodoSchema(Schema):
    title = fields.Str(required=True)
    description = fields.Str(required=False)


class UpdateTodoSchema(Schema):
    title = fields.Str(required=False)
    description = fields.Str(required=False)