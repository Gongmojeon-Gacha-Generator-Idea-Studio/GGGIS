import gradio as gr
import src.data_manager as dm
from src.idea_functions import (
    get_ideas_dataframe,
    get_idea_details_by_index,
    refresh_ideas,
    delete_idea,
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
    )


def handle_idea_selection(evt: gr.SelectData):
    """아이디어 선택 이벤트 처리"""
    print(f"[DEBUG] SelectData evt.index: {evt.index}")
    print(f"[DEBUG] SelectData evt.value: {evt.value}")

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
            original_index,  # selected_idea_index
            gr.update(visible=True),  # delete_idea_btn
            gr.update(visible=False, value=""),  # delete_status
            idea_details[6],  # created_at -> created_at_display
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
