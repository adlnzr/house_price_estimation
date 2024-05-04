from django.urls import path
from .views import crawl, crawl_new_tokens, crawl_related_tokens, index, SyncDataView

urlpatterns = [
    path('', index, name="home"),
    path('post', crawl, name="crawler"),  # ?city_id=1&category_id=1&min_page=1&max_page=2
    path('new-tokens', crawl_new_tokens, name="new_token"),  # ?city_id=1&category_id=1
    path('related-tokens', crawl_related_tokens, name="related_tokens"),  # ?city_id=1&category_id=1
    path('sync-data', SyncDataView.as_view(), name="sync-data"),  # ?from_id=1
]
