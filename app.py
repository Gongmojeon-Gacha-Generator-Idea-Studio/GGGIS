import gradio as gr
import json
import os
import pandas as pd
from typing import List, Dict, Any
from data_manager import initialize_data
from node_functions import (
    upload_portfolio_files, process_uploaded_files, add_keyword, create_node,
    get_nodes_dataframe, filter_nodes, get_all_tags, refresh_nodes
)
from idea_functions import (
    generate_idea_with_chatgpt, generate_idea_with_gemini,
    get_ideas_dataframe, refresh_ideas, get_idea_details
)

# 앱 시작 시 데이터 초기화
initialize_data()

# Gradio 인터페이스 구성
with gr.Blocks(title="노드폴리오", theme=gr.themes.Soft()) as app:
    
    # 헤더
    gr.Markdown("# 🔗 노드폴리오 테스트")
    gr.Markdown("---")
    
    # 탭 구성
    with gr.Tabs():
        
        # 1. 포폴 업로드 탭
        with gr.Tab("📁 포폴업로드"):
            gr.Markdown("### 포트폴리오 파일을 업로드하면 AI가 분석하여 노드를 자동 생성합니다")
            
            file_upload = gr.Files(
                label="포트폴리오 파일 업로드 (PDF, Word)",
                file_count="multiple",
                file_types=[".pdf", ".doc", ".docx"]
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
                outputs=[upload_status, gr.State()]
            )
            
            process_btn.click(
                process_uploaded_files,
                inputs=[upload_status],
                outputs=[process_status]
            )
        
        # 2. 노드 입력하기 탭
        with gr.Tab("✏️ 노드 입력하기"):
            gr.Markdown("### 프로젝트 정보를 직접 입력하여 노드를 생성하세요")
            
            with gr.Column():
                title_input = gr.Textbox(label="1. 프로젝트 제목", placeholder="프로젝트 제목을 입력하세요")
                solution_input = gr.Textbox(
                    label="2. 당신의 솔루션에 대해 소개해주세요. (핵심기능과 사용 기술을 포함하여 작성해주세요.)",
                    lines=5,
                    placeholder="솔루션의 핵심 기능과 사용된 기술을 포함하여 자세히 설명해주세요"
                )
                
                gr.Markdown("#### 3. 솔루션에 대한 키워드를 입력해주세요")
                with gr.Row():
                    keyword_input = gr.Textbox(label="키워드", placeholder="키워드를 입력하세요")
                    add_keyword_btn = gr.Button("➕ 키워드 추가", variant="secondary")
                
                tags_display = gr.Textbox(label="추가된 키워드", interactive=False, placeholder="키워드가 여기에 표시됩니다")
                keyword_status = gr.Textbox(label="키워드 추가 상태", interactive=False)
            
            create_btn = gr.Button("✨ 노드 생성하기", variant="primary", size="lg")
            create_status = gr.Textbox(label="생성 결과", interactive=False)
            
            # 이벤트 연결
            add_keyword_btn.click(
                add_keyword,
                inputs=[keyword_input, tags_display],
                outputs=[tags_display, keyword_status]
            )
            
            create_btn.click(
                create_node,
                inputs=[title_input, solution_input, tags_display],
                outputs=[create_status]
            )
        
        # 3. 내 노드 확인하기 탭
        with gr.Tab("📋 내 노드 확인하기"):
            gr.Markdown("### 생성된 모든 노드를 확인하고 관리하세요")
            
            with gr.Row():
                refresh_btn = gr.Button("🔄 새로고침", variant="secondary")
                tag_filter = gr.Dropdown(
                    label="태그로 필터링",
                    choices=get_all_tags(),
                    value="",
                    allow_custom_value=False
                )
            
            nodes_dataframe = gr.Dataframe(
                value=get_nodes_dataframe(),
                headers=["프로젝트 제목", "솔루션 소개", "태그", "출처"],
                interactive=False,
                wrap=True
            )
            
            # 이벤트 연결
            refresh_btn.click(
                refresh_nodes,
                outputs=[nodes_dataframe, tag_filter]
            )
            
            tag_filter.change(
                filter_nodes,
                inputs=[tag_filter],
                outputs=[nodes_dataframe]
            )
        
        # 4. AI 아이디어 생성 탭
        with gr.Tab("🚀 AI 아이디어 생성"):
            gr.Markdown("### 공모전 정보를 입력하여 AI 아이디어를 생성하세요")
            
            # 공모전 정보 섹션
            gr.Markdown("#### 🏆 공모전 정보")
            contest_title = gr.Textbox(label="공모전 제목", placeholder="참가할 공모전 제목을 입력하세요")
            contest_theme = gr.Textbox(label="공모전 주제", placeholder="공모전의 주요 주제를 입력하세요")
            contest_description = gr.Textbox(
                label="공모전 설명",
                lines=3,
                placeholder="공모전에 대한 상세 설명을 입력하세요"
            )
            contest_context = gr.Textbox(
                label="공모전 맥락 (선택사항)",
                lines=2,
                placeholder="공모전의 배경이나 추가적인 맥락 정보를 입력하세요 (선택사항)"
            )
            
            # API 키 입력
            gr.Markdown("#### 🔑 API 설정")
            api_key_input = gr.Textbox(
                label="OpenAI API Key",
                type="password",
                placeholder="OpenAI API 키를 입력하세요"
            )
            
            # 아이디어 생성 섹션
            gr.Markdown("#### 🤖 아이디어 생성하기")
            with gr.Row():
                chatgpt_btn = gr.Button("🤖 ChatGPT로 아이디어 생성", variant="primary", size="lg")
                gemini_btn = gr.Button("💎 Gemini로 생성 (준비중)", variant="secondary", size="lg", interactive=False)
            
            idea_generation_status = gr.Textbox(label="생성 상태", interactive=False)
            
            # 이벤트 연결
            chatgpt_btn.click(
                generate_idea_with_chatgpt,
                inputs=[contest_title, contest_theme, contest_description, contest_context, api_key_input],
                outputs=[idea_generation_status]
            )
            
            gemini_btn.click(
                generate_idea_with_gemini,
                inputs=[contest_title, contest_theme, contest_description, contest_context, api_key_input],
                outputs=[idea_generation_status]
            )
        
        # 5. 생성된 아이디어 확인하기 탭
        with gr.Tab("💭 생성된 아이디어 확인하기"):
            gr.Markdown("### AI로 생성된 아이디어를 확인하고 상세 내용을 볼 수 있습니다")
            
            with gr.Row():
                refresh_ideas_btn = gr.Button("🔄 새로고침", variant="secondary")
            
            # 아이디어 목록
            ideas_dataframe = gr.Dataframe(
                value=get_ideas_dataframe(),
                headers=["AI 이름", "아이디어 제목", "아이디어 개요"],
                interactive=True,
                elem_id="ideas_table"
            )
            
            # 선택된 아이디어 상세 정보
            gr.Markdown("#### 📋 선택된 아이디어 상세 정보")
            gr.Markdown("*위 테이블에서 행을 클릭하면 해당 아이디어의 상세 정보가 표시됩니다.*")
            
            with gr.Accordion("🎯 아이디어 상세 정보", open=True):
                selected_title = gr.Textbox(label="아이디어 제목", interactive=False)
                contest_info_display = gr.Textbox(label="공모전 정보", lines=4, interactive=False)
                problem_display = gr.Textbox(label="문제 의식", lines=3, interactive=False)
                solution_display = gr.Textbox(label="솔루션 해결 방안", lines=4, interactive=False)
                implementation_display = gr.Textbox(label="구현 방안", lines=3, interactive=False)
                expected_effect_display = gr.Textbox(label="기대 효과", lines=3, interactive=False)
            
            # 이벤트 연결
            refresh_ideas_btn.click(
                refresh_ideas,
                outputs=[ideas_dataframe]
            )
            
            ideas_dataframe.select(
                get_idea_details,
                inputs=[ideas_dataframe],
                outputs=[selected_title, contest_info_display, problem_display, solution_display, implementation_display, expected_effect_display]
            )

# 앱 실행
if __name__ == "__main__":
    app.launch(share=True, debug=True)