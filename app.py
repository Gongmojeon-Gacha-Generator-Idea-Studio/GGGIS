import gradio as gr
import json
import os
import pandas as pd
from typing import List, Dict, Any

# 노드 데이터를 저장할 전역 변수
nodes_data = []
# 아이디어 데이터를 저장할 전역 변수
ideas_data = []

def save_nodes():
    """노드 데이터를 JSON 파일로 저장"""
    with open('nodes_data.json', 'w', encoding='utf-8') as f:
        json.dump(nodes_data, f, ensure_ascii=False, indent=2)

def save_ideas():
    """아이디어 데이터를 JSON 파일로 저장"""
    with open('ideas_data.json', 'w', encoding='utf-8') as f:
        json.dump(ideas_data, f, ensure_ascii=False, indent=2)

def load_nodes():
    """저장된 노드 데이터 불러오기"""
    global nodes_data
    if os.path.exists('nodes_data.json'):
        try:
            with open('nodes_data.json', 'r', encoding='utf-8') as f:
                nodes_data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            nodes_data = []
            print("nodes_data.json 파일이 손상되었거나 비어있습니다. 새로 시작합니다.")
    else:
        nodes_data = []

def load_ideas():
    """저장된 아이디어 데이터 불러오기"""
    global ideas_data
    if os.path.exists('ideas_data.json'):
        try:
            with open('ideas_data.json', 'r', encoding='utf-8') as f:
                ideas_data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            ideas_data = []
            print("ideas_data.json 파일이 손상되었거나 비어있습니다. 새로 시작합니다.")
    else:
        ideas_data = []

# 1. 포폴 업로드 탭 함수들
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
        "source": "파일 업로드"
    }
    
    nodes_data.append(sample_node)
    save_nodes()
    
    return "파일 분석이 완료되어 노드가 생성되었습니다!"

# 2. 노드 입력하기 탭 함수들
def add_keyword(keyword, current_tags):
    """키워드 추가"""
    if not keyword:
        return current_tags, "키워드를 입력해주세요."
    
    if current_tags:
        tags_list = [tag.strip() for tag in current_tags.split(',') if tag.strip()]
    else:
        tags_list = []
    
    if keyword not in tags_list:
        tags_list.append(keyword)
        updated_tags = ', '.join(tags_list)
        return updated_tags, f"'{keyword}' 키워드가 추가되었습니다."
    else:
        return current_tags, "이미 존재하는 키워드입니다."

def create_node(title, solution, tags):
    """사용자 입력으로 새 노드 생성"""
    if not title or not solution:
        return "프로젝트 제목과 솔루션을 모두 입력해주세요."
    
    # 태그를 리스트로 변환
    tags_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
    
    new_node = {
        "title": title,
        "solution": solution,
        "tags": tags_list,
        "source": "직접 입력"
    }
    
    nodes_data.append(new_node)
    save_nodes()
    
    return "새 노드가 성공적으로 생성되었습니다!"

# 3. 내 노드 확인하기 탭 함수들
def get_nodes_dataframe(filter_tag=""):
    """저장된 노드들을 데이터프레임으로 변환"""
    if not nodes_data:
        return pd.DataFrame()
    
    # 필터링된 노드들
    filtered_nodes = []
    for node in nodes_data:
        if not filter_tag or filter_tag in node.get('tags', []):
            filtered_nodes.append({
                "프로젝트 제목": node['title'],
                "솔루션 소개": node['solution'][:100] + "..." if len(node['solution']) > 100 else node['solution'],
                "태그": ', '.join(node.get('tags', [])),
                "출처": node.get('source', '직접 입력')
            })
    
    return pd.DataFrame(filtered_nodes)

def filter_nodes(filter_tag):
    """태그로 노드 필터링"""
    return get_nodes_dataframe(filter_tag)

def get_all_tags():
    """모든 노드의 태그 목록 반환"""
    all_tags = set()
    for node in nodes_data:
        all_tags.update(node.get('tags', []))
    return [""] + sorted(list(all_tags))

# 4. AI 아이디어 생성 탭 함수들
def add_team_member(member_code, current_members):
    """팀원 추가"""
    if not member_code:
        return current_members, "팀원 코드를 입력해주세요."
    
    new_member = f"👤 {member_code} (닉네임)"
    
    if current_members:
        updated_members = current_members + f"\n{new_member}"
    else:
        updated_members = new_member
    
    return updated_members, "팀원이 추가되었습니다!"

def generate_idea_chatgpt(competition_name, is_development, category, team_members):
    """ChatGPT로 아이디어 생성"""
    if not competition_name:
        return "공모전 이름을 입력해주세요."
    
    idea_content = f"""## 🤖 ChatGPT 생성 아이디어

**공모전:** {competition_name}
**개발 여부:** {is_development}
**분야:** {category}

### 아이디어: "스마트 환경 모니터링 시스템"

**핵심 컨셉:**
당신의 노드에서 분석한 IoT와 데이터 분석 경험을 활용하여, 실시간 환경 데이터를 수집하고 예측 분석을 제공하는 시스템을 제안합니다.

**주요 기능:**
1. 다중 센서 기반 환경 데이터 수집
2. AI 기반 환경 변화 예측
3. 실시간 알림 및 대응 방안 제시
4. 커뮤니티 기반 환경 개선 참여 플랫폼

**활용된 노드:**
• 이전 IoT 프로젝트의 센서 활용 경험
• 데이터 분석 및 시각화 기술
• 웹/앱 개발 경험

**차별점:**
기존 환경 모니터링 시스템과 달리, 개인 사용자도 쉽게 참여할 수 있는 접근성과 AI 예측 기능을 결합"""
    
    # 아이디어 저장
    new_idea = {
        "title": "스마트 환경 모니터링 시스템",
        "competition": competition_name,
        "generator": "ChatGPT",
        "summary": "IoT와 데이터 분석을 활용한 실시간 환경 모니터링 및 예측 시스템",
        "content": idea_content,
        "category": category,
        "development_type": is_development
    }
    
    ideas_data.append(new_idea)
    save_ideas()
    
    return idea_content

def generate_idea_gemini(competition_name, is_development, category, team_members):
    """Gemini로 아이디어 생성"""
    if not competition_name:
        return "공모전 이름을 입력해주세요."
    
    idea_content = f"""## 🎯 Gemini 생성 아이디어

**공모전:** {competition_name}
**개발 여부:** {is_development}
**분야:** {category}

### 아이디어: "협업 기반 지역 문제 해결 플랫폼"

**핵심 컨셉:**
지역 주민들이 직면한 실질적 문제를 발굴하고, 다양한 배경의 사람들이 협업하여 해결책을 찾는 플랫폼입니다.

**주요 기능:**
1. 지역 문제 제보 및 검증 시스템
2. 스킬 기반 팀 매칭 알고리즘
3. 프로젝트 진행 관리 및 리소스 공유
4. 성과 측정 및 영향력 분석 도구

**활용된 노드:**
• 커뮤니티 플랫폼 개발 경험
• 사용자 경험 설계 역량
• 데이터 기반 의사결정 경험

**혁신성:**
단순한 아이디어 제안을 넘어서, 실제 실행 가능한 프로젝트로 연결하는 구조적 접근"""
    
    # 아이디어 저장
    new_idea = {
        "title": "협업 기반 지역 문제 해결 플랫폼",
        "competition": competition_name,
        "generator": "Gemini",
        "summary": "지역 주민과 다양한 배경의 사람들이 협업하여 실질적 문제를 해결하는 플랫폼",
        "content": idea_content,
        "category": category,
        "development_type": is_development
    }
    
    ideas_data.append(new_idea)
    save_ideas()
    
    return idea_content

# 5. 생성된 아이디어 확인하기 탭 함수들
def get_ideas_display():
    """생성된 아이디어들을 표시용으로 변환"""
    if not ideas_data:
        return "아직 생성된 아이디어가 없습니다."
    
    display_items = []
    for i, idea in enumerate(ideas_data):
        card = f"""
<div style="border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin: 8px 0; background: #f9f9f9;">
    <h3>💡 {idea['title']}</h3>
    <p><strong>생성 AI:</strong> {idea['generator']} | <strong>공모전:</strong> {idea['competition']}</p>
    <p><strong>요약:</strong> {idea['summary']}</p>
    <details>
        <summary>자세한 내용 보기</summary>
        <div style="margin-top: 12px; padding: 12px; background: white; border-radius: 4px;">
            {idea['content'].replace('\n', '<br>')}
        </div>
    </details>
</div>
"""
        display_items.append(card)
    
    return "".join(display_items)

def refresh_ideas():
    """아이디어 목록 새로고침"""
    load_ideas()
    return get_ideas_display()

# 앱 시작 시 데이터 로드
load_nodes()
load_ideas()

# Gradio 인터페이스 구성
with gr.Blocks(title="노드폴리오", theme=gr.themes.Soft()) as app:
    
    # 헤더
    gr.Markdown("# 🔗 노드폴리오")
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
                lambda: [get_nodes_dataframe(), get_all_tags()],
                outputs=[nodes_dataframe, tag_filter]
            )
            
            tag_filter.change(
                filter_nodes,
                inputs=[tag_filter],
                outputs=[nodes_dataframe]
            )
        
        # 4. AI 아이디어 생성 탭
        with gr.Tab("🚀 AI 아이디어 생성"):
            gr.Markdown("### 공모전 정보와 팀원을 설정하여 AI 아이디어를 생성하세요")
            
            # 공모전 정보 섹션
            gr.Markdown("#### 🏆 공모전 정보")
            with gr.Row():
                comp_name = gr.Textbox(label="공모전 이름", placeholder="참가할 공모전 이름을 입력하세요")
                is_dev = gr.Dropdown(
                    label="개발 여부",
                    choices=["개발", "기획만", "혼합"],
                    value="개발"
                )
            category = gr.Textbox(label="분야/카테고리", placeholder="예: AI, 웹개발, 모바일, IoT, 데이터 분석 등")
            
            # 팀원 정보 섹션
            gr.Markdown("#### 👥 함께하는 사람")
            with gr.Row():
                member_code_input = gr.Textbox(label="팀원 코드", placeholder="팀원의 코드를 입력하세요")
                add_member_btn = gr.Button("➕ 팀원 추가", variant="secondary")
            
            team_members_display = gr.Textbox(label="현재 팀원", interactive=False, lines=3)
            member_add_status = gr.Textbox(label="추가 상태", interactive=False)
            
            # 아이디어 생성 섹션
            gr.Markdown("#### 🤖 아이디어 생성하기")
            with gr.Row():
                chatgpt_btn = gr.Button("🤖 ChatGPT로 생성", variant="primary", size="lg")
                gemini_btn = gr.Button("💎 Gemini로 생성", variant="primary", size="lg")
            
            idea_output = gr.Markdown(label="생성된 아이디어")
            
            # 이벤트 연결
            add_member_btn.click(
                add_team_member,
                inputs=[member_code_input, team_members_display],
                outputs=[team_members_display, member_add_status]
            )
            
            chatgpt_btn.click(
                generate_idea_chatgpt,
                inputs=[comp_name, is_dev, category, team_members_display],
                outputs=[idea_output]
            )
            
            gemini_btn.click(
                generate_idea_gemini,
                inputs=[comp_name, is_dev, category, team_members_display],
                outputs=[idea_output]
            )
        
        # 5. 생성된 아이디어 확인하기 탭
        with gr.Tab("💭 생성된 아이디어 확인하기"):
            gr.Markdown("### ChatGPT와 Gemini로 생성된 아이디어를 확인하세요")
            
            refresh_ideas_btn = gr.Button("🔄 새로고침", variant="secondary")
            ideas_display = gr.HTML(get_ideas_display())
            
            # 이벤트 연결
            refresh_ideas_btn.click(
                refresh_ideas,
                outputs=[ideas_display]
            )

# 앱 실행
if __name__ == "__main__":
    app.launch(share=True, debug=True)