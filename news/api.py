from datetime import timedelta
from django.utils import timezone
from ninja import Router
from ninja.pagination import paginate, PageNumberPagination
from ninja.errors import HttpError
from ninja_jwt.authentication import JWTAuth
from ninja_extra.shortcuts import get_object_or_exception
from news.schemas import NewsInSchema, NewsOutSchema, NewsChannelSchema, NewsCategorySchema, NewsEmail
from news.models import NewsChannel, NewsCategory, News
from typing import List
from django.core.mail.message import EmailMessage

router = Router()

@router.post("/channel")
def create_channel(request, payload:NewsChannelSchema):
    for channel in payload.channels:
        NewsChannel.objects.create(channel_name=channel)
    return {"msg" : "채널이 생성되었습니다."}

@router.post("/category")
def create_category(request, payload:NewsCategorySchema):
    for category in payload.categories:
        NewsCategory.objects.create(category_name=category)
    return {"msg" : "카테고리가 생성되었습니다."}

@router.post("")
def create_news(request, payload:NewsInSchema):
    dict_data = payload.dict()
    channel = NewsChannel.objects.get(channel_name=dict_data.pop("channel"))
    category = NewsCategory.objects.get(category_name=dict_data.pop("category"))
    News.objects.create(**dict_data, channel=channel, category=category)
    return {"msg" : "뉴스가 생성되었습니다."}

@router.get("", response=NewsOutSchema)
def read_news(request, page:int, channel:str, category:str = None):
    channel_obj = NewsChannel.objects.get(channel_name=channel)
    if category != None:
        category = NewsCategory.objects.get(category_name=category)
        News_obj = News.objects.filter(channel=channel_obj, category=category).all().order_by('-create_time','-id')[(page-1)*5:page*5]
    else:
        News_obj = News.objects.filter(channel=channel_obj).order_by('-create_time','-id').all()[(page-1)*5:page*5]
    res = {"newsItems" : []}
    for obj in News_obj:
        tem_dict = {}
        tem_dict['newsId'] = obj.id
        tem_dict['newsOriginLink'] = obj.link
        tem_dict['newsChannel'] = obj.channel.channel_name
        tem_dict['newsImage'] = obj.image
        tem_dict['newsHeadline'] = obj.headline
        tem_dict['newsCategory'] = obj.category.category_name
        tem_dict['newsDate'] = obj.create_time
        tem_dict['isBookmarked'] = False
        res["newsItems"].append(tem_dict)
    return res

@router.post("/email")
def send_email(request, payload:NewsEmail):
    mail = EmailMessage('test subject','test content', to=payload.emails)
    mail.send()
    return {"msg" : "메일 발송"}