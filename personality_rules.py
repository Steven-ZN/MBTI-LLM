"""
人格-行为映射规则库
基于MBTI四维度的可观测写作行为规则
"""

from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class PersonalityProfile:
    """人格配置"""
    mbti: str  # 4字母MBTI类型
    e_score: float  # 外向性 [-1, 1]
    s_score: float  # 感觉性 [-1, 1] 
    t_score: float  # 思考性 [-1, 1]
    j_score: float  # 判断性 [-1, 1]
    valence: float  # 情绪愉悦度 [-1, 1]
    arousal: float  # 情绪唤醒度 [-1, 1]

class PersonalityRules:
    """人格行为规则映射器"""
    
    def __init__(self):
        self.rules = self._init_rules()
    
    def _init_rules(self) -> Dict[str, Dict]:
        """初始化规则库"""
        return {
            'sentence_patterns': {
                'E_high': {
                    'direct_calls': 0.8,  # 直接号召句比例
                    'second_person': 0.6,  # 第二人称使用率
                    'short_paragraphs': True,  # 段落简短
                    'exclamations': 0.3,  # 感叹号使用率
                    'hedging_words': 0.1,  # 限定词使用率
                },
                'I_high': {
                    'direct_calls': 0.2,
                    'second_person': 0.3,
                    'short_paragraphs': False,
                    'exclamations': 0.1,
                    'hedging_words': 0.4,  # 更多"可能"、"也许"
                },
                'N_high': {
                    'abstract_ratio': 0.7,  # 抽象概念比例
                    'metaphors': 0.5,  # 比喻使用率
                    'patterns': 0.6,  # 模式提炼
                    'cross_domain': 0.4,  # 跨域类比
                },
                'S_high': {
                    'abstract_ratio': 0.3,
                    'metaphors': 0.2,
                    'concrete_facts': 0.8,  # 具体事实
                    'numbers_lists': 0.6,  # 数字和清单
                },
                'T_high': {
                    'logical_structure': 0.9,  # 逻辑结构清晰
                    'premise_conclusion': 0.8,  # 前提-结论模式
                    'emotion_words': 0.2,  # 情绪词汇
                    'evidence_based': 0.8,  # 基于证据
                },
                'F_high': {
                    'logical_structure': 0.5,
                    'premise_conclusion': 0.4,
                    'emotion_words': 0.7,  # 更多情绪词汇
                    'empathy_phrases': 0.8,  # 共情语句
                    'value_oriented': 0.7,  # 价值导向
                },
                'J_high': {
                    'conclusion_first': 0.8,  # 结论先行
                    'structured_lists': 0.7,  # 条目化
                    'action_items': 0.6,  # 行动项
                    'definitive_language': 0.8,  # 确定性语言
                },
                'P_high': {
                    'conclusion_first': 0.3,
                    'structured_lists': 0.4,
                    'open_questions': 0.7,  # 开放式问题
                    'alternatives': 0.6,  # 备选方案
                    'exploratory_tone': 0.8,  # 探索性语调
                }
            },
            
            'vocabulary': {
                'hedging_words': [
                    '可能', '也许', '大概', '似乎', '倾向于', 
                    '通常来说', '在某种程度上', '相对而言'
                ],
                'direct_words': [
                    '必须', '应该', '肯定', '显然', '明确',
                    '立即', '直接', '马上', '决定性地'
                ],
                'empathy_phrases': [
                    '我理解你的感受', '这确实让人', '从你的角度来看',
                    '我能感受到', '这种感觉很自然', '你的担心是可以理解的'
                ],
                'logical_connectors': [
                    '因此', '由此可见', '基于这个前提', '逻辑上',
                    '根据分析', '数据表明', '事实证明', '研究显示'
                ],
                'abstract_concepts': [
                    '本质上', '从模式来看', '宏观而言', '系统性地',
                    '概念化', '框架', '范式', '整体思维'
                ],
                'concrete_markers': [
                    '具体来说', '举例而言', '第一步', '实际操作中',
                    '数据显示', '现实情况是', '实践证明'
                ]
            },
            
            'structure_patterns': {
                'ENTJ': {
                    'opening': '结论先行',
                    'body': '三点论证',
                    'closing': '行动建议',
                    'tone': '权威指导'
                },
                'INFP': {
                    'opening': '价值叙事',
                    'body': '情感共鸣',
                    'closing': '开放思考',
                    'tone': '温暖启发'
                },
                'ISTP': {
                    'opening': '问题拆解',
                    'body': '逐项分析',
                    'closing': '实用方案',
                    'tone': '务实客观'
                }
            }
        }
    
    def get_personality_weights(self, profile: PersonalityProfile) -> Dict[str, float]:
        """根据人格档案计算各维度权重"""
        weights = {}
        
        # E/I维度
        if profile.e_score > 0:
            weights.update(self.rules['sentence_patterns']['E_high'])
        else:
            weights.update(self.rules['sentence_patterns']['I_high'])
        
        # N/S维度
        if profile.s_score < 0:  # N倾向
            weights.update(self.rules['sentence_patterns']['N_high'])
        else:  # S倾向
            weights.update(self.rules['sentence_patterns']['S_high'])
        
        # T/F维度
        if profile.t_score > 0:
            weights.update(self.rules['sentence_patterns']['T_high'])
        else:
            weights.update(self.rules['sentence_patterns']['F_high'])
        
        # J/P维度
        if profile.j_score > 0:
            weights.update(self.rules['sentence_patterns']['J_high'])
        else:
            weights.update(self.rules['sentence_patterns']['P_high'])
        
        return weights
    
    def get_vocab_preferences(self, profile: PersonalityProfile) -> Dict[str, List[str]]:
        """获取词汇偏好"""
        vocab = {}
        
        if abs(profile.e_score) > 0.5:
            if profile.e_score > 0:
                vocab['preferred'] = self.rules['vocabulary']['direct_words']
                vocab['avoid'] = self.rules['vocabulary']['hedging_words']
            else:
                vocab['preferred'] = self.rules['vocabulary']['hedging_words']
                vocab['avoid'] = self.rules['vocabulary']['direct_words']
        
        if profile.t_score < 0:  # F倾向
            vocab['empathy'] = self.rules['vocabulary']['empathy_phrases']
        
        if profile.t_score > 0:  # T倾向
            vocab['logical'] = self.rules['vocabulary']['logical_connectors']
        
        if profile.s_score < 0:  # N倾向
            vocab['abstract'] = self.rules['vocabulary']['abstract_concepts']
        else:  # S倾向
            vocab['concrete'] = self.rules['vocabulary']['concrete_markers']
        
        return vocab
    
    def get_structure_template(self, mbti: str) -> Dict[str, str]:
        """获取结构模板"""
        return self.rules['structure_patterns'].get(mbti, {
            'opening': '直接回应',
            'body': '分点说明',
            'closing': '总结',
            'tone': '中性客观'
        })

# 预定义人格档案
PREDEFINED_PERSONAS = {
    'ENTJ': PersonalityProfile(
        mbti='ENTJ',
        e_score=0.8, s_score=0.2, t_score=0.9, j_score=0.9,
        valence=0.2, arousal=0.7
    ),
    'INFP': PersonalityProfile(
        mbti='INFP',
        e_score=-0.7, s_score=-0.6, t_score=-0.8, j_score=-0.5,
        valence=0.3, arousal=0.3
    ),
    'ISTP': PersonalityProfile(
        mbti='ISTP',
        e_score=-0.5, s_score=0.8, t_score=0.7, j_score=-0.4,
        valence=0.0, arousal=0.2
    )
}