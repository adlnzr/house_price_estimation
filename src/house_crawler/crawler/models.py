from django.db import models

from crawler.queryset import PostTokenManager, PostManager


class BaseModel(models.Model):
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class City(BaseModel):
    name = models.CharField(max_length=32, db_index=True)


class Category(BaseModel):
    name = models.CharField(max_length=64)


class VacancyType(BaseModel):
    name = models.CharField(max_length=64)
    code = models.CharField(max_length=64)


class Vacancy(BaseModel):
    name = models.CharField(max_length=64)


class PostToken(BaseModel):
    code = models.CharField(max_length=64, unique=True)

    objects = PostTokenManager()

    def __str__(self):
        return self.code


class Post(BaseModel):
    objects = PostManager()

    token = models.OneToOneField(PostToken, on_delete=models.CASCADE)
    token_code = models.CharField(max_length=16, null=True, blank=True)
    city_rel = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)
    city_name = models.CharField(max_length=255, null=True, blank=True)

    image_count = models.IntegerField(null=True, blank=True)
    title = models.CharField(max_length=255, null=True, blank=True)
    top_description_text = models.CharField(max_length=255, null=True, blank=True)
    middle_description_text = models.CharField(max_length=255, null=True, blank=True)
    bottom_description_text = models.CharField(max_length=255, null=True, blank=True)
    red_text = models.CharField(max_length=255, null=True, blank=True)
    checkable = models.CharField(max_length=255, null=True, blank=True)
    label = models.CharField(max_length=255, null=True, blank=True)
    label_color = models.CharField(max_length=255, null=True, blank=True)
    is_checked = models.CharField(max_length=255, null=True, blank=True)
    has_chat = models.CharField(max_length=255, null=True, blank=True)
    district_persian = models.CharField(max_length=255, null=True, blank=True)
    city_persian = models.CharField(max_length=255, null=True, blank=True)
    category_slug_persian = models.CharField(max_length=255, null=True, blank=True)
    last_post_date = models.BigIntegerField(null=True, blank=True)
    first_post_date = models.BigIntegerField(null=True, blank=True)
    brand_model = models.CharField(max_length=255, null=True, blank=True)
    business_ref = models.CharField(max_length=255, null=True, blank=True)
    business_type = models.CharField(max_length=255, null=True, blank=True)
    cat_1 = models.CharField(max_length=255, null=True, blank=True)
    cat_2 = models.CharField(max_length=255, null=True, blank=True)
    cat_3 = models.CharField(max_length=255, null=True, blank=True)
    category = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    credit = models.CharField(max_length=255, null=True, blank=True)
    district = models.CharField(max_length=255, null=True, blank=True)
    gender = models.CharField(max_length=255, null=True, blank=True)
    originality = models.CharField(max_length=255, null=True, blank=True)
    price = models.CharField(max_length=255, null=True, blank=True)
    rent = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255, null=True, blank=True)
    image_url = models.CharField(max_length=255, null=True, blank=True)
    web_url = models.CharField(max_length=255, null=True, blank=True)
    unavailable_after = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    chat_enabled = models.CharField(max_length=255, null=True, blank=True)
    suggestion_tokens = models.JSONField(null=True, blank=True)
    elevator = models.CharField(max_length=16, null=True, blank=True)
    not_elevator = models.CharField(max_length=16, null=True, blank=True)
    parking = models.CharField(max_length=16, null=True, blank=True)
    not_parking = models.CharField(max_length=16, null=True, blank=True)
    depot = models.CharField(max_length=16, null=True, blank=True)
    not_depot = models.CharField(max_length=16, null=True, blank=True)
    map_type = models.CharField(max_length=255, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    radius = models.FloatField(max_length=255, null=True, blank=True)
    map_image_url = models.CharField(max_length=255, null=True, blank=True)
    balcony = models.CharField(max_length=255, null=True, blank=True)
    not_balcony = models.CharField(max_length=255, null=True, blank=True)
    check_cost_limit = models.CharField(max_length=255, null=True, blank=True)
    check_cost = models.CharField(max_length=255, null=True, blank=True)
    pricing_cost = models.CharField(max_length=255, null=True, blank=True)
    meter = models.CharField(max_length=32, null=True, blank=True)
    rooms = models.CharField(max_length=32, null=True, blank=True)
    floor = models.CharField(max_length=32, null=True, blank=True)
    total_price = models.CharField(max_length=32, null=True, blank=True)
    price_per_meter = models.CharField(max_length=32, null=True, blank=True)
    real_state_agency = models.CharField(max_length=32, null=True, blank=True)
    real_state_agent = models.CharField(max_length=32, null=True, blank=True)
    year = models.CharField(max_length=32, null=True, blank=True)
    land_meter = models.CharField(max_length=32, null=True, blank=True)
    house_status = models.CharField(max_length=32, null=True, blank=True)

    def __str__(self):
        return f"{self.__class__}: {self.token}"

    @classmethod
    def columns_name(cls):
        return {
            'token_code': 'token_code',
            'brand_model': 'brand_model',
            'business_ref': 'business_ref',
            'business_type': 'business_type',
            'cat_1': 'cat_1',
            'cat_2': 'cat_2',
            'cat_3': 'cat_3',
            'category': 'category',
            'city': 'city',
            'credit': 'credit',
            'district': 'district',
            'gender': 'gender',
            'image_count': 'image_count',
            'originality': 'originality',
            'price': 'price',
            'rent': 'rent',
            'status': 'status',
            'token': 'token',
            'image_url': 'image_url',
            'title': 'title',
            'web_url': 'web_url',
            'unavailable_after': 'unavailable_after',
            'description': 'description',
            'chat_enabled': 'chat_enabled',
            'suggestion_tokens': 'suggestion_tokens',
            'elevator': 'آسانسور',
            'not_elevator': 'آسانسور ندارد',
            'parking': 'پارکینگ',
            'not_parking': 'پارکینگ ندارد',
            'depot': 'انباری',
            'not_depot': 'انباری ندارد',
            'district_persian': 'district_persian',
            'city_persian': 'city_persian',
            'category_slug_persian': 'category_slug_persian',
            'top_description_text': 'top_description_text',
            'middle_description_text': 'middle_description_text',
            'bottom_description_text': 'bottom_description_text',
            'red_text': 'red_text',
            'checkable': 'checkable',
            'label': 'label',
            'label_color': 'label_color',
            'is_checked': 'is_checked',
            'has_chat': 'has_chat',
            'city_name': 'city_name',
            'last_post_date': 'last_post_date',
            'first_post_date': 'first_post_date',
            'map_type': 'map_type',
            'latitude': 'latitude',
            'longitude': 'longitude',
            'radius': 'radius',
            'map_image_url': 'map_image_url',
            'balcony': 'بالکن',
            'not_balcony': 'بالکن ندارد',
            'check_cost_limit': 'حدود هزینه کارشناسی',
            'check_cost': 'هزینه کارشناسی',
            'pricing_cost': 'هزینه قیمت‌گذاری',
            'meter': 'متراژ',
            'land_meter': 'متراژ زمین',
            'rooms': 'اتاق',
            'floor': 'طبقه',
            'total_price': 'قیمت کل',
            'price_per_meter': 'قیمت هر متر',
            'real_state_agency': 'آژانس املاک',
            'real_state_agent': 'مشاور املاک',
            'year': 'ساخت',
            'house_status': 'وضعیت این ملک',
        }
