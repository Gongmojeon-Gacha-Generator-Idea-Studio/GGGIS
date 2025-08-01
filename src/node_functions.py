import pandas as pd
import src.data_manager as dm


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

    dm.nodes_data.append(sample_node)
    dm.save_nodes()

    return "파일 분석이 완료되어 노드가 생성되었습니다!"


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


def create_node(title, solution, tags):
    """사용자 입력으로 새 노드 생성"""
    print(
        f"[DEBUG] create_node 호출됨 - title: {title}, solution 길이: {len(solution) if solution else 0}, tags: {tags}"
    )

    if not title or not solution:
        return (
            "❌ 프로젝트 제목과 솔루션을 모두 입력해주세요.",
            title,
            solution,
            "",
            tags,
            "",
        )

    # 태그를 리스트로 변환
    tags_list = [tag.strip() for tag in tags.split(",") if tag.strip()] if tags else []

    # 키워드 필수 검증
    if not tags_list:
        return "❌ 키워드를 최소 1개 이상 입력해주세요!", title, solution, "", tags, ""

    print(f"[DEBUG] 태그 리스트 변환 완료: {tags_list}")

    new_node = {
        "title": title,
        "solution": solution,
        "tags": tags_list,
        "source": "직접 입력",
    }

    print(f"[DEBUG] 새 노드 생성: {new_node}")
    print(f"[DEBUG] 현재 nodes_data 길이: {len(dm.nodes_data)}")

    dm.nodes_data.append(new_node)
    print(f"[DEBUG] 노드 추가 후 nodes_data 길이: {len(dm.nodes_data)}")

    dm.save_nodes()

    # 성공시 모든 필드 초기화
    return "✅ 새 노드가 성공적으로 생성되었습니다!", "", "", "", "", ""


def get_nodes_dataframe(filter_tag=""):
    """저장된 노드들을 데이터프레임으로 변환"""
    if not dm.nodes_data:
        return pd.DataFrame()

    # 필터링된 노드들
    filtered_nodes = []
    for node in dm.nodes_data:
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
    for node in dm.nodes_data:
        all_tags.update(node.get("tags", []))
    return [""] + sorted(list(all_tags))


def refresh_nodes():
    """노드 목록 새로고침"""
    dm.load_nodes()
    return get_nodes_dataframe(), get_all_tags()
