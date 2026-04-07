import math


class EcologyService:
    """
    生态脆弱度服务 mock 层。
    后续可替换为真实生态敏感区、土地利用、保护区等接口。
    """

    land_use_types = ["商业用地", "居住用地", "滨水景观", "科教园区", "交通枢纽", "工业用地"]

    def get_ecology_info(self, longitude: float, latitude: float) -> dict:
        selector = int(abs(math.floor((longitude + latitude) * 100))) % len(self.land_use_types)
        ecology_score = round(25 + abs(math.sin(latitude * 2)) * 45, 2)
        land_use_type = self.land_use_types[selector]

        if ecology_score >= 70:
            vulnerability_level = "高"
        elif ecology_score >= 45:
            vulnerability_level = "中"
        else:
            vulnerability_level = "低"

        return {
            "land_use_type": land_use_type,
            "ecology_score": ecology_score,
            "vulnerability_level": vulnerability_level,
            "near_sensitive_area": vulnerability_level in {"高", "中"},
        }
