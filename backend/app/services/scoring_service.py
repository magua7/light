class ScoringService:
    score_weights = {
        "image": 0.7,
        "satellite": 0.2,
        "ecology": 0.1,
    }

    def calculate_scores(self, ai_result: dict, satellite_info: dict, ecology_info: dict) -> dict:
        summary = ai_result.get("summary", {})
        image_scores = [item["score"] for item in ai_result.get("images", [])]
        legacy_image_score = round(sum(image_scores) / len(image_scores), 2) if image_scores else 0
        image_score = round(
            float(
                summary.get("model_total_score")
                or summary.get("image_avg_score")
                or legacy_image_score
            ),
            2,
        )
        satellite_score = round(float(satellite_info.get("satellite_score", 0)), 2)
        ecology_score = round(float(ecology_info.get("ecology_score", 0)), 2)

        model_final_score = summary.get("final_score")
        model_grade = summary.get("grade")

        if model_final_score is not None and model_grade:
            total_score = round(float(model_final_score), 2)
            level = str(model_grade)
        else:
            total_score = round(
                image_score * self.score_weights["image"]
                + satellite_score * self.score_weights["satellite"]
                + ecology_score * self.score_weights["ecology"],
                2,
            )
            level = self.get_level(total_score)

        blue_risk = bool(summary.get("blue_risk", False))
        type_count = summary.get("type_count", {})
        suggestions = summary.get("suggestions") or self.build_suggestions(level, type_count, blue_risk, ecology_info)
        warning_level = self.get_warning_level(total_score, blue_risk)

        return {
            "image_score": image_score,
            "satellite_score": satellite_score,
            "ecology_score": ecology_score,
            "total_score": total_score,
            "level": level,
            "blue_risk": blue_risk,
            "suggestions": suggestions,
            "warning_level": warning_level,
        }

    def get_level(self, score: float) -> str:
        if score <= 20:
            return "优"
        if score <= 40:
            return "良"
        if score <= 60:
            return "中"
        if score <= 80:
            return "较差"
        return "差"

    def get_warning_level(self, score: float, blue_risk: bool) -> str | None:
        if score >= 80:
            return "高风险"
        if score >= 60 or blue_risk:
            return "中高风险"
        return None

    def build_suggestions(
        self,
        level: str,
        type_count: dict,
        blue_risk: bool,
        ecology_info: dict,
    ) -> list[str]:
        suggestions: list[str] = []

        if type_count.get("ad_light", 0) >= 2:
            suggestions.append("建议对广告牌光源进行分时调光，降低夜间高亮连续投射。")
        if type_count.get("up_light", 0) >= 1:
            suggestions.append("建议调整上射灯角度并增加遮光罩，减少直射天空的逸散光。")
        if type_count.get("move_light", 0) >= 2:
            suggestions.append("建议规范动态灯带和滚动屏播放时段，避免高频闪烁刺激。")
        if type_count.get("stay_light", 0) >= 3:
            suggestions.append("建议对静态景观灯实施分区控制，优先关闭低价值照明。")
        if blue_risk:
            suggestions.append("存在蓝光风险，建议更换为低色温光源并控制高色温 LED 的使用比例。")
        if ecology_info.get("vulnerability_level") == "高":
            suggestions.append("监测点邻近生态敏感区域，建议纳入重点时段照明管控范围。")
        if level in {"较差", "差"}:
            suggestions.append("综合评级偏高，建议由属地管理部门安排复核并制定专项治理方案。")

        if not suggestions:
            suggestions.append("当前光环境整体可控，建议持续监测并保持照明设备维护。")

        return suggestions[:5]
