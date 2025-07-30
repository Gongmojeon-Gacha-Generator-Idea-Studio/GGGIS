import pandas as pd
from data_manager import nodes_data, ideas_data, save_ideas, load_ideas
from openai_client import create_openai_client
from typing import List, Dict, Any

def generate_idea_with_chatgpt(contest_title, contest_theme, contest_description, contest_context="", api_key=""):
    """ChatGPT를 이용해 아이디어 생성"""
    if not contest_title or not contest_theme:
        return "공모전 제목과 주제를 입력해주세요."
    
    if not api_key:
        return "OpenAI API 키를 입력해주세요."
    
    try:
        # OpenAI 클라이언트 생성
        client = create_openai_client(api_key)
        
        # 공모전 정보 구성
        contest_info = {
            "title": contest_title,
            "theme": contest_theme,
            "description": contest_description,
            "context": contest_context
        }
        
        # 아이디어 생성
        generated_idea = client.generate_idea(contest_info, nodes_data)
        
        if "error" in generated_idea:
            return generated_idea["error"]
        
        # 생성된 아이디어를 ideas_data에 저장
        ideas_data.append(generated_idea)
        save_ideas()
        
        return f"아이디어 '{generated_idea['title']}'가 성공적으로 생성되었습니다!"
        
    except Exception as e:
        return f"아이디어 생성 중 오류가 발생했습니다: {str(e)}"

def get_ideas_dataframe():
    """생성된 아이디어들을 데이터프레임으로 변환"""
    if not ideas_data:
        return pd.DataFrame(columns=["AI 이름", "아이디어 제목", "아이디어 개요"])
    
    df_data = []
    for idea in ideas_data:
        df_data.append({
            "AI 이름": idea.get("ai_name", "Unknown"),
            "아이디어 제목": idea.get("title", "제목 없음"),
            "아이디어 개요": idea.get("overview", "개요 없음")
        })
    
    return pd.DataFrame(df_data)

def get_idea_details(selection_data):
    """선택된 아이디어의 상세 정보 반환"""
    if not selection_data or not hasattr(selection_data, 'index') or len(selection_data.index) == 0:
        return "아이디어를 선택해주세요.", "", "", "", "", ""
    
    # 선택된 행의 인덱스 가져오기
    selected_index = selection_data.index[0]
    
    if selected_index >= len(ideas_data):
        return "선택된 아이디어를 찾을 수 없습니다.", "", "", "", "", ""
    
    idea = ideas_data[selected_index]
    
    title = idea.get("title", "제목 없음")
    problem = idea.get("problem", "문제의식 정보가 없습니다.")
    solution = idea.get("solution", "솔루션 정보가 없습니다.")
    implementation = idea.get("implementation", "구현방안 정보가 없습니다.")
    expected_effect = idea.get("expected_effect", "기대효과 정보가 없습니다.")
    
    # 공모전 정보
    contest_info = idea.get("contest_info", {})
    contest_details = f"""공모전 제목: {contest_info.get('title', 'N/A')}
주제: {contest_info.get('theme', 'N/A')}
설명: {contest_info.get('description', 'N/A')}
맥락: {contest_info.get('context', 'N/A')}"""
    
    return title, contest_details, problem, solution, implementation, expected_effect

def refresh_ideas():
    """아이디어 목록 새로고침"""
    load_ideas()
    return get_ideas_dataframe()

def clear_ideas():
    """모든 아이디어 삭제"""
    global ideas_data
    ideas_data = []
    save_ideas()
    return get_ideas_dataframe()

def delete_idea(selected_index):
    """선택된 아이디어 삭제"""
    if selected_index is None or selected_index >= len(ideas_data):
        return "삭제할 아이디어를 선택해주세요.", get_ideas_dataframe()
    
    deleted_idea = ideas_data.pop(selected_index)
    save_ideas()
    
    return f"아이디어 '{deleted_idea.get('title', '제목 없음')}'가 삭제되었습니다.", get_ideas_dataframe()

# 추가: Gemini API 연동을 위한 준비 함수
def generate_idea_with_gemini(contest_title, contest_theme, contest_description, contest_context="", api_key=""):
    """Gemini를 이용해 아이디어 생성 (향후 구현 예정)"""
    return "Gemini API 연동은 아직 구현되지 않았습니다."
