"""
风格评分器 - 基于规则的简易版本
用于评估文本与目标人格的匹配度
"""

import re
import jieba
from typing import Dict, List, Tuple
from collections import Counter
from personality_rules import PersonalityProfile, PersonalityRules

class StyleScorer:
    """风格评分器"""
    
    def __init__(self):
        self.rules = PersonalityRules()
        
    def score_text(self, text: str, target_profile: PersonalityProfile) -> float:
        """
        对文本进行人格匹配度评分
        返回值范围: [0, 1]，越高越匹配
        """
        if not text.strip():
            return 0.0
        
        # 获取目标人格的权重和偏好
        weights = self.rules.get_personality_weights(target_profile)
        vocab_prefs = self.rules.get_vocab_preferences(target_profile)
        
        # 计算各项指标得分
        scores = {
            'sentence_structure': self._score_sentence_structure(text, weights),
            'vocabulary_match': self._score_vocabulary(text, vocab_prefs),
            'tone_consistency': self._score_tone(text, target_profile),
            'length_style': self._score_length_style(text, target_profile),
            'punctuation_style': self._score_punctuation(text, target_profile)
        }
        
        # 加权平均
        final_score = (
            scores['sentence_structure'] * 0.3 +
            scores['vocabulary_match'] * 0.25 +
            scores['tone_consistency'] * 0.2 +
            scores['length_style'] * 0.15 +
            scores['punctuation_style'] * 0.1
        )
        
        return min(1.0, max(0.0, final_score))
    
    def _score_sentence_structure(self, text: str, weights: Dict[str, float]) -> float:
        """评估句子结构风格"""
        sentences = re.split(r'[。！？]', text)
        if not sentences:
            return 0.5
        
        score = 0.0
        
        # 分析句子长度
        avg_length = sum(len(s.strip()) for s in sentences if s.strip()) / len([s for s in sentences if s.strip()])
        
        # 短句风格 (E倾向)
        if weights.get('short_paragraphs', False):
            score += 0.8 if avg_length < 20 else 0.2
        else:
            score += 0.8 if avg_length > 25 else 0.2
        
        # 直接号召句检测
        direct_calls = len([s for s in sentences if self._is_direct_call(s)])
        direct_ratio = direct_calls / len(sentences) if sentences else 0
        target_ratio = weights.get('direct_calls', 0.5)
        score += 1 - abs(direct_ratio - target_ratio)
        
        return score / 2
    
    def _is_direct_call(self, sentence: str) -> bool:
        """检测是否为直接号召句"""
        direct_patterns = [
            r'应该', r'必须', r'建议.*?', r'推荐.*?', 
            r'你.*?', r'我们.*?', r'让我们'
        ]
        return any(re.search(pattern, sentence) for pattern in direct_patterns)
    
    def _score_vocabulary(self, text: str, vocab_prefs: Dict[str, List[str]]) -> float:
        """评估词汇选择"""
        words = list(jieba.cut(text))
        word_set = set(words)
        
        score = 0.5  # 基础分
        
        # 偏好词汇匹配
        if 'preferred' in vocab_prefs:
            preferred_count = sum(1 for word in vocab_prefs['preferred'] if word in word_set)
            score += 0.3 * min(1.0, preferred_count / max(1, len(vocab_prefs['preferred'])))
        
        # 避免词汇惩罚
        if 'avoid' in vocab_prefs:
            avoid_count = sum(1 for word in vocab_prefs['avoid'] if word in word_set)
            score -= 0.2 * min(1.0, avoid_count / max(1, len(vocab_prefs['avoid'])))
        
        # 特殊词汇加分
        for category in ['empathy', 'logical', 'abstract', 'concrete']:
            if category in vocab_prefs:
                category_count = sum(1 for word in vocab_prefs[category] if word in word_set)
                score += 0.1 * min(1.0, category_count / max(1, len(vocab_prefs[category])))
        
        return min(1.0, max(0.0, score))
    
    def _score_tone(self, text: str, profile: PersonalityProfile) -> float:
        """评估语调一致性"""
        score = 0.5
        
        # 感叹号使用（E倾向）
        exclamation_count = text.count('！') + text.count('!')
        text_length = len(text)
        exclamation_ratio = exclamation_count / max(1, text_length / 100)
        
        if profile.e_score > 0:  # 外向
            score += 0.3 if exclamation_ratio > 0.5 else -0.1
        else:  # 内向
            score += 0.3 if exclamation_ratio < 0.3 else -0.1
        
        # 限定词使用（I倾向）
        hedging_words = ['可能', '也许', '大概', '似乎', '倾向于']
        hedging_count = sum(text.count(word) for word in hedging_words)
        
        if profile.e_score < 0:  # 内向
            score += 0.3 if hedging_count > 0 else -0.1
        else:  # 外向
            score += 0.3 if hedging_count == 0 else -0.1
        
        return min(1.0, max(0.0, score))
    
    def _score_length_style(self, text: str, profile: PersonalityProfile) -> float:
        """评估长度风格"""
        char_count = len(text.strip())
        
        # 根据人格类型的偏好长度
        if profile.mbti == 'ENTJ':
            # ENTJ倾向中等长度，结构化
            ideal_range = (100, 300)
        elif profile.mbti == 'INFP':
            # INFP倾向较长，深入
            ideal_range = (150, 400)
        elif profile.mbti == 'ISTP':
            # ISTP倾向简洁实用
            ideal_range = (80, 200)
        else:
            ideal_range = (100, 250)
        
        if ideal_range[0] <= char_count <= ideal_range[1]:
            return 1.0
        elif char_count < ideal_range[0]:
            return max(0.3, char_count / ideal_range[0])
        else:
            return max(0.3, ideal_range[1] / char_count)
    
    def _score_punctuation(self, text: str, profile: PersonalityProfile) -> float:
        """评估标点符号风格"""
        score = 0.5
        
        # 问号使用（P倾向）
        question_count = text.count('？') + text.count('?')
        if profile.j_score < 0:  # P倾向
            score += 0.5 if question_count > 0 else 0.1
        else:  # J倾向
            score += 0.3 if question_count == 0 else 0.1
        
        # 顿号和分号使用（结构化倾向）
        struct_punct = text.count('；') + text.count('、') + text.count(':') + text.count('：')
        if profile.j_score > 0:  # J倾向
            score += 0.5 if struct_punct > 0 else 0.1
        
        return min(1.0, max(0.0, score))
    
    def get_detailed_analysis(self, text: str, target_profile: PersonalityProfile) -> Dict[str, any]:
        """获取详细分析报告"""
        weights = self.rules.get_personality_weights(target_profile)
        vocab_prefs = self.rules.get_vocab_preferences(target_profile)
        
        return {
            'overall_score': self.score_text(text, target_profile),
            'breakdown': {
                'sentence_structure': self._score_sentence_structure(text, weights),
                'vocabulary_match': self._score_vocabulary(text, vocab_prefs),
                'tone_consistency': self._score_tone(text, target_profile),
                'length_style': self._score_length_style(text, target_profile),
                'punctuation_style': self._score_punctuation(text, target_profile)
            },
            'text_stats': {
                'char_count': len(text),
                'sentence_count': len(re.split(r'[。！？]', text)),
                'exclamation_count': text.count('！') + text.count('!'),
                'question_count': text.count('？') + text.count('?')
            }
        }