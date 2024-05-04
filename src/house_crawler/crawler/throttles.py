from rest_framework.throttling import UserRateThrottle


class SyncDataRateThrottle(UserRateThrottle):
    scope = 'sync_data'
