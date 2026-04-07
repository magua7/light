import math


class GeoService:
    """
    地理信息服务 mock 层。
    后续可替换为真实 GIS 或逆地理编码接口。
    """

    region_names = [
        "中心城区",
        "商业密集区",
        "居住混合区",
        "滨江景观带",
        "高校片区",
        "工业过渡区",
    ]

    def resolve_location(self, longitude: float, latitude: float, location_name: str | None = None) -> dict:
        index = int(abs(math.floor(longitude * latitude * 1000))) % len(self.region_names)
        region_name = self.region_names[index]
        display_name = location_name or f"{region_name}监测点"

        return {
            "region_name": region_name,
            "display_name": display_name,
            "province": "示例省",
            "city": "示例市",
            "coordinates": {
                "longitude": longitude,
                "latitude": latitude,
            },
        }
