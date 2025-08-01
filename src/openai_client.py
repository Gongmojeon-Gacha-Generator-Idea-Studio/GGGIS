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
                model="gpt-4o",  # 또는 "gpt-4", "gpt-3.5-turbo"
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
                max_tokens=5000,
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
                "rationale": "",
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
                - 설명: {node.get('description', '설명 없음')}
                - 테넌트: {node.get('tenant', '미지정')}
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
                구현방안: [기술적 구현 또는 실행 계획을 단계별로 나열 (1. 2. 3. 형태 또는 - 형태로)]  
                기대효과: [예상 성과 또는 효과를 항목별로 나열 (- 형태로 작성)]  
                근거: [위의 공모전 정보와 노드들이 어떻게 연결되어 이 아이디어가 도출되었는지를 connecting the dots 관점에서 논리적 단계별로 설명 (- 형태로 작성)]
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
            "rationale": "",
            "contest_info": contest_info,
            "raw_response": generated_text,
        }

        try:
            # 더 강건한 파싱을 위한 키워드 매핑
            keyword_mappings = {
                "제목": "title",
                "개요": "overview",
                "문제의식": "problem",
                "솔루션": "solution",
                "구현방안": "implementation",
                "기대효과": "expected_effect",
                "근거": "rationale",
            }

            lines = generated_text.split("\n")
            current_key = None

            for line in lines:
                line = line.strip()
                if not line:  # 빈 줄 건너뛰기
                    continue

                # 키워드 검색 (콜론 포함)
                found_key = False
                for keyword, key in keyword_mappings.items():
                    if (
                        line.startswith(f"{keyword}:")
                        or line.startswith(f"**{keyword}:**")
                        or line.startswith(f"#{keyword}")
                    ):
                        current_key = key
                        # 콜론 이후 내용 추출
                        content = line.split(":", 1)[1].strip() if ":" in line else ""
                        idea[current_key] = content
                        found_key = True
                        break

                # 키워드가 발견되지 않았고 현재 키가 있으면 내용 추가
                if not found_key and current_key and line:
                    if idea[current_key]:
                        idea[current_key] += " " + line
                    else:
                        idea[current_key] = line

        except Exception as e:
            print(f"[파싱오류] {e}")
            print(f"[원본응답] {generated_text}")
            idea["title"] = "파싱 실패"
            idea["overview"] = f"결과 파싱에 실패했습니다. 오류: {str(e)}"

        # 파싱 후 빈 필드가 있는지 확인 및 디버깅
        empty_fields = [
            key
            for key, value in idea.items()
            if key not in ["contest_info", "raw_response", "ai_name"] and not value
        ]
        if empty_fields:
            print(f"[경고] 빈 필드 발견: {empty_fields}")
            print(f"[원본응답 일부] {generated_text[:500]}...")

        # 최소한의 제목은 확보
        if not idea.get("title"):
            idea["title"] = "제목 없음"

        # 구현방안, 기대효과, 근거 필드 가독성 개선 (항목별 개행 추가)
        if idea.get("implementation"):
            idea["implementation"] = format_list_text(idea["implementation"])
        if idea.get("expected_effect"):
            idea["expected_effect"] = format_list_text(idea["expected_effect"])
        if idea.get("rationale"):
            idea["rationale"] = format_list_text(idea["rationale"])

        return idea


def format_list_text(text: str) -> str:
    """텍스트의 가독성을 개선하여 각 항목별로 개행 추가"""
    if not text:
        return text

    import re

    # 먼저 텍스트를 정리
    text = text.strip()

    # "- " 패턴이 있으면 우선 처리
    if "- " in text and not text.startswith("- "):
        # "- " 앞에 개행 추가 (첫 번째 항목 제외)
        formatted_text = re.sub(r"([^.\n])\s*(-\s)", r"\1\n\2", text)
    else:
        # "- " 패턴이 없거나 이미 첫 번째가 "- "로 시작하면 숫자 패턴도 처리
        formatted_text = text

        # "1. ", "2. " 등의 패턴 앞에 개행 추가 (첫 번째 항목 제외)
        formatted_text = re.sub(r"([^.\n])(\d+\.\s)", r"\1\n\2", formatted_text)

        # "- " 로 시작하는 항목들 처리
        formatted_text = re.sub(r"([^.\n])\s*(-\s)", r"\1\n\2", formatted_text)

    # "• " 로 시작하는 항목들 처리
    formatted_text = re.sub(r"([^.\n])\s*(•\s)", r"\1\n\2", formatted_text)

    # 처음에 개행이 추가된 경우 제거
    if formatted_text.startswith("\n"):
        formatted_text = formatted_text[1:]

    return formatted_text


def format_implementation_text(text: str) -> str:
    """구현방안 텍스트의 가독성을 개선하여 각 항목별로 개행 추가 (하위 호환성)"""
    return format_list_text(text)


# 사용 예시
def create_openai_client(api_key: str = None) -> OpenAIClient:
    return OpenAIClient(api_key)
