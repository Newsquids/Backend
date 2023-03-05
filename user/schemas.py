from ninja import Schema
from datetime import datetime
from typing import Optional, List

class SignupSchema(Schema):
    email : str
