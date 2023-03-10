from ninja import Schema
from ninja_jwt.schema import TokenRefreshSerializer

class SignupSchema(Schema):
    email : str

class RefreshSchema(TokenRefreshSerializer):
    refresh: str