from time import sleep
from typing import Callable
from functools import partial

import requests
from logging import getLogger

from django.db import IntegrityError

from crawler.models import Post, PostToken, City, Category


class Crawler:
    crawler_name = 'Divar'
    url = 'https://api.divar.ir/v8/web-search/tehran/buy-residential'

    base_url = 'https://api.divar.ir/v8/web-search/tehran/buy-residential?{0}'
    post_url = "https://api.divar.ir/v8/posts-v2/web/{0}"

    def __init__(self, city_id=1, category_id=1, min_page: int = 0, max_page: int = 10, *args, **kwargs):
        self.logger = getLogger(name=self.crawler_name)
        self.city_id = city_id if city_id is not None else 1
        self.category_id = category_id if category_id is not None else 1
        self._max_page = max_page if max_page is not None else 0
        self._min_page = min_page if min_page is not None else 10
        self._token = None
        self.post_count = 0
        self.post_detail_count = 0
        self.post_data: dict = dict()
        self.normal_fields = {
            'webengage': (
                'brand_model', 'business_ref', 'business_type', 'cat_1', 'cat_2', 'cat_3', 'category', 'city', 'credit',
                'district', 'gender', 'image_count', 'originality', 'price', 'rent', 'status', 'token',),
            'share': ('image_url', 'title', 'web_url'),
            'seo': ('unavailable_after', 'title', 'description'),
            'contact': ('chat_enabled',),
        }
        self.post_detail_section_list_data_fields = {
            'section_name': 'LIST_DATA',

        }
        self.columns_name = Post.columns_name()

    def validation(self):
        try:
            City.objects.get(target_id=self.city_id)
            Category.objects.get(target_id=self.category_id)
        except City.DoesNotExist:
            raise 'City not found'
        except Category.DoesNotExist:
            raise 'Category not found'

    def _make_list_url(self, format_str: str) -> str:
        return self.base_url.format(format_str)

    def _make_detail_url(self, format_str: str) -> str:
        return self.post_url.format(format_str)

    def _iterate_page(self, page: int = 0):
        print(page)
        return self._make_list_url(f'page={page}')

    def _range_page(self):
        return range(self._min_page, (self._max_page) + 1)

    def _get_token_from_server_info(self, elm):
        return elm['action_log']['server_side_info']['info']['post_token']

    def _get_other_data_from_tokens_list(self, elm):
        result = {
            'top_description_text': elm['data']['top_description_text'],
            'middle_description_text': elm['data']['middle_description_text'],
            'bottom_description_text': elm['data']['bottom_description_text'],
            'red_text': elm['data']['red_text'],
            'checkable': elm['data']['checkable'],
            'label': elm['data']['label'],
            'label_color': elm['data']['label_color'],
            'is_checked': elm['data']['is_checked'],
            'has_chat': elm['data']['has_chat']
        }

        return result

    def _get_all_tokens(self):
        return PostToken.objects.active()

    def _is_new_token(self, token):
        return not PostToken.objects.filter(code=token).exists()

    def _send_request(self, url, callback_func: Callable = None):  # todo generalize
        state, data, counter = True, None, 0
        while state and counter < 4:
            try:
                r = requests.get(url, timeout=15)
            except:
                counter += 1
            if r.status_code == 404:
                if callback_func:
                    callback_func()
                state = False
            elif r.status_code == 200:
                state = False
                data = r.json()
            else:
                self.logger.error(f'Response status code is: {r.status_code} , url: {url}, request: {r}')
                sleep(5)
        return data

    def _callback_func_token_detail(self, token):
        PostToken.objects.filter(code=token).delete()
        self.logger.warning(f'token {token} deleted by callback function')
        # pass

    def _get_tokens(self):
        if not self._min_page and not self._max_page:
            result = self._incremental_pages()
        else:
            result = self._specific_pages()
        return result

    def _get_token(self, incremental: int):
        sleep(0.1)
        url = self._iterate_page(page=incremental)
        # r = requests.get(url)
        data = self._send_request(url=url)
        if data is None:
            return False
        elif len(data['web_widgets']['post_list']) == 0:
            return False
        extraction_data = {
            'first_post_date': data['first_post_date'],
            'last_post_date': data['last_post_date']}
        data = data.get('web_widgets').get('post_list')

        for i in data:
            self.post_count += 1
            try:
                post_token = None
                if i['widget_type'] == 'POST_ROW':
                    post_token = self._get_token_from_server_info(i)
                    extraction_data = {**extraction_data, **self._get_other_data_from_tokens_list(i)}
                    # post_token = i['data']['action']['payload']['token']
                elif i['widget_type'] == 'SELECTOR_ROW':
                    widget_list = i['data']['action']['payload']['modal_page']['widget_list']
                    for elm in widget_list:
                        post_token = self._get_token_from_server_info(elm)
                else:  # SECTION_DIVIDER_ROW
                    pass
                if post_token is not None and self._is_new_token(token=post_token):
                    new_token = PostToken.objects.create(**{'code': post_token})
                    Post.objects.update_or_create(token=new_token, defaults=extraction_data)
                else:
                    self.logger.warning(f'OLD TOKEN: {post_token}')
            except Exception as e:
                self.logger.warning(str(e))
                continue
        return True

    def _incremental_pages(self):
        all_home = 0
        state = True
        incremental = 0
        false_number = 0
        while state:
            incremental += 1
            res = self._get_token(incremental)
            if res:
                all_home += 1
            else:
                false_number += 1

            if false_number == 5:
                return all_home
            # break
        return all_home

    def _specific_pages(self):
        all_home = 0
        for p in self._range_page():
            res = self._get_token(p)
            if res:
                all_home += 1
        return all_home

    def _get_tokens_detail(self):

        all_active_token = self._get_all_tokens()
        for token in all_active_token:
            sleep(0.1)
            self._token = token
            url = self._make_detail_url(token.code)
            print(f'POST DETAIL URL: {url}')
            data = self._send_request(
                url=url,
                callback_func=partial(self._callback_func_token_detail, token=token.code))
            if data is None:
                continue
            self._get_one_token_detail(data)
            self.post_detail_count += 1
            print('********' * 5)

            # break
        return self.post_detail_count

    def _get_one_token_detail(self, data: dict) -> dict:
        self.post_data = {'city_name': 'tehran', 'token_code': self._token.code}
        for key in self.normal_fields.keys():
            for item in self.normal_fields[key]:
                self.post_data[item] = self._get_item(data.get(key), item)
        for elm in data.get('sections'):
            self._route_section(section=elm)

        seo_web_info = data['seo'].get('web_info')
        self.post_data['district_persian'] = seo_web_info.get('district_persian')  # elm['district_persian']
        self.post_data['city_persian'] = seo_web_info.get('city_persian')
        self.post_data['category_slug_persian'] = seo_web_info.get('category_slug_persian')
        # post_data = {**post_data, **{z['title']: z['value'] for z in data['seo'].get('web_info')}}
        # print(self.post_data)
        self._clear()
        self._write_post()
        return self.post_data

    def _write_post(self):
        self._token.is_active = False
        self._token.save()
        post = Post.objects.filter(token=self._token)
        self.post_data['token'] = self._token
        pre_pare_data = {}
        for k, v in self.post_data.items():
            if hasattr(Post, k):
                pre_pare_data[k] = v
        diff_ = len(pre_pare_data) - len(self.post_data)
        if diff_ != 0:
            self.logger.critical(f'diff pre_pare_data - self.post_data {diff_}')
        if not post.exists():
            try:
                Post.objects.create(**pre_pare_data)
            except IntegrityError:
                self.logger.critical(f'IntegrityError {self._token}')

        else:
            post.update(**pre_pare_data)

    def _clear(self):
        diff = list(set(self.post_data) - set(self.columns_name))
        for d in diff:
            fake_name_data = self.post_data.pop(d)
            real_name = list(self.columns_name.keys())[list(self.columns_name.values()).index(d)]
            self.post_data[real_name] = fake_name_data
        diff2 = list(set(self.columns_name) - set(self.post_data))
        if diff2:
            self.logger.critical(f'new column founded: {diff2}')

    def _get_item(self, data, item):
        result = data.get(item)
        return result

    def _route_section(self, section):
        exec(f'self._section_{section["section_name"]}(section)')

        # # if section["section_name"] == "IMAGE":
        #     self._section_IMAGE(section)
        # elif section["section_name"] == "BUSINESS_SECTION":
        #     self._section_BUSINESS_SECTION(section)
        # elif section["section_name"] == "TITLE":
        #     self._section_TITLE(section)
        # elif section["section_name"] == "NOTE":
        #     self._section_NOTE(section)
        # elif section["section_name"] == "DESCRIPTION":
        #     self._section_DESCRIPTION(section)
        # elif section["section_name"] == "STATIC":
        #     self._section_STATIC(section)
        # elif section["section_name"] == "TAGS":
        #     self._section_TAGS(section)
        # elif section["section_name"] == "BREADCRUMB":
        #     self._section_BREADCRUMB(section)
        # elif section["section_name"] == "INSPECTION":
        #     self._section_INSPECTION(section)
        # elif section["section_name"] == "SUGGESTION":
        #     self._section_SUGGESTION(section)
        # elif section["section_name"] == "MAP":
        #     self._section_MAP(section)
        # elif section["section_name"] == "LIST_DATA":
        #     self._section_LIST_DATA(section)

    def _section_IMAGE(self, section):
        pass

    def _section_BUSINESS_SECTION(self, section):
        pass

    def _section_TITLE(self, section):
        pass

    def _section_NOTE(self, section):
        pass

    def _section_DESCRIPTION(self, section):
        pass

    def _section_STATIC(self, section):
        pass

    def _section_TAGS(self, section):
        pass

    def _section_BREADCRUMB(self, section):
        pass

    def _section_INSPECTION(self, section):
        result = {}
        for widget in section['widgets'][0]['data']['widget_list']:
            if widget['widget_type'] == 'GROUP_INFO_ROW':
                for item in widget['data']['items']:
                    result[item['title']] = item['value']
        self.post_data = {**self.post_data, **result}

    def _section_SUGGESTION(self, section):
        suggestion_tokens: list = []
        widgets = section.get('widgets')
        if widgets is None:
            return None
        for data in section.get('widgets'):
            if data.get('action_log') is not None:
                suggestion_tokens.extend(data['action_log']['server_side_info']['info']['tokens'])
            else:
                suggestion_tokens.extend(data['items'][0]['action']['payload']['suggested_tokens'])

        self.post_data['suggestion_tokens'] = list(set(suggestion_tokens))

    def _section_MAP(self, section):
        data = section['widgets'][0]['data']
        location = data['location']
        self.post_data = {**self.post_data, **{
            'map_type': location.get('type'),
            'latitude': location.get('fuzzy_data', {}).get('point', {}).get('latitude'),
            'longitude': location.get('fuzzy_data', {}).get('point', {}).get('longitude'),
            'radius': location.get('fuzzy_data', {}).get('radius'),
            'map_image_url': data['image_url']
        }}

    def _section_LIST_DATA(self, section: dict):
        result, main_item, ef = {}, {}, {}
        widgets = section['widgets']

        for widget in widgets:
            if widget['widget_type'] in ["GROUP_INFO_ROW", 'UNEXPANDABLE_ROW']:
                if widget.get('data', {}).get('items') is not None:
                    for item in widget['data']['items']:
                        result[item['title']] = item['value']
                else:
                    result[widget['data']['title']] = widget['data']['value']
            elif widget['widget_type'] == 'GROUP_FEATURE_ROW':
                features = widget['data']
                main_item = {z['title']: z['value'] if z.get('value') else True for z in features['items']}
                extra_features = features.get('actions')
                ef = {}
                if extra_features is not None:
                    ef = {z['title']: z['value'] if z.get('value') else True for z in extra_features}
        # meter = widgets[0]['data']['items'][0]['value']
        # construction_year = widgets[0]['data']['items'][1]['value']
        # room = widgets[0]['data']['items'][2]['value']
        # total_price = widgets[1]['data']['value']
        # price_per_meter = widgets[2]['data']['value']
        #
        # widgets_3 = widgets[3]['data']
        # real_state_agency_title = widgets_3['value']
        # real_state_agency_business_ref = widgets_3.get('action', {}).get('payload', {}).get('business_ref',
        #                                                                                     None)
        # real_state_agency_slug = widgets_3.get('action', {}).get('payload', {}).get('slug', None)
        # real_state_agent = widgets[4]['data']['value']
        # real_state_agent_slug = widgets[4]['data']['action']['payload']['slug']
        #
        # ceil = widgets[5]['data']['value'
        self.post_data = {**self.post_data, **main_item, **ef, **result}


class DivarCrawler(Crawler):
    def crawl_new_tokens(self):
        self._min_page, self._max_page = None, None
        new_tokens = self._get_tokens()
        return {'post_count': self.post_count, 'new_tokens': new_tokens, }

    def crawl(self):
        # new_tokens = self._get_tokens()
        new_tokens = 0
        post_detail_count = self._get_tokens_detail()
        # post_detail_count = 0
        return {'post_count': self.post_count, 'new_tokens': new_tokens, 'post_detail_count': post_detail_count}

    def craw_related_tokens(self):
        related_tokens = Post.objects.active().filter(suggestion_tokens__isnull=False).values_list('suggestion_tokens',
                                                                                                   flat=True)
        new_tokens = []
        for tokens in related_tokens:
            new_tokens.extend(tokens)

        before_tokens = PostToken.objects.values_list('code', flat=True)
        new_tokens = list(set(new_tokens) - set(before_tokens))
        obs = [PostToken(code=code) for code in set(new_tokens)]
        PostToken.objects.bulk_create(obs, batch_size=500)
        return len(new_tokens)

    def get_image_random(self):
        data = self._send_request(self._make_list_url(''))
        if data is not None:
            images = []
            for widget in data['web_widgets']['post_list']:
                try:
                    images.append(widget['data']['image_url'][0]['src'])
                except:
                    pass
                if len(images) == 3:
                    break
            return images
