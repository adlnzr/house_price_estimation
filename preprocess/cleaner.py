import os
from math import radians, sin, cos, sqrt, asin

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sklearn
from geopy import Nominatim

import utils


class Cleaner:
    def __init__(self, df: pd.DataFrame = None, min_dist=1):
        self.raw_df = df
        self.df = self.raw_df.copy()
        self.min_dist = min_dist
        self.csv_district_file_path = '../data/districts_location.csv'

        self.cols_number = ['meter', 'rooms', 'year', ]
        self.cols_bool = ['balcony', 'elevator', 'depot', 'parking']
        self.cols_need_to_fill = ['real_state_agency', 'floor']
        # self.cols_drop = [
        #     'city_rel', 'top_description_text', 'middle_description_text', 'bottom_description_text', 'red_text',
        #     'checkable', 'label', 'label_color', 'is_checked', 'has_chat', 'last_post_date', 'first_post_date',
        #     'brand_model', 'image_url', 'web_url', 'business_ref', 'chat_enabled', 'cat_1', 'cat_2', 'cat_3',
        #     'gender', 'originality', 'status', 'not_elevator', 'not_parking', 'not_depot', 'map_type', 'id',
        #     'is_active', 'radius', 'map_image_url', 'not_balcony', 'check_cost_limit', 'check_cost', 'pricing_cost',
        #     'land_meter', 'house_status', 'created_at', 'token', 'token_code', 'city_name', 'city_persian', 'credit',
        #     'image_count', 'category_slug_persian', 'rent','unavailable_after','suggestion_tokens','title','district_persian'
        # ]
        self.cols_drop = [
            'city_rel', 'top_description_text', 'middle_description_text', 'bottom_description_text', 'red_text',
            'checkable', 'label', 'label_color', 'is_checked', 'has_chat', 'last_post_date', 'first_post_date',
            'brand_model', 'gender', 'originality', 'status', 'not_elevator', 'not_parking', 'not_depot', 'map_type',
            'latitude', 'balcony', 'total_price', 'created_at', 'real_state_agency',
            'longitude', 'radius', 'map_image_url', 'not_balcony', 'check_cost_limit', 'check_cost', 'pricing_cost',
            'land_meter', 'house_status', 'category_slug_persian', 'title', 'token_code', 'web_url', 'rent',
            'price_per_meter', 'image_count', 'id', 'token', 'city_name', 'description', 'credit',
            'suggestion_tokens', 'unavailable_after', 'is_active', 'district_persian', 'chat_enabled',
            'city_persian', 'business_ref', 'cat_1', 'cat_2', 'cat_3', 'image_url', 'city', 'category',
        ]
        self.cols_change_to_digits = self.cols_number
        self.drop_na_cols = ['meter', 'floor', 'price']
        self.route = {
            'func_number': self.cols_number, 'func_bool': self.cols_bool, 'func_cols_drop': self.cols_drop,
            'func_need_cat_fill': self.cols_need_to_fill, 'func_floor': ['floor'],
            'func_drop_na_cols': self.drop_na_cols, 'func_ultimate_drop': ['floor']
        }
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
            # 'func_price',
            'func_ultimate_drop',
            'func_near_metro']

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

    def func_change_to_int(self):
        func_name = 'func_change_to_int'
        for field in self.route[func_name]:
            df_field = self.df[field]
            df_field = df_field.map(lambda x: int(x) if x.isdigit() else x)
            self.df[field] = df_field

    def func_bool(self):
        func_name = 'func_bool'

    def func_need_cat_fill(self):
        func_name = 'func_need_cat_fill'
        for field in self.route[func_name]:
            # if field == 'real_state_agency':
            #     self.df[field] = self.df[field].fillna('personal')
            if field == 'floor':
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

    def func_price(self):
        func_name = 'func_price'
        for field in self.route[func_name]:
            df_field = self.df[field]
            df_field = df_field.str.split().apply(lambda x: x[0].replace("٬", ""))
            df_field = df_field.apply(lambda x: int(x) if x != 'توافقی' else x)
            condition = df_field.loc[(df_field != 'توافقی') & (df_field != 11111111111) & (df_field != 1111111111)]

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

    def func_near_metro(self):
        func_name = 'func_near_metro'
        coord = self.get_location_coordinates(loc_series=self.df['district'])
        metro_df = pd.read_csv('../data/metro.csv')
        if_near_df = self._near_metro(coordinates_df=coord, metro_df=metro_df, min_dist=self.min_dist)
        if_near_df.loc_name = if_near_df.loc_name.str.replace(' tehran', '')

        self.df = pd.merge(self.df, if_near_df[['loc_name', 'if_near']], left_on='district',
                           right_on='loc_name', how='left')

    def get_location_coordinates(self, loc_series, language='en'):
        unique_district = loc_series.astype(str)
        unique_district = unique_district.unique().tolist()
        loc_teh = [s + ' tehran' for s in unique_district]

        districts_location = pd.read_csv(self.csv_district_file_path) if os.path.exists(
            self.csv_district_file_path) else None
        if districts_location is None:
            diff_loc = loc_teh
        else:
            print('HERE222222')
            diff_loc = set(districts_location.loc_name) - set(loc_teh)

        loc_name_csv = []
        loc = []
        lats = []
        longs = []
        geolocator = Nominatim(user_agent="your_app_name")
        for item in diff_loc:
            print('item', item)
            location = geolocator.geocode(item)
            if location:
                loc_name_csv.append(item)
                loc.append(item.removesuffix(' tehran'))
                lats.append(location.latitude)
                longs.append(location.longitude)
        if loc_name_csv:
            print(loc_name_csv)
            coordinates_df = pd.DataFrame({'loc_name': loc, 'lat': lats, 'long': longs})
            pd.DataFrame({'loc_name': loc_name_csv, 'lats': lats, 'longs': longs}).to_csv(
                self.csv_district_file_path, index=False)
            print('Here 3')

            return coordinates_df
        else:
            print('Here 4')
            return districts_location  # pd.read_csv(self.csv_district_file_path)

    def _distance(self, lat1, lon1, lat2, lon2):
        lon1 = radians(lon1)
        lon2 = radians(lon2)
        lat1 = radians(lat1)
        lat2 = radians(lat2)
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371
        dist_km = c * r
        return (dist_km)

    def _near_metro(self, coordinates_df, metro_df, min_dist):
        region_len = len(coordinates_df)
        metro_len = len(metro_df)
        region = []
        near_dist = []
        for i in range(region_len):
            for j in range(metro_len):
                dist = self._distance(coordinates_df.iloc[i, 2], coordinates_df.iloc[i, 3], metro_df.iloc[j, 1],
                                      metro_df.iloc[j, 2])
                if dist <= min_dist:
                    region.append(coordinates_df.iloc[i, 0])
                    near_dist.append(dist)
                    break
        if_near = pd.DataFrame({'region': region})
        coordinates_df['if_near'] = coordinates_df.iloc[:, 0].isin(if_near['region']).astype(int)
        return coordinates_df


if __name__ == '__main__':
    raw_df = pd.read_csv('../data/Post-2023-11-13.csv')  # ../data/Post-2023-11-13.csv')
    df = Cleaner(raw_df).transform()
    print(df.info())
