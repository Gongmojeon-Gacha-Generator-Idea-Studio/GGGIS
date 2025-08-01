import gradio as gr
import src.data_manager as dm
from src.idea_functions import (
    get_ideas_dataframe,
    get_idea_details_by_index,
    refresh_ideas,
    delete_idea,
)
from src.node_functions import (
    get_nodes_dataframe,
    get_node_details_by_index,
    update_node,
    delete_node,
)


def clear_idea_generation_fields():
    """AI 아이디어 생성 탭 클릭시 모든 입력 필드 초기화"""
    return "", "", "", "", ""


def refresh_and_reset():
    """아이디어 목록 새로고침하고 모든 상태 초기화"""
    updated_df = refresh_ideas()
    return (
        updated_df,
        gr.update(visible=False),  # 삭제 버튼 숨기기
        gr.update(visible=False, value=""),  # 삭제 상태 숨기기
        "아이디어를 선택해주세요.",
        "",
        "",
        "",
        "",
        "",
        "",  # 생성일시 초기화 추가
        "",  # 아이디어 생성 상태 초기화 추가
        "",  # 검색 필드 초기화 추가
    )


def refresh_and_reset_with_node_status():
    """아이디어 목록 새로고침하고 노드 생성 상태까지 모든 상태 초기화"""
    updated_df = refresh_ideas()
    return (
        updated_df,
        gr.update(visible=False),  # 삭제 버튼 숨기기
        gr.update(visible=False, value=""),  # 삭제 상태 숨기기
        "아이디어를 선택해주세요.",
        "",
        "",
        "",
        "",
        "",
        "",  # 생성일시 초기화 추가
        "",  # 아이디어 생성 상태 초기화 추가
        "",  # 노드 생성 상태 초기화 추가
    )


def handle_idea_selection(evt: gr.SelectData):
    """아이디어 선택 이벤트 처리"""

    if evt.index is not None and len(evt.index) >= 1:
        display_index = evt.index[0]  # 화면에 표시된 인덱스

        # 정렬된 배열에서 원본 인덱스 찾기
        if not dm.ideas_data:
            return (
                "아이디어가 없습니다.",
                "",
                "",
                "",
                "",
                "",
                "",  # 생성일시 추가
                -1,
                gr.update(visible=False),
                gr.update(visible=False, value=""),
            )

        # 생성일시 기준으로 정렬된 아이디어 목록 생성
        sorted_ideas = sorted(
            dm.ideas_data,
            key=lambda x: x.get("created_at", "1900-01-01 00:00:00"),
            reverse=True,
        )

        if display_index >= len(sorted_ideas):
            return (
                "선택된 아이디어를 찾을 수 없습니다.",
                "",
                "",
                "",
                "",
                "",
                "",  # 생성일시 추가
                -1,
                gr.update(visible=False),
                gr.update(visible=False, value=""),
            )

        # 선택된 아이디어의 원본 인덱스 찾기
        selected_idea = sorted_ideas[display_index]
        original_index = dm.ideas_data.index(selected_idea)

        idea_details = get_idea_details_by_index(original_index)
        # 아이디어 선택시 삭제 버튼 표시
        # idea_details는 (title, contest_details, problem, solution, implementation, expected_effect, created_at) 순서
        return (
            idea_details[0],  # title -> selected_title
            idea_details[1],  # contest_details -> contest_info_display
            idea_details[2],  # problem -> problem_display
            idea_details[3],  # solution -> solution_display
            idea_details[4],  # implementation -> implementation_display
            idea_details[5],  # expected_effect -> expected_effect_display
            idea_details[6],  # created_at -> created_at_display
            original_index,  # selected_idea_index
            gr.update(visible=True),  # delete_idea_btn
            gr.update(visible=False, value=""),  # delete_status
        )

    return (
        "아이디어를 선택해주세요.",
        "",
        "",
        "",
        "",
        "",
        "",  # 생성일시 추가
        -1,
        gr.update(visible=False),
        gr.update(visible=False, value=""),
    )


def handle_delete_idea(selected_index):
    """아이디어 삭제 이벤트 처리"""
    if selected_index < 0:
        return (
            gr.update(visible=True, value="❌ 삭제할 아이디어를 선택해주세요."),
            get_ideas_dataframe(),
            gr.update(visible=False),
            "아이디어를 선택해주세요.",
            "",
            "",
            "",
            "",
            "",
            "",  # 생성일시 추가
        )

    try:
        result_message, updated_df = delete_idea(selected_index)
        return (
            gr.update(visible=True, value=f"✅ {result_message}"),
            updated_df,
            gr.update(visible=False),  # 삭제 버튼 숨기기
            "아이디어를 선택해주세요.",
            "",
            "",
            "",
            "",
            "",
            "",  # 생성일시 추가
        )
    except Exception as e:
        return (
            gr.update(visible=True, value=f"❌ 삭제 중 오류가 발생했습니다: {str(e)}"),
            get_ideas_dataframe(),
            gr.update(visible=False),
            "아이디어를 선택해주세요.",
            "",
            "",
            "",
            "",
            "",
            "",  # 생성일시 추가
        )


def handle_node_selection(evt: gr.SelectData):
    """노드 선택 이벤트 처리"""

    if evt.index is not None and len(evt.index) >= 1:
        display_index = evt.index[0]  # 화면에 표시된 인덱스

        # 정렬된 배열에서 원본 인덱스 찾기
        if not dm.nodes_data:
            return (
                "노드를 선택해주세요.",
                "",
                "",
                "",
                "",
                -1,
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False, value=""),
            )

        # 생성일시 기준으로 정렬된 노드 목록 생성
        sorted_nodes = sorted(
            dm.nodes_data,
            key=lambda x: x.get("created_at", "1900-01-01 00:00:00"),
            reverse=True,
        )

        if display_index >= len(sorted_nodes):
            return (
                "선택된 노드를 찾을 수 없습니다.",
                "",
                "",
                "",
                "",
                -1,
                gr.update(visible=False),
                gr.update(visible=False),
                gr.update(visible=False, value=""),
            )

        # 선택된 노드의 원본 인덱스 찾기
        selected_node = sorted_nodes[display_index]
        original_index = dm.nodes_data.index(selected_node)

        node_details = get_node_details_by_index(original_index)
        # 노드 선택시 편집/삭제 버튼 표시
        return (
            node_details[0],  # title -> selected_node_title
            node_details[1],  # description -> selected_node_description
            node_details[2],  # tenant -> selected_node_tenant
            node_details[3],  # tags -> selected_node_tags
            node_details[4],  # created_at -> selected_node_created_at
            original_index,  # selected_node_index
            gr.update(visible=True),  # edit_node_btn
            gr.update(visible=True),  # delete_node_btn
            gr.update(visible=False, value=""),  # node_action_status
        )

    return (
        "노드를 선택해주세요.",
        "",
        "",
        "",
        "",
        -1,
        gr.update(visible=False),
        gr.update(visible=False),
        gr.update(visible=False, value=""),
    )


def handle_edit_node(selected_index, title, description, tenant, tags):
    """노드 편집 이벤트 처리"""
    if selected_index < 0:
        return (
            gr.update(visible=True, value="❌ 편집할 노드를 선택해주세요."),
            get_nodes_dataframe(),
        )

    try:
        result_message, updated_df = update_node(
            selected_index, title, description, tenant, tags
        )
        return (
            gr.update(visible=True, value=result_message),
            updated_df,
        )
    except Exception as e:
        return (
            gr.update(visible=True, value=f"❌ 편집 중 오류가 발생했습니다: {str(e)}"),
            get_nodes_dataframe(),
        )


def handle_delete_node(selected_index):
    """노드 삭제 이벤트 처리"""
    if selected_index < 0:
        return (
            gr.update(visible=True, value="❌ 삭제할 노드를 선택해주세요."),
            get_nodes_dataframe(),
            gr.update(visible=False),  # edit_node_btn
            gr.update(visible=False),  # delete_node_btn
            "노드를 선택해주세요.",
            "",
            "",
            "",
            "",
        )

    try:
        result_message, updated_df = delete_node(selected_index)
        return (
            gr.update(visible=True, value=f"✅ {result_message}"),
            updated_df,
            gr.update(visible=False),  # edit_node_btn 숨기기
            gr.update(visible=False),  # delete_node_btn 숨기기
            "노드를 선택해주세요.",
            "",
            "",
            "",
            "",
        )
    except Exception as e:
        return (
            gr.update(visible=True, value=f"❌ 삭제 중 오류가 발생했습니다: {str(e)}"),
            get_nodes_dataframe(),
            gr.update(visible=False),  # edit_node_btn
            gr.update(visible=False),  # delete_node_btn
            "노드를 선택해주세요.",
            "",
            "",
            "",
            "",
        )
