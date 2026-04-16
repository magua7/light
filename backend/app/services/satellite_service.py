import math


class SatelliteService:
    """
    卫星夜光评估服务。
    当前使用本地规则兜底，可在后续接入真实遥感平台或 API。
    """

    def get_satellite_info(self, longitude: float, latitude: float) -> dict:
        brightness_value = round(abs(math.sin(longitude) * 45 + math.cos(latitude) * 35) + 20, 2)
        satellite_score = min(round(brightness_value, 2), 100)

        if satellite_score >= 80:
            brightness_level = "极亮"
        elif satellite_score >= 60:
            brightness_level = "偏亮"
        elif satellite_score >= 40:
            brightness_level = "中等"
        else:
            brightness_level = "较暗"

        return {
            "brightness_value": brightness_value,
            "satellite_score": satellite_score,
            "brightness_level": brightness_level,
            "source": "local_satellite_service",
        }
