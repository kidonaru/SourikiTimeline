from typing import List
from scripts.common_utils import format_short_chara_name, convert_ocr_string
from scripts.common_utils import calculate_similarity

class CharaSkill:
    file_path = 'resources/skill.tsv'

    chara_name: str
    skill_name: str
    skill_detail: str

    ocr_skill_name: str

    def __init__(self, chara_name, skill_name, skill_detail):
        self.chara_name = chara_name
        self.skill_name = skill_name
        self.skill_detail = skill_detail
        self.ocr_skill_name = convert_ocr_string(skill_name)

    @classmethod
    def from_tsv(cls):
        chara_skills: list[cls] = []
        with open(CharaSkill.file_path, 'r', encoding='utf-8') as file:
            header = next(file).strip().split('\t')
            for line in file:
                parts = line.strip().split('\t')
                if len(parts) >= 3:
                    chara_name = parts[header.index('キャラ')]
                    skill_name = parts[header.index('EXスキル名')]
                    skill_detail = parts[header.index('EXスキル詳細')]
                    chara_skills.append(cls(chara_name, skill_name, skill_detail))
        return chara_skills
    
    @classmethod
    def find_best_match(cls, chara_skills: List['CharaSkill'], query_skill: str, threshold: int = 50):
        if query_skill == '':
            return None, 0

        best_match = None
        highest_similarity = 0
        query_skill = convert_ocr_string(query_skill)

        for chara_skill in chara_skills:
            similarity = calculate_similarity(chara_skill.ocr_skill_name, query_skill)
            if similarity > highest_similarity and similarity >= threshold:
                highest_similarity = similarity
                best_match = chara_skill

        return best_match, highest_similarity

    def get_short_chara_name(self):
        return format_short_chara_name(self.chara_name)

    def __repr__(self):
        return f"CharaSkill(chara_name='{self.chara_name}', skill_name='{self.skill_name}', skill_detail='{self.skill_detail}')"
