import gradio as gr
from src.data_manager import initialize_data
import src.data_manager as dm
from src.node_functions import *
from src.idea_functions import *
from src.ui_handlers import (
    clear_idea_generation_fields,
    refresh_and_reset,
    refresh_and_reset_with_node_status,
    handle_idea_selection,
    handle_delete_idea,
)

# 앱 시작 시 데이터 초기화
initialize_data()

# Gradio 인터페이스 구성
with gr.Blocks(title="", theme=gr.themes.Soft()) as demo:

    # 헤더
    gr.Markdown("# 🔗 GGG Idea Studio")
    gr.Markdown("---")

    # 탭 구성
    with gr.Tabs():

        # 4. AI 아이디어 생성 탭
        with gr.Tab("🚀 AI 아이디어 생성") as idea_generation_tab:
            gr.Markdown("### AI 아이디어를 생성하세요")

            # 공모전 정보 섹션
            contest_title = gr.Textbox(
                label="공모전 제목", placeholder="참가할 공모전 제목을 입력하세요"
            )
            contest_theme = gr.Textbox(
                label="공모전 주제 [Domain]",
                placeholder="공모전의 주요 주제 혹은 공모전의 도메인을 입력하세요",
            )
            contest_description = gr.Textbox(
                label="공모전 설명 [Context]",
                lines=3,
                placeholder="공모전에 대한 상세 설명과 추가적인 맥락 정보를 입력하세요",
            )
            contest_context = gr.Textbox(
                label="공모전 맥락 [Igniter] (선택사항)",
                lines=2,
                placeholder="아이디에이션의 방향성을 결정하는 핵심 포인트를 입력하세요 (선택사항)",
            )

            # 아이디어 생성 섹션
            gr.Markdown("#### 🤖 아이디어 생성하기")
            with gr.Row():
                chatgpt_btn = gr.Button(
                    "🤖 ChatGPT로 아이디어 생성", variant="primary", size="lg"
                )
                gemini_btn = gr.Button(
                    "💎 Gemini로 생성 (준비중)",
                    variant="secondary",
                    size="lg",
                    interactive=False,
                )

            idea_generation_status = gr.Textbox(label="생성 상태", interactive=False)

            # 이벤트 연결
            chatgpt_btn.click(
                generate_idea_with_chatgpt,
                inputs=[
                    contest_title,
                    contest_theme,
                    contest_description,
                    contest_context,
                ],
                outputs=[
                    idea_generation_status,
                    contest_title,
                    contest_theme,
                    contest_description,
                    contest_context,
                ],
            )

            gemini_btn.click(
                generate_idea_with_gemini,
                inputs=[
                    contest_title,
                    contest_theme,
                    contest_description,
                    contest_context,
                ],
                outputs=[
                    idea_generation_status,
                    contest_title,
                    contest_theme,
                    contest_description,
                    contest_context,
                ],
            )

            # 탭 클릭시 자동 초기화 기능 제거 (사용자 요청)

        # 5. 생성된 아이디어 확인하기 탭
        with gr.Tab("💭 생성된 아이디어 확인하기") as ideas_view_tab:
            gr.Markdown(
                "### AI로 생성된 아이디어를 확인하고 상세 내용을 볼 수 있습니다"
            )

            # 아이디어 목록
            ideas_dataframe = gr.Dataframe(
                value=get_ideas_dataframe(),
                headers=["생성일시", "아이디어 제목", "아이디어 개요", "AI 이름"],
                interactive=False,
                elem_id="ideas_table",
            )

            # 선택된 아이디어 상세 정보
            gr.Markdown("#### 📋 선택된 아이디어 상세 정보")
            gr.Markdown(
                "*위 테이블에서 행을 클릭하면 해당 아이디어의 상세 정보가 표시됩니다.*"
            )

            with gr.Accordion("🎯 아이디어 상세 정보", open=True):
                selected_title = gr.Textbox(label="아이디어 제목", interactive=False)
                contest_info_display = gr.Textbox(
                    label="공모전 정보", lines=4, interactive=False
                )
                problem_display = gr.Textbox(
                    label="문제 의식", lines=3, interactive=False
                )
                solution_display = gr.Textbox(
                    label="솔루션 해결 방안", lines=4, interactive=False
                )
                implementation_display = gr.Textbox(
                    label="구현 방안", lines=3, interactive=False
                )
                expected_effect_display = gr.Textbox(
                    label="기대 효과", lines=3, interactive=False
                )
                created_at_display = gr.Textbox(label="생성일시", interactive=False)

            # 삭제 관련 UI
            selected_idea_index = gr.State(-1)  # 선택된 아이디어 인덱스

            with gr.Row():
                delete_idea_btn = gr.Button(
                    "🗑️ 선택된 아이디어 삭제", variant="stop", visible=False
                )
                delete_status = gr.Textbox(
                    label="", interactive=False, visible=False, show_label=False
                )

            # 이벤트 연결

            ideas_dataframe.select(
                fn=handle_idea_selection,
                outputs=[
                    selected_title,
                    contest_info_display,
                    problem_display,
                    solution_display,
                    implementation_display,
                    expected_effect_display,
                    selected_idea_index,
                    delete_idea_btn,
                    delete_status,
                    created_at_display,
                ],
            )

            delete_idea_btn.click(
                fn=handle_delete_idea,
                inputs=[selected_idea_index],
                outputs=[
                    delete_status,
                    ideas_dataframe,
                    delete_idea_btn,
                    selected_title,
                    contest_info_display,
                    problem_display,
                    solution_display,
                    implementation_display,
                    expected_effect_display,
                    created_at_display,
                ],
            )

            # 탭 클릭시 자동 새로고침 및 아이디어 생성 상태 초기화
            ideas_view_tab.select(
                fn=refresh_and_reset,
                outputs=[
                    ideas_dataframe,
                    delete_idea_btn,
                    delete_status,
                    selected_title,
                    contest_info_display,
                    problem_display,
                    solution_display,
                    implementation_display,
                    expected_effect_display,
                    created_at_display,
                    idea_generation_status,  # 아이디어 생성 상태 초기화
                ],
            )

        # 1. 포폴 업로드 탭
        with gr.Tab("📁 포폴업로드", visible=False) as portfolio_upload_tab:
            gr.Markdown(
                "### 포트폴리오 파일을 업로드하면 AI가 분석하여 노드를 자동 생성합니다"
            )

            file_upload = gr.Files(
                label="포트폴리오 파일 업로드 (PDF, Word)",
                file_count="multiple",
                file_types=[".pdf", ".doc", ".docx"],
            )

            upload_status = gr.Textbox(label="업로드 상태", interactive=False)

            with gr.Row():
                upload_btn = gr.Button("📤 파일 업로드", variant="secondary")
                process_btn = gr.Button("🤖 AI 분석 시작", variant="primary")

            process_status = gr.Textbox(label="분석 결과", interactive=False)

            # 이벤트 연결
            upload_btn.click(
                upload_portfolio_files,
                inputs=[file_upload],
                outputs=[upload_status, gr.State()],
            )

            process_btn.click(
                process_uploaded_files, inputs=[upload_status], outputs=[process_status]
            )

        # 2. 노드 입력하기 탭
        with gr.Tab("✏️ 노드 입력하기") as node_input_tab:
            gr.Markdown("### 노드를 생성하세요")

            with gr.Column():
                title_input = gr.Textbox(
                    label="1. 노드 제목", placeholder="노드 제목을 입력하세요"
                )
                description_input = gr.Textbox(
                    label="2. 노드에 대해 소개해주세요. (핵심기능과 사용 기술을 포함하여 작성해주세요.)",
                    lines=5,
                    placeholder="노드의 핵심 기능과 사용된 기술을 포함하여 자세히 설명해주세요",
                )

                tenant_input = gr.Textbox(
                    label="3. 테넌트 (그룹)",
                    placeholder="이 노드가 속할 그룹을 입력하세요 (예: 국민대, SuperbAI)",
                )

                gr.Markdown("#### 4. 노드에 대한 키워드를 입력해주세요")
                with gr.Row():
                    keyword_input = gr.Textbox(
                        label="키워드",
                        placeholder="키워드를 입력하세요 (예: 파이썬, 인공지능, AWS)",
                        scale=2,
                    )
                    add_keyword_btn = gr.Button(
                        "➕ 키워드 추가",
                        variant="secondary",
                        scale=1,
                    )

                tags_display = gr.Textbox(
                    label="추가된 키워드",
                    interactive=False,
                    placeholder="키워드가 여기에 표시됩니다",
                )
                keyword_status = gr.Textbox(label="키워드 추가 상태", interactive=False)

            create_btn = gr.Button("✨ 노드 생성하기", variant="primary", size="lg")
            create_status = gr.Textbox(label="생성 결과", interactive=False)

            # 이벤트 연결
            add_keyword_btn.click(
                add_keyword,
                inputs=[keyword_input, tags_display],
                outputs=[tags_display, keyword_input, keyword_status],
            )

            # 엔터키로도 키워드 추가 가능
            keyword_input.submit(
                add_keyword,
                inputs=[keyword_input, tags_display],
                outputs=[tags_display, keyword_input, keyword_status],
            )

            create_btn.click(
                create_node,
                inputs=[title_input, description_input, tenant_input, tags_display],
                outputs=[
                    create_status,
                    title_input,
                    description_input,
                    tenant_input,
                    keyword_input,
                    tags_display,
                    keyword_status,
                ],
            )

        # 3. 내 노드 확인하기 탭
        with gr.Tab("📋 내 노드 확인하기") as node_view_tab:
            gr.Markdown("### 생성된 모든 노드를 확인하고 관리하세요")

            # 필터링 옵션들
            with gr.Row():
                search_input = gr.Textbox(
                    label="🔍 노드 이름 검색",
                    placeholder="검색할 노드 이름을 입력하세요...",
                    scale=2,
                )

            with gr.Row():
                tenant_filter = gr.Dropdown(
                    label="🏢 테넌트 필터 (다중선택)",
                    choices=[],  # 초기에는 빈 리스트
                    multiselect=True,
                    scale=1,
                )
                tag_filter = gr.Dropdown(
                    label="🏷️ 태그 필터 (다중선택)",
                    choices=[],  # 초기에는 빈 리스트
                    multiselect=True,
                    scale=1,
                )

            nodes_dataframe = gr.Dataframe(
                value=get_nodes_dataframe(),
                headers=["생성일자", "노드 이름", "테넌트", "설명", "태그"],
                interactive=False,
                wrap=False,
                elem_id="nodes_table",
            )

            # 이벤트 연결 - 모든 필터 변경 시 실시간 필터링
            for filter_component in [search_input, tenant_filter, tag_filter]:
                filter_component.change(
                    filter_nodes_multi,
                    inputs=[search_input, tenant_filter, tag_filter],
                    outputs=[nodes_dataframe],
                )

            # 내 노드 확인하기 탭 클릭시 자동 새로고침 및 상태 초기화
            def refresh_and_clear_status():
                df, tags, tenants = refresh_nodes()
                return (
                    df,
                    "",  # 검색 입력 초기화
                    gr.update(choices=tenants, value=[]),  # 테넌트 필터 업데이트
                    gr.update(choices=tags, value=[]),  # 태그 필터 업데이트
                    "",  # 아이디어 생성 상태 초기화
                    "",  # 노드 생성 상태 초기화
                )

            node_view_tab.select(
                fn=refresh_and_clear_status,
                outputs=[
                    nodes_dataframe,
                    search_input,
                    tenant_filter,
                    tag_filter,
                    idea_generation_status,
                    create_status,
                ],
            )

        # 탭 간 상태 초기화 이벤트 (모든 컴포넌트 정의 후)

    # AI 아이디어 생성 탭 클릭시 노드 생성 상태만 초기화
    idea_generation_tab.select(
        fn=lambda: "",
        outputs=[create_status],
    )

    # 포폴 업로드 탭 클릭시 노드 생성 상태만 초기화
    portfolio_upload_tab.select(
        fn=lambda: "",
        outputs=[create_status],
    )

    # 노드 입력하기 탭 클릭시 아이디어 생성 상태, 노드 생성 상태만 초기화
    node_input_tab.select(
        fn=lambda: ("", ""),
        outputs=[idea_generation_status, create_status],
    )

# 앱 실행
if __name__ == "__main__":
    demo.launch(share=False, debug=True, server_name="0.0.0.0", server_port=7860)
