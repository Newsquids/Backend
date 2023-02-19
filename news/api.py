from datetime import timedelta
from django.utils import timezone
from ninja import Router
from ninja.pagination import paginate, PageNumberPagination
from ninja.errors import HttpError
from ninja_jwt.authentication import JWTAuth
from ninja_extra.shortcuts import get_object_or_exception
from news.schemas import NewsInSchema, NewsOutSchema, NewsChannelSchema, NewsCategorySchema
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
def create_news(request, payload:NewsInSchema):
    dict_data = payload.dict()
    channel = NewsChannel.objects.get(channel_name=dict_data.pop("channel"))
    category = NewsCategory.objects.get(category_name=dict_data.pop("category"))
    News.objects.create(**dict_data, channel=channel, category=category)
    return {"msg" : "뉴스가 생성되었습니다."}

@router.get("", response=List[NewsOutSchema])
@paginate(PageNumberPagination, page_size=5)
def read_news(request, channel:str, category:str = None):
    channel = NewsChannel.objects.get(channel_name=channel)
    if category != None:
        category = NewsCategory.objects.get(category_name=category)
        return News.objects.filter(channel=channel, category=category).all().order_by('-create_time','-id')
    return News.objects.filter(channel=channel).all().order_by('-create_time','-id')