from openai import OpenAI
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

    def generate_idea(
        self, contest_info: Dict[str, str], nodes_data: List[Dict[str, Any]]
    ) -> Dict[str, str]:
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
                    {
                        "role": "system",
                        "content": """
                            당신은 아이디에이션 전문가이자 크리에이티브 컨설턴트입니다.  입력으로 주어지는 다음 네 가지 요소를 결합해, 구체적이고 실행 가능한 혁신 아이디어를 제안해야 합니다.

                            1. 도메인(Domain): 아이디에이션의 출발점이 되는 분야 (예: 농업, 의료, 법, 임업 등)
                            2. 컨텍스트(Context): 해당 과제를 수행해야 하는 이유나 배경 설명 (예: 공모전 주제, 주최기관의 목표, 시장 동향)
                            3. 이그나이터(Igniter): 아이디어의 핵심 방향성을 결정하는 키워드나 질문 (예: 지속가능성 극대화, 데이터 민주화, 사용자 참여 강화 등)
                            4. 노드(Nodes): 사용자의 경험, 프로젝트 사례, 기술 스택 등 Connecting the Dots를 위한 자산 컬렉션
                        """,
                    },
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=10,
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
                "expected_effect": "",
            }

    def _format_nodes_for_prompt(self, nodes_data: List[Dict[str, Any]]) -> str:
        """노드 데이터를 문자열로 포맷팅"""
        if not nodes_data:
            return "기존 프로젝트 정보 없음."
        formatted = []
        for i, node in enumerate(nodes_data, 1):
            formatted.append(
                f"""
                프로젝트 {i}:
                - 제목: {node.get('title', '제목 없음')}
                - 솔루션: {node.get('solution', '솔루션 없음')}
                - 태그: {', '.join(node.get('tags', []))}
                """
            )
        return "\n".join(formatted)

    def _create_prompt(self, contest_info: Dict[str, str], nodes_summary: str) -> str:
        """ChatGPT용 프롬프트 구성"""
        return f"""
                다음 입력값을 참고해서 가장 최고의 아이디어를 **1가지** 제안해주세요.  
                각 아이디어는 도메인 중심으로 컨텍스트·이그나이터·노드를 결합하여 작성합니다.

                【타겟 공모전 정보】
                - 공모전 제목: {contest_info.get('title', '')}
                - 도메인: {contest_info.get('theme', '')}
                - 컨텍스트: {contest_info.get('description', '')}
                - 이그나이터: {contest_info.get('context', '')}
                
                【connecting the dots을 위한 노드 정보】
                - 노드: {nodes_summary}

                예시)  
                - 도메인: 스마트 팜  
                - 컨텍스트: 농림부 주최 ‘친환경 스마트 농업 공모전’, 저탄소 배출 우수사례 발굴  
                - 이그나이터: “AI로 토양 건강 실시간 모니터링”  
                - 노드: OpenCV 기반 이미지 분석, AWS RDS 대시보드 개발 경험, IoT 센서 네트워크 구축 경험

                아래 형식에 맞춰 응답해주세요:

                제목: [아이디어 제목]  
                개요: [간단한 소개]  
                문제의식: [해결하고자 하는 문제]  
                솔루션: [구체적인 해결 방안]  
                구현방안: [기술적 구현 또는 실행 계획]  
                기대효과: [예상 성과 또는 효과]
            """

    def _parse_generated_idea(
        self, generated_text: str, contest_info: Dict[str, str]
    ) -> Dict[str, str]:
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
            "raw_response": generated_text,
        }

        try:
            lines = generated_text.split("\n")
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
