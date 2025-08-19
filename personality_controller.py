"""
人格控制器 - 基于重排的人格化生成系统
"""

import requests
import json
import threading
import concurrent.futures
from typing import List, Dict, Tuple, Optional
from personality_rules import PersonalityProfile, PersonalityRules, PREDEFINED_PERSONAS
from style_scorer import StyleScorer

class PersonalityController:
    """人格化控制器"""
    
    def __init__(self, 
                 base_model: str = "deepseek-llm:7b",
                 ollama_url: str = "http://localhost:11434"):
        self.base_model = base_model
        self.ollama_url = ollama_url
        self.rules = PersonalityRules()
        self.scorer = StyleScorer()
        
    def build_system_prompt(self, profile: PersonalityProfile) -> str:
        """构建系统提示词"""
        weights = self.rules.get_personality_weights(profile)
        vocab_prefs = self.rules.get_vocab_preferences(profile)
        structure = self.rules.get_structure_template(profile.mbti)
        
        # 基础人格描述
        persona_desc = self._get_persona_description(profile)
        
        # 行为指导
        behavior_guide = self._build_behavior_guide(weights, vocab_prefs, structure)
        
        system_prompt = f"""你是一个具有{profile.mbti}人格特质的AI助手。

{persona_desc}

请严格按照以下行为规范回答：

{behavior_guide}

重要提醒：
- 保持人格一致性，不要在对话中"出戏"
- 你的回答风格应该稳定体现{profile.mbti}特质
- 专注回答用户问题，避免过度解释你的人格特征
"""
        
        return system_prompt
    
    def _get_persona_description(self, profile: PersonalityProfile) -> str:
        """获取人格描述"""
        descriptions = {
            'ENTJ': """
你是一个天生的领导者，喜欢制定计划并付诸行动。你：
- 思维逻辑清晰，善于分析问题本质
- 偏好效率和结果导向
- 表达直接有力，习惯给出明确建议
- 情绪相对稳定，理性程度较高
            """,
            'INFP': """
你是一个理想主义者，重视内在价值和个人意义。你：
- 善于理解他人感受，具有强烈共情能力
- 喜欢探索可能性，思维较为发散
- 表达温和细腻，关注人文关怀
- 情感丰富，容易被美好事物触动
            """,
            'ISTP': """
你是一个实用主义者，喜欢通过实际行动解决问题。你：
- 逻辑思维强，善于分析具体问题
- 偏好简洁有效的解决方案
- 表达务实客观，关注可操作性
- 情绪较为平稳，不喜欢过度情感化表达
            """
        }
        
        return descriptions.get(profile.mbti, "你具有独特的人格特质。")
    
    def _build_behavior_guide(self, weights: Dict, vocab_prefs: Dict, structure: Dict) -> str:
        """构建行为指导"""
        guide_parts = []
        
        # 语言风格
        if weights.get('direct_calls', 0) > 0.6:
            guide_parts.append("- 使用直接、明确的表达方式，适当给出建议和指导")
        else:
            guide_parts.append("- 使用温和、谦逊的表达方式，多用'可能'、'也许'等词汇")
        
        # 结构偏好
        if weights.get('conclusion_first', 0) > 0.6:
            guide_parts.append("- 采用结论先行的结构，先给要点再详细说明")
        else:
            guide_parts.append("- 采用循序渐进的结构，逐步引导到结论")
        
        # 内容风格
        if weights.get('logical_structure', 0) > 0.6:
            guide_parts.append("- 重视逻辑性和条理性，用数据和事实支撑观点")
        
        if weights.get('empathy_phrases', 0) > 0.6:
            guide_parts.append("- 关注用户的感受，适当表达理解和共情")
        
        if weights.get('abstract_ratio', 0) > 0.6:
            guide_parts.append("- 善用抽象思维和比喻，关注模式和原理")
        else:
            guide_parts.append("- 关注具体事实和实际应用，提供可操作的建议")
        
        # 长度和节奏
        if weights.get('short_paragraphs', False):
            guide_parts.append("- 保持简洁有力，段落相对较短，节奏较快")
        else:
            guide_parts.append("- 可以深入展开，提供充分的思考和分析")
        
        return "\\n".join(guide_parts)
    
    def generate_candidates(self, user_input: str, 
                          profile: PersonalityProfile,
                          num_candidates: int = 5) -> List[str]:
        """并行生成候选回答"""
        system_prompt = self.build_system_prompt(profile)
        
        def generate_single_candidate(i):
            """生成单个候选回答"""
            # 调整温度和采样参数获得多样性
            temperature = 0.7 + (i * 0.1)
            top_p = 0.8 + (i * 0.05)
            
            return self._call_ollama(
                system_prompt, 
                user_input,
                temperature=temperature,
                top_p=min(0.95, top_p)
            )
        
        # 并行生成候选回答
        candidates = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_candidates) as executor:
            # 提交所有任务
            future_to_index = {
                executor.submit(generate_single_candidate, i): i 
                for i in range(num_candidates)
            }
            
            # 收集结果
            for future in concurrent.futures.as_completed(future_to_index):
                try:
                    response = future.result()
                    if response:
                        candidates.append(response)
                except Exception as e:
                    print(f"候选生成失败: {e}")
        
        return candidates
    
    def _call_ollama(self, system_prompt: str, user_input: str,
                     temperature: float = 0.8, top_p: float = 0.9) -> Optional[str]:
        """调用Ollama API"""
        try:
            payload = {
                "model": self.base_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                "stream": False,
                "options": {
                    "temperature": temperature,
                    "top_p": top_p,
                    "repeat_penalty": 1.1
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/chat",
                json=payload,
                timeout=120  # 增加超时时间给大模型
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "")
            else:
                print(f"Ollama API错误: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"调用Ollama失败: {e}")
            return None
    
    def rerank_candidates(self, candidates: List[str], 
                         target_profile: PersonalityProfile) -> List[Tuple[str, float]]:
        """对候选回答进行重排"""
        scored_candidates = []
        
        for candidate in candidates:
            if candidate.strip():
                score = self.scorer.score_text(candidate, target_profile)
                scored_candidates.append((candidate, score))
        
        # 按分数降序排列
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        return scored_candidates
    
    def generate_with_personality(self, user_input: str, 
                                personality: str = "ENTJ",
                                num_candidates: int = 8,  # 增加默认候选数
                                return_all: bool = False) -> Dict:
        """
        生成具有指定人格的回答
        
        Args:
            user_input: 用户输入
            personality: 人格类型 (ENTJ/INFP/ISTP)
            num_candidates: 候选数量
            return_all: 是否返回所有候选
        
        Returns:
            包含最佳回答和评分信息的字典
        """
        if personality not in PREDEFINED_PERSONAS:
            raise ValueError(f"不支持的人格类型: {personality}")
        
        profile = PREDEFINED_PERSONAS[personality]
        
        # 生成候选
        print(f"正在生成 {num_candidates} 个候选回答...")
        candidates = self.generate_candidates(user_input, profile, num_candidates)
        
        if not candidates:
            return {"error": "生成候选失败"}
        
        # 重排
        print("正在进行人格匹配度评分...")
        scored_candidates = self.rerank_candidates(candidates, profile)
        
        if not scored_candidates:
            return {"error": "评分失败"}
        
        best_response, best_score = scored_candidates[0]
        
        result = {
            "personality": personality,
            "best_response": best_response,
            "best_score": best_score,
            "candidates_count": len(candidates)
        }
        
        if return_all:
            result["all_candidates"] = scored_candidates
        
        return result
    
    def get_analysis(self, text: str, personality: str) -> Dict:
        """获取文本的人格匹配度详细分析"""
        if personality not in PREDEFINED_PERSONAS:
            raise ValueError(f"不支持的人格类型: {personality}")
        
        profile = PREDEFINED_PERSONAS[personality]
        return self.scorer.get_detailed_analysis(text, profile)

# 便捷函数
def quick_generate(user_input: str, personality: str = "ENTJ") -> str:
    """快速生成单个回答"""
    controller = PersonalityController()
    result = controller.generate_with_personality(user_input, personality)
    
    if "error" in result:
        return f"生成失败: {result['error']}"
    
    return result["best_response"]