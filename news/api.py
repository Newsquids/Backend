from datetime import timedelta
from django.utils import timezone
from ninja import Router
from ninja.errors import HttpError
from ninja_jwt.authentication import JWTAuth
from ninja_extra.shortcuts import get_object_or_exception
from news.schemas import NewsInOutSchema, NewsChannelSchema, NewsCategorySchema
from news.models import NewsChannel, NewsCategory, News
from typing import List

router = Router()

@router.post("/channel")
def create_channel(request, payload:NewsChannelSchema):
    NewsChannel.objects.create(**payload.dict())
    return {"msg" : "채널이 생성되었습니다."}

@router.post("/category")
def create_category(request, payload:NewsCategorySchema):
    NewsCategory.objects.create(**payload.dict())
    return {"msg" : "카테고리가 생성되었습니다."}

@router.post("")
def create_news(request, payload:NewsInOutSchema):
    dict_data = payload.dict()
    channel = NewsChannel.objects.get(channel_name=dict_data.pop("channel"))
    category = NewsCategory.objects.get(category_name=dict_data.pop("category"))
    News.objects.create(**dict_data, channel=channel, category=category)
    return {"msg" : "뉴스가 생성되었습니다."}