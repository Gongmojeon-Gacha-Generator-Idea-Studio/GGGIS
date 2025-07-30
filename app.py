import gradio as gr
import json
import os
from typing import List, Dict, Any

# 노드 데이터를 저장할 전역 변수
nodes_data = []

def save_nodes():
    """노드 데이터를 JSON 파일로 저장"""
    with open('nodes_data.json', 'w', encoding='utf-8') as f:
        json.dump(nodes_data, f, ensure_ascii=False, indent=2)

def load_nodes():
    """저장된 노드 데이터 불러오기"""
    global nodes_data
    if os.path.exists('nodes_data.json'):
        with open('nodes_data.json', 'r', encoding='utf-8') as f:
            nodes_data = json.load(f)

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
    # 현재는 샘플 노드 생성
    sample_node = {
        "title": "AI 분석된 프로젝트",
        "competition": "업로드 파일에서 추출",
        "problem": "파일에서 분석된 문제점",
        "solution": "파일에서 추출된 솔루션",
        "features": ["기능1", "기능2", "기능3"],
        "weaknesses": "분석된 약점",
        "links": "",
        "source": "파일 업로드"
    }
    
    nodes_data.append(sample_node)
    save_nodes()
    
    return "파일 분석이 완료되어 노드가 생성되었습니다!"

# 2. 노드 입력하기 탭 함수들
def create_node(title, competition, problem, solution, features, weaknesses, links):
    """사용자 입력으로 새 노드 생성"""
    if not title or not competition or not problem or not solution:
        return "필수 항목을 모두 입력해주세요."
    
    # 핵심 기능을 리스트로 변환
    features_list = [f.strip() for f in features.split(',') if f.strip()]
    
    new_node = {
        "title": title,
        "competition": competition,
        "problem": problem,
        "solution": solution,
        "features": features_list,
        "weaknesses": weaknesses if weaknesses else "없음",
        "links": links if links else "없음",
        "source": "직접 입력"
    }
    
    nodes_data.append(new_node)
    save_nodes()
    
    return "새 노드가 성공적으로 생성되었습니다!"

# 3. 내 노드 확인하기 탭 함수들
def get_nodes_display():
    """저장된 노드들을 표시용 텍스트로 변환"""
    if not nodes_data:
        return "아직 생성된 노드가 없습니다."
    
    display_text = ""
    for i, node in enumerate(nodes_data, 1):
        display_text += f"""
### 📌 노드 {i}: {node['title']}
**공모전명:** {node['competition']}  
**데이터 소스:** {node['source']}

<details>
<summary>상세 정보 보기</summary>

**문제점:** {node['problem']}

**솔루션:** {node['solution']}

**핵심 기능:**
{chr(10).join([f"• {feature}" for feature in node['features']])}

**기술적/현실적 약점:** {node['weaknesses']}

**관련 링크:** {node['links']}

</details>

---
"""
    
    return display_text

def refresh_nodes():
    """노드 목록 새로고침"""
    load_nodes()
    return get_nodes_display()

# 4. AI 아이디어 생성 탭 함수들
def add_team_member(member_code, current_members):
    """팀원 추가"""
    if not member_code:
        return current_members, "팀원 코드를 입력해주세요."
    
    # TODO: 실제 팀원 정보 조회 로직 구현
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
    
    # TODO: 실제 ChatGPT API 연동
    sample_idea = f"""
## 🤖 ChatGPT 생성 아이디어

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
기존 환경 모니터링 시스템과 달리, 개인 사용자도 쉽게 참여할 수 있는 접근성과 AI 예측 기능을 결합
"""
    
    return sample_idea

def generate_idea_gemini(competition_name, is_development, category, team_members):
    """Gemini로 아이디어 생성"""
    if not competition_name:
        return "공모전 이름을 입력해주세요."
    
    # TODO: 실제 Gemini API 연동
    sample_idea = f"""
## 🎯 Gemini 생성 아이디어

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
단순한 아이디어 제안을 넘어서, 실제 실행 가능한 프로젝트로 연결하는 구조적 접근
"""
    
    return sample_idea

# 앱 시작 시 노드 데이터 로드
load_nodes()

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
                competition_input = gr.Textbox(label="2. 참가 공모전명", placeholder="참가한 공모전 이름을 입력하세요")
                problem_input = gr.Textbox(
                    label="3. 이 프로젝트는 어떤 문제를 해결하나요?",
                    lines=3,
                    placeholder="해결하고자 한 문제를 구체적으로 설명해주세요"
                )
                solution_input = gr.Textbox(
                    label="4. 당신의 솔루션은 무엇인가요? (주요 대상을 포함하여 작성해주세요.)",
                    lines=3,
                    placeholder="솔루션과 주요 대상을 포함하여 설명해주세요"
                )
                features_input = gr.Textbox(
                    label="5. 핵심 기능을 2~4개 적어주세요. (사용한 기술을 포함하여 작성해주세요.)",
                    lines=3,
                    placeholder="핵심 기능을 쉼표로 구분하여 입력하세요 (예: 실시간 데이터 처리, AI 기반 추천 시스템, 모바일 앱 개발)"
                )
                weaknesses_input = gr.Textbox(
                    label="6. 기술적/현실적인 약점이 있다면 무엇인가요? (선택)",
                    lines=2,
                    placeholder="약점이나 한계점이 있다면 입력하세요"
                )
                links_input = gr.Textbox(
                    label="7. notion/figma/slides 링크 (선택)",
                    placeholder="관련 링크가 있다면 입력하세요"
                )
            
            create_btn = gr.Button("✨ 노드 생성하기", variant="primary", size="lg")
            create_status = gr.Textbox(label="생성 결과", interactive=False)
            
            # 이벤트 연결
            create_btn.click(
                create_node,
                inputs=[title_input, competition_input, problem_input, solution_input, features_input, weaknesses_input, links_input],
                outputs=[create_status]
            )
        
        # 3. 내 노드 확인하기 탭
        with gr.Tab("📋 내 노드 확인하기"):
            gr.Markdown("### 생성된 모든 노드를 확인하고 관리하세요")
            
            refresh_btn = gr.Button("🔄 새로고침", variant="secondary")
            nodes_display = gr.Markdown(get_nodes_display())
            
            # 이벤트 연결
            refresh_btn.click(
                refresh_nodes,
                outputs=[nodes_display]
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

# 앱 실행ㅋ
if __name__ == "__main__":
    app.launch(share=True, debug=True) 