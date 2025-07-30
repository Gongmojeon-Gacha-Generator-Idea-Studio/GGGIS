from openai import OpenAI
import json
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

class OpenAIClient:
    def __init__(self, api_key: str = None):
        """
        OpenAI 클라이언트 초기화
        api_key가 None이면 환경변수 OPENAI_API_KEY에서 가져옴
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key가 필요합니다.")
        
        self.client = OpenAI(api_key=self.api_key)

    def generate_idea(self, contest_info: Dict[str, str], nodes_data: List[Dict[str, Any]]) -> Dict[str, str]:
        """
        공모전 정보와 노드 데이터를 기반으로 아이디어 생성
        """
        try:
            # 노드 요약
            nodes_summary = self._format_nodes_for_prompt(nodes_data)
            prompt = self._create_prompt(contest_info, nodes_summary)

            # OpenAI GPT 호출
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # 또는 "gpt-4", "gpt-3.5-turbo"
                messages=[
                    {"role": "system", "content": "당신은 창의적인 아이디어 생성 전문가입니다. 주어진 정보를 바탕으로 혁신적이고 실현 가능한 아이디어를 제안해주세요."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )

            generated_text = response.choices[0].message.content
            idea = self._parse_generated_idea(generated_text, contest_info)
            return idea

        except Exception as e:
            return {
                "error": f"아이디어 생성 중 오류: {str(e)}",
                "ai_name": "ChatGPT",
                "title": "오류",
                "overview": "아이디어 생성 실패",
                "problem": "",
                "solution": "",
                "implementation": "",
                "expected_effect": ""
            }

    def _format_nodes_for_prompt(self, nodes_data: List[Dict[str, Any]]) -> str:
        """노드 데이터를 문자열로 포맷팅"""
        if not nodes_data:
            return "기존 프로젝트 정보 없음."
        formatted = []
        for i, node in enumerate(nodes_data, 1):
            formatted.append(f"""
        프로젝트 {i}:
        - 제목: {node.get('title', '제목 없음')}
        - 솔루션: {node.get('solution', '솔루션 없음')}
        - 태그: {', '.join(node.get('tags', []))}
""")
        return "\n".join(formatted)

    def _create_prompt(self, contest_info: Dict[str, str], nodes_summary: str) -> str:
        """ChatGPT용 프롬프트 구성"""
        return f"""
                다음 공모전 정보와 기존 프로젝트 경험을 바탕으로 새로운 아이디어를 제안해주세요.

                【공모전 정보】
                - 공모전 제목: {contest_info.get('title', '')}
                - 주제: {contest_info.get('theme', '')}
                - 상세 설명: {contest_info.get('description', '')}
                - 맥락: {contest_info.get('context', '')}

                【기존 프로젝트 경험】
                {nodes_summary}

                아래 형식에 맞춰 응답해주세요:

                제목: [아이디어 제목]  
                개요: [간단한 소개]  
                문제의식: [해결하고자 하는 문제]  
                솔루션: [구체적인 해결 방안]  
                구현방안: [기술적 구현 또는 실행 계획]  
                기대효과: [예상 성과 또는 효과]
            """

    def _parse_generated_idea(self, generated_text: str, contest_info: Dict[str, str]) -> Dict[str, str]:
        """AI 생성 결과를 구조화된 형태로 파싱"""
        idea = {
            "ai_name": "ChatGPT",
            "title": "",
            "overview": "",
            "problem": "",
            "solution": "",
            "implementation": "",
            "expected_effect": "",
            "contest_info": contest_info,
            "raw_response": generated_text
        }

        try:
            lines = generated_text.split('\n')
            current_key = None
            for line in lines:
                line = line.strip()
                if line.startswith("제목:"):
                    current_key = "title"
                    idea[current_key] = line.replace("제목:", "").strip()
                elif line.startswith("개요:"):
                    current_key = "overview"
                    idea[current_key] = line.replace("개요:", "").strip()
                elif line.startswith("문제의식:"):
                    current_key = "problem"
                    idea[current_key] = line.replace("문제의식:", "").strip()
                elif line.startswith("솔루션:"):
                    current_key = "solution"
                    idea[current_key] = line.replace("솔루션:", "").strip()
                elif line.startswith("구현방안:"):
                    current_key = "implementation"
                    idea[current_key] = line.replace("구현방안:", "").strip()
                elif line.startswith("기대효과:"):
                    current_key = "expected_effect"
                    idea[current_key] = line.replace("기대효과:", "").strip()
                elif line and current_key:
                    idea[current_key] += " " + line
        except Exception as e:
            print(f"[파싱오류] {e}")
            idea["title"] = "파싱 실패"
            idea["overview"] = "결과 파싱에 실패했습니다."

        return idea


# 사용 예시
def create_openai_client(api_key: str = None) -> OpenAIClient:
    return OpenAIClient(api_key)