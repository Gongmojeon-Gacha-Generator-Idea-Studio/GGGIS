import gradio as gr
from src.data_manager import initialize_data
from src.node_functions import (
    get_nodes_dataframe,
    add_keyword,
    create_node,
    filter_nodes_multi,
)
from src.idea_functions import (
    get_ideas_dataframe,
    generate_idea_with_chatgpt,
    generate_idea_with_gemini,
)
from src.ui_handlers import (
    refresh_and_reset,
    handle_idea_selection,
    handle_delete_idea,
    handle_node_selection,
    handle_edit_node,
    handle_delete_node,
    filter_ideas,
    refresh_and_clear_status,
    refresh_idea_nodes,
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

            # 노드 연결 섹션
            gr.Markdown("#### 🔗 노드 연결")
            gr.Markdown("*아이디어 생성에 사용할 노드들을 필터링하여 선택하세요*")

            # 노드 필터링 옵션들
            with gr.Row():
                idea_node_search_input = gr.Textbox(
                    label="🔍 노드 이름 검색",
                    placeholder="검색할 노드 이름을 입력하세요...",
                    scale=2,
                )

            with gr.Row():
                idea_tenant_filter = gr.Dropdown(
                    label="🏢 테넌트 필터 (다중선택)",
                    choices=[],  # 초기에는 빈 리스트
                    multiselect=True,
                    scale=1,
                )
                idea_tag_filter = gr.Dropdown(
                    label="🏷️ 태그 필터 (다중선택)",
                    choices=[],  # 초기에는 빈 리스트
                    multiselect=True,
                    scale=1,
                )

            idea_nodes_dataframe = gr.Dataframe(
                value=get_nodes_dataframe(),
                headers=["생성일자", "노드 이름", "테넌트", "설명", "태그"],
                interactive=False,
                wrap=False,
                elem_id="idea_nodes_table",
                height=300,
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

            # 노드 필터링 이벤트들
            for filter_component in [
                idea_node_search_input,
                idea_tenant_filter,
                idea_tag_filter,
            ]:
                filter_component.change(
                    filter_nodes_multi,
                    inputs=[
                        idea_node_search_input,
                        idea_tenant_filter,
                        idea_tag_filter,
                    ],
                    outputs=[idea_nodes_dataframe],
                )

            chatgpt_btn.click(
                generate_idea_with_chatgpt,
                inputs=[
                    contest_title,
                    contest_theme,
                    contest_description,
                    contest_context,
                    idea_node_search_input,
                    idea_tenant_filter,
                    idea_tag_filter,
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
                    idea_node_search_input,
                    idea_tenant_filter,
                    idea_tag_filter,
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

            # 검색 필드
            idea_search_input = gr.Textbox(
                label="🔍 공모전 제목 또는 아이디어 제목 검색",
                placeholder="검색할 제목을 입력하세요...",
                scale=2,
            )

            # 아이디어 목록
            ideas_dataframe = gr.Dataframe(
                value=get_ideas_dataframe(),
                headers=[
                    "생성일시",
                    "공모전 제목",
                    "아이디어 제목",
                    "아이디어 개요",
                    "AI 이름",
                ],
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

            with gr.Accordion("🔗 사용된 노드 및 필터 정보", open=False):
                used_nodes_display = gr.Textbox(
                    label="사용된 노드", lines=5, interactive=False
                )
                used_filters_display = gr.Textbox(
                    label="사용된 필터", lines=5, interactive=False
                )
                rationale_display = gr.Textbox(
                    label="아이디어 생성 근거 (Connecting the Dots)",
                    lines=8,
                    interactive=False,
                )

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

            # 검색 필드 이벤트
            idea_search_input.change(
                fn=filter_ideas,
                inputs=[idea_search_input],
                outputs=[ideas_dataframe],
            )

            ideas_dataframe.select(
                fn=handle_idea_selection,
                outputs=[
                    selected_title,
                    contest_info_display,
                    problem_display,
                    solution_display,
                    implementation_display,
                    expected_effect_display,
                    created_at_display,
                    used_nodes_display,
                    used_filters_display,
                    rationale_display,
                    selected_idea_index,
                    delete_idea_btn,
                    delete_status,
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
                    used_nodes_display,
                    used_filters_display,
                    rationale_display,
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
                    used_nodes_display,
                    used_filters_display,
                    rationale_display,
                    idea_generation_status,  # 아이디어 생성 상태 초기화
                    idea_search_input,  # 검색 필드 초기화
                ],
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

            # 선택된 노드 상세 정보
            gr.Markdown("#### 📋 선택된 노드 상세 정보")
            gr.Markdown(
                "*위 테이블에서 행을 클릭하면 해당 노드의 상세 정보가 표시됩니다.*"
            )

            with gr.Accordion("🔧 노드 상세 정보", open=True):
                selected_node_title = gr.Textbox(label="노드 제목", interactive=True)
                selected_node_description = gr.Textbox(
                    label="노드 설명", lines=4, interactive=True
                )
                selected_node_tenant = gr.Textbox(label="테넌트", interactive=True)
                selected_node_tags = gr.Textbox(
                    label="태그 (콤마로 구분)", interactive=True
                )
                selected_node_created_at = gr.Textbox(
                    label="생성일시", interactive=False
                )

            # 편집/삭제 관련 UI
            selected_node_index = gr.State(-1)  # 선택된 노드 인덱스

            with gr.Row():
                edit_node_btn = gr.Button(
                    "✏️ 선택된 노드 편집", variant="primary", visible=False
                )
                delete_node_btn = gr.Button(
                    "🗑️ 선택된 노드 삭제", variant="stop", visible=False
                )

            node_action_status = gr.Textbox(
                label="", interactive=False, visible=False, show_label=False
            )

            # 이벤트 연결 - 모든 필터 변경 시 실시간 필터링
            for filter_component in [search_input, tenant_filter, tag_filter]:
                filter_component.change(
                    filter_nodes_multi,
                    inputs=[search_input, tenant_filter, tag_filter],
                    outputs=[nodes_dataframe],
                )

            # 노드 선택 이벤트
            nodes_dataframe.select(
                fn=handle_node_selection,
                outputs=[
                    selected_node_title,
                    selected_node_description,
                    selected_node_tenant,
                    selected_node_tags,
                    selected_node_created_at,
                    selected_node_index,
                    edit_node_btn,
                    delete_node_btn,
                    node_action_status,
                ],
            )

            # 노드 편집 이벤트
            edit_node_btn.click(
                fn=handle_edit_node,
                inputs=[
                    selected_node_index,
                    selected_node_title,
                    selected_node_description,
                    selected_node_tenant,
                    selected_node_tags,
                ],
                outputs=[
                    node_action_status,
                    nodes_dataframe,
                ],
            )

            # 노드 삭제 이벤트
            delete_node_btn.click(
                fn=handle_delete_node,
                inputs=[selected_node_index],
                outputs=[
                    node_action_status,
                    nodes_dataframe,
                    edit_node_btn,
                    delete_node_btn,
                    selected_node_title,
                    selected_node_description,
                    selected_node_tenant,
                    selected_node_tags,
                    selected_node_created_at,
                ],
            )

            # 내 노드 확인하기 탭 클릭시 자동 새로고침 및 상태 초기화
            node_view_tab.select(
                fn=refresh_and_clear_status,
                outputs=[
                    nodes_dataframe,
                    search_input,
                    tenant_filter,
                    tag_filter,
                    idea_generation_status,
                    create_status,
                    selected_node_title,
                    selected_node_description,
                    selected_node_tenant,
                    selected_node_tags,
                    selected_node_created_at,
                    selected_node_index,
                    edit_node_btn,
                    delete_node_btn,
                    node_action_status,
                ],
            )

        # 탭 간 상태 초기화 이벤트 (모든 컴포넌트 정의 후)

    # AI 아이디어 생성 탭 클릭시 상태 초기화 및 노드 필터 초기화
    idea_generation_tab.select(
        fn=refresh_idea_nodes,
        outputs=[
            idea_nodes_dataframe,
            idea_node_search_input,
            idea_tenant_filter,
            idea_tag_filter,
            create_status,
        ],
    )

    # 노드 입력하기 탭 클릭시 아이디어 생성 상태, 노드 생성 상태만 초기화
    node_input_tab.select(
        fn=lambda: ("", ""),
        outputs=[idea_generation_status, create_status],
    )

# 앱 실행
if __name__ == "__main__":
    demo.launch(share=False, debug=True, server_name="0.0.0.0", server_port=7860)
