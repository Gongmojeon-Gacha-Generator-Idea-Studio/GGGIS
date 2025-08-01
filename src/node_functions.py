import pandas as pd
from src.data_manager import *


def upload_portfolio_files(files):
    """포트폴리오 파일 업로드 처리"""
    if not files:
        return "파일을 선택해주세요.", ""

    uploaded_files = []
    for file in files:
        if file:
            uploaded_files.append(f"📄 {file.name}")

    files_display = "\n".join(uploaded_files)
    return f"업로드된 파일:\n{files_display}", files_display


def process_uploaded_files(files_display):
    """업로드된 파일들을 AI로 분석하여 노드 생성"""
    if not files_display:
        return "업로드된 파일이 없습니다."

    # TODO: 실제 AI 분석 로직 구현
    sample_node = {
        "title": "AI 분석된 프로젝트",
        "solution": "업로드된 파일에서 분석된 솔루션과 핵심 기능들을 포함한 상세 설명",
        "tags": ["AI", "데이터분석", "웹개발"],
        "source": "파일 업로드",
    }

    nodes_data.append(sample_node)
    save_nodes()

    return "파일 분석이 완료되어 노드가 생성되었습니다!"


def add_keyword(keyword, current_tags):
    """키워드 추가"""
    if not keyword:
        return current_tags, "키워드를 입력해주세요."

    if current_tags:
        tags_list = [tag.strip() for tag in current_tags.split(",") if tag.strip()]
    else:
        tags_list = []

    if keyword not in tags_list:
        tags_list.append(keyword)
        updated_tags = ", ".join(tags_list)
        return updated_tags, f"'{keyword}' 키워드가 추가되었습니다."
    else:
        return current_tags, "이미 존재하는 키워드입니다."


def create_node(title, solution, tags):
    """사용자 입력으로 새 노드 생성"""
    if not title or not solution:
        return "프로젝트 제목과 솔루션을 모두 입력해주세요."

    # 태그를 리스트로 변환
    tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()]

    new_node = {
        "title": title,
        "solution": solution,
        "tags": tags_list,
        "source": "직접 입력",
    }

    nodes_data.append(new_node)
    save_nodes()

    return "새 노드가 성공적으로 생성되었습니다!"


def get_nodes_dataframe(filter_tag=""):
    """저장된 노드들을 데이터프레임으로 변환"""
    if not nodes_data:
        return pd.DataFrame()

    # 필터링된 노드들
    filtered_nodes = []
    for node in nodes_data:
        if not filter_tag or filter_tag in node.get("tags", []):
            filtered_nodes.append(
                {
                    "프로젝트 제목": node["title"],
                    "솔루션 소개": (
                        node["solution"][:100] + "..."
                        if len(node["solution"]) > 100
                        else node["solution"]
                    ),
                    "태그": ", ".join(node.get("tags", [])),
                    "출처": node.get("source", "직접 입력"),
                }
            )

    return pd.DataFrame(filtered_nodes)


def filter_nodes(filter_tag):
    """태그로 노드 필터링"""
    return get_nodes_dataframe(filter_tag)


def get_all_tags():
    """모든 노드의 태그 목록 반환"""
    all_tags = set()
    for node in nodes_data:
        all_tags.update(node.get("tags", []))
    return [""] + sorted(list(all_tags))


def refresh_nodes():
    """노드 목록 새로고침"""
    from src.data_manager import load_nodes

    load_nodes()
    return get_nodes_dataframe(), get_all_tags()
