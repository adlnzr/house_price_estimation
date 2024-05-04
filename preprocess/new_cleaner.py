import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn
import utils


class Cleaner:
    def __init__(self, df: pd.DataFrame = None, ):
        self.raw_df = df
        self.df = self.raw_df.copy()
        self.cols_number = ['meter', 'rooms']  # Adel : removed 'rent','total_price', 'price_per_meter'
        self.cols_bool = ['balcony', 'elevator', 'depot', 'parking']
        self.cols_need_to_fill = ['floor']  # Adel: removed 'real_state_agency'
        self.cols_drop = [
            'city_rel', 'top_description_text', 'middle_description_text', 'bottom_description_text', 'red_text',
            'checkable', 'label', 'label_color', 'is_checked', 'has_chat', 'last_post_date', 'first_post_date',
            'brand_model',
            'gender', 'originality', 'status', 'not_elevator', 'not_parking', 'not_depot', 'map_type', 'latitude',
            'longitude',
            'radius', 'map_image_url', 'not_balcony', 'check_cost_limit', 'check_cost', 'pricing_cost',
            'land_meter', 'house_status',
            'category_slug_persian', 'title', 'token_code', 'web_url', 'rent', 'price_per_meter',
            'image_count', 'id', 'token', 'city_name', 'description', 'credit', 'suggestion_tokens',
            'unavailable_after', 'is_active', 'district_persian', 'chat_enabled', 'city_persian',
            'business_ref', 'cat_1', 'cat_2', 'cat_3', 'image_url', 'city', 'category', 'balcony', 'total_price',
            'created_at', 'real_state_agency',

        ]  # Adel - some more columns droped
        self.drop_na_cols = ['meter', 'floor', 'price']  # added by Adel
        self.route = {'func_number': self.cols_number, 'func_bool': self.cols_bool, 'func_cols_drop': self.cols_drop,
                      'func_need_cat_fill': self.cols_need_to_fill, 'func_floor': ['floor'],
                      'func_drop_na_cols': self.drop_na_cols, 'func_ultimate_drop': ['floor']}
        self.pipe_order = [
            'func_cols_drop',
            'func_bool',
            'func_number',
            'func_need_cat_fill',
            'func_floor',
            'func_drop_na_cols',
            'func_meter_cleaner',
            'func_floor_',
            'func_agent_binary',
            'func_price_m2',
            'func_age',
            'func_rooms',
            'func_price',
            'func_ultimate_drop']

        self.ultimate_drop = ['floor', 'year']  # Adel: this column should be removed at the end of pipe_order

    def fit(self, X):
        pass

    def transform(self):
        for pipe in self.pipe_order:
            exec(f'self.{pipe}()')
        return self.df

    def func_number(self):
        func_name = 'func_number'
        for field in self.route[func_name]:
            self.df[field] = self.df[field].map(self.convart_persion_number)

    def func_bool(self):
        func_name = 'func_bool'

    def func_need_cat_fill(self):
        func_name = 'func_need_cat_fill'
        for field in self.route[func_name]:
            if field == 'real_state_agency':
                self.df[field] = self.df[field].fillna('personal')
            elif field == 'floor':
                self.df[field] = self.df[field].fillna(0)

    def func_cols_drop(self):
        func_name = 'func_cols_drop'
        self.df = self.df.drop(self.route[func_name], axis=1)

    def func_floor(self):
        field_name = 'floor'
        self.df[field_name] = self.df.floor.str.replace('زیر همکف', '−۱').str.replace('زیرهمکف', '−۱'). \
            str.replace('همکف', '۰').str.replace('از بیشتر از', ' '). \
            str.replace('+۳۰', '۳۰').str.replace('از', '_').str.replace(' ', '_').str.replace('___', '_')

        not_nan_values = self.df.loc[self.df[field_name].isna() == False, field_name]
        self.df.loc[self.df[field_name].isna() == False, field_name] = not_nan_values.map(
            utils.convert_fa_number_to_en)

        self.df[field_name] = self.df[field_name].map(self.floor_and_all)

    def floor_and_all(self, value):
        try:
            if np.isnan(value):
                return None
        except Exception:
            pass
        return value.split('_')[:2] if '_' in value else (value, None)

    def convart_persion_number(self, value):
        if not value:  # Return empty string if value is empty
            return value

        n = None
        if isinstance(value, str):
            n = utils.convert_fa_number_to_en(value)
        return n

    def func_drop_na_cols(self):  # added by Adel
        func_name = 'func_drop_na_cols'
        self.df.dropna(subset=self.route[func_name], inplace=True)

    def func_meter_cleaner(self):  # added by Adel
        # self.df.loc[:,'meter'] = self.df.loc[:,'meter'].apply(lambda x: x.replace('متر',''))
        # self.df.loc[:,'meter'] = self.df.loc[:,'meter'].apply(lambda x: x.replace('٬',''))
        self.df.loc[:, 'meter'] = self.df['meter'].apply(lambda x: int(x))

    def func_floor_(self):  # added by Adel
        self.df['floor_0'] = self.df['floor'].apply(lambda x: x[0])
        self.df['floor_0'] = self.df.loc[:, 'floor_0'].str.replace('بدون اتاق', '')
        self.df['floor_0'] = self.df.loc[:, 'floor_0'].str.replace('−', '-').astype(int)

    def func_agent_binary(self):  # added by Adel
        self.df['real_state_agent'] = self.df['real_state_agent'].apply(lambda x: 1 if pd.notna(x) else 0)

    def func_price_m2(self):  # added by Adel
        self.df['price_m2'] = self.df['price'] / self.df['meter']

    def func_ultimate_drop(self):  # added by Adel
        func_name = 'func_ultimate_drop'
        self.df = self.df.drop(self.route[func_name], axis=1)

    def func_age(self):  # added by Adel
        self.df.loc[:, 'year'] = self.df['year'].apply(lambda x: 1369 if isinstance(x, str) and 'قبل از' in x else x)
        self.df.loc[:, 'year'] = self.df['year'].apply(lambda x: int(x))
        self.df.loc[:, 'age'] = self.df['year'].apply(lambda x: 1402 - x)

    def func_rooms(self):  # added by Adel
        self.df['rooms'] = self.df.loc[:, 'rooms'].str.replace('بدون اتاق', 'z')
        self.df['rooms'] = self.df.loc[:, 'rooms'].str.replace('z', '0')

    def func_price(self):  # added by Adel
        self.df['price'] = self.df['price'].astype(float)

