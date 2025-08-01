import pandas as pd
import gradio as gr
import src.data_manager as dm
from datetime import datetime


def add_keyword(keyword, current_tags):
    """키워드 추가 (콤마로 구분된 여러 키워드 지원)"""
    if not keyword:
        return current_tags, "", ""

    # 기존 태그 리스트 가져오기
    if current_tags:
        tags_list = [tag.strip() for tag in current_tags.split(",") if tag.strip()]
    else:
        tags_list = []

    # 입력된 키워드를 콤마로 분할하여 처리
    new_keywords = [kw.strip() for kw in keyword.split(",") if kw.strip()]

    # 중복 키워드 체크
    duplicate_keywords = []
    added_keywords = []

    for new_keyword in new_keywords:
        if new_keyword:
            if new_keyword in tags_list:
                duplicate_keywords.append(new_keyword)
            else:
                tags_list.append(new_keyword)
                added_keywords.append(new_keyword)

    # 중복 키워드가 있는 경우 경고 메시지 표시
    if duplicate_keywords and not added_keywords:
        # 모든 키워드가 중복인 경우
        duplicate_list = ", ".join(duplicate_keywords)
        return current_tags, "", f"❌ 이미 존재하는 키워드입니다: {duplicate_list}"
    elif duplicate_keywords and added_keywords:
        # 일부 키워드만 중복인 경우
        duplicate_list = ", ".join(duplicate_keywords)
        updated_tags = ", ".join(tags_list)
        return (
            updated_tags,
            "",
            f"⚠️ 일부 키워드가 중복되어 제외되었습니다: {duplicate_list}",
        )

    # 업데이트된 태그 리스트와 빈 키워드 입력 필드, 성공 메시지 반환
    updated_tags = ", ".join(tags_list)
    added_list = ", ".join(added_keywords)
    return updated_tags, "", f"✅ 키워드가 추가되었습니다: {added_list}"


def create_node(title, description, tenant, tags):
    """사용자 입력으로 새 노드 생성"""
    if not title or not description:
        return (
            "❌ 프로젝트 제목과 설명을 모두 입력해주세요.",
            title,
            description,
            tenant,
            "",
            tags,
            "",
        )

    # 테넌트 필수 검증
    if not tenant:
        return (
            "❌ 테넌트(그룹)를 입력해주세요.",
            title,
            description,
            tenant,
            "",
            tags,
            "",
        )

    # 태그를 리스트로 변환
    tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []

    # 키워드 필수 검증
    if not tags_list:
        return (
            "❌ 키워드를 최소 1개 이상 입력해주세요!",
            title,
            description,
            tenant,
            "",
            tags,
            "",
        )

    new_node = {
        "title": title,
        "description": description,
        "tenant": tenant.strip(),
        "tags": tags_list,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    dm.nodes_data.append(new_node)

    dm.save_nodes()

    # 성공시 모든 필드 초기화
    return "✅ 새 노드가 성공적으로 생성되었습니다!", "", "", "", "", "", ""


def get_nodes_dataframe(search_text="", selected_tenants=None, selected_tags=None):
    """저장된 노드들을 데이터프레임으로 변환 (다중 필터 지원)"""
    # 컬럼명 정의
    columns = ["생성일자", "노드 이름", "테넌트", "설명", "태그"]

    if not dm.nodes_data:
        return pd.DataFrame(columns=columns)

    # 필터링된 노드들
    filtered_nodes = []
    for node in dm.nodes_data:
        # 텍스트 검색 필터 (노드 이름에서 검색)
        if search_text and search_text.lower() not in node["title"].lower():
            continue

        # 테넌트 필터
        if selected_tenants and node.get("tenant", "미지정") not in selected_tenants:
            continue

        # 태그 필터 (선택된 태그 중 하나라도 포함되어야 함)
        if selected_tags:
            node_tags = node.get("tags", [])
            if not any(tag in node_tags for tag in selected_tags):
                continue

        filtered_nodes.append(
            {
                "생성일자": node.get("created_at", "미상"),
                "노드 이름": node["title"],
                "테넌트": node.get("tenant", "미지정"),
                "설명": (
                    node["description"][:100] + "..."
                    if len(node["description"]) > 100
                    else node["description"]
                ),
                "태그": ", ".join(node.get("tags", [])),
            }
        )

    # 필터링 결과가 없어도 컬럼명이 유지되도록 빈 DataFrame 반환
    if not filtered_nodes:
        return pd.DataFrame(columns=columns)

    return pd.DataFrame(filtered_nodes)


def filter_nodes_multi(search_text, selected_tenants, selected_tags):
    """다중 필터로 노드 필터링"""
    df = get_nodes_dataframe(search_text, selected_tenants, selected_tags)
    return gr.update(value=df)


def get_all_tags():
    """모든 노드의 태그 목록 반환"""
    all_tags = set()
    for node in dm.nodes_data:
        all_tags.update(node.get("tags", []))
    return sorted(list(all_tags))


def get_all_tenants():
    """모든 노드의 테넌트 목록 반환"""
    all_tenants = set()
    for node in dm.nodes_data:
        tenant = node.get("tenant", "미지정")
        if tenant:
            all_tenants.add(tenant)
    return sorted(list(all_tenants))


def refresh_nodes():
    """노드 목록 새로고침"""
    dm.load_nodes()
    return get_nodes_dataframe(), get_all_tags(), get_all_tenants()


def get_node_details_by_index(index):
    """인덱스로 노드 상세 정보 가져오기"""
    if 0 <= index < len(dm.nodes_data):
        node = dm.nodes_data[index]
        return (
            node.get("title", ""),
            node.get("description", ""),
            node.get("tenant", ""),
            ", ".join(node.get("tags", [])),
            node.get("created_at", ""),
        )
    return ("노드를 선택해주세요.", "", "", "", "")


def update_node(index, title, description, tenant, tags_str):
    """노드 정보 업데이트"""
    if not title or not description:
        return "❌ 노드 제목과 설명을 모두 입력해주세요.", get_nodes_dataframe()

    if not tenant:
        return "❌ 테넌트를 입력해주세요.", get_nodes_dataframe()

    # 태그를 리스트로 변환
    tags_list = (
        [tag.strip() for tag in tags_str.split(",") if tag.strip()] if tags_str else []
    )

    if not tags_list:
        return "❌ 태그를 최소 1개 이상 입력해주세요.", get_nodes_dataframe()

    if 0 <= index < len(dm.nodes_data):
        dm.nodes_data[index].update(
            {
                "title": title,
                "description": description,
                "tenant": tenant.strip(),
                "tags": tags_list,
            }
        )
        dm.save_nodes()
        return "✅ 노드가 성공적으로 수정되었습니다.", get_nodes_dataframe()

    return "❌ 수정할 노드를 찾을 수 없습니다.", get_nodes_dataframe()


def delete_node(index):
    """노드 삭제"""
    if 0 <= index < len(dm.nodes_data):
        deleted_node = dm.nodes_data.pop(index)
        dm.save_nodes()
        return (
            f"노드 '{deleted_node.get('title', '알 수 없음')}'가 삭제되었습니다.",
            get_nodes_dataframe(),
        )

    return "❌ 삭제할 노드를 찾을 수 없습니다.", get_nodes_dataframe()
