import pandas as pd
import src.data_manager as dm
from src.openai_client import create_openai_client

try:
    from gradio import SelectData
except ImportError:
    # Gradio 버전이 낮은 경우
    SelectData = None


def generate_idea_with_chatgpt(
    contest_title, contest_theme, contest_description, contest_context=""
):
    """ChatGPT를 이용해 아이디어 생성"""
    if not contest_title or not contest_theme:
        return "공모전 제목과 주제를 입력해주세요."

    try:
        # OpenAI 클라이언트 생성 (.env에서 API 키 자동 로드)
        client = create_openai_client()

        # 공모전 정보 구성
        contest_info = {
            "title": contest_title,
            "theme": contest_theme,
            "description": contest_description,
            "context": contest_context,
        }

        # 아이디어 생성
        generated_idea = client.generate_idea(contest_info, dm.nodes_data)

        if "error" in generated_idea:
            return generated_idea["error"]

        # 생성된 아이디어를 ideas_data에 저장
        print(f"[DEBUG] 아이디어 생성 완료: {generated_idea.get('title', 'No Title')}")
        print(f"[DEBUG] 저장 전 ideas_data 길이: {len(dm.ideas_data)}")

        dm.ideas_data.append(generated_idea)
        print(f"[DEBUG] 저장 후 ideas_data 길이: {len(dm.ideas_data)}")

        try:
            dm.save_ideas()
            print(f"[DEBUG] JSON 저장 완료")
        except Exception as save_error:
            print(f"[DEBUG] JSON 저장 실패: {save_error}")
            return f"아이디어 생성은 완료되었지만 저장 중 오류가 발생했습니다: {save_error}"

        return f"아이디어 '{generated_idea['title']}'가 성공적으로 생성되었습니다!"

    except Exception as e:
        return f"아이디어 생성 중 오류가 발생했습니다: {str(e)}"


def get_ideas_dataframe():
    """생성된 아이디어들을 데이터프레임으로 변환"""
    if not dm.ideas_data:
        return pd.DataFrame(columns=["AI 이름", "아이디어 제목", "아이디어 개요"])

    df_data = []
    for idea in dm.ideas_data:
        df_data.append(
            {
                "AI 이름": idea.get("ai_name", "Unknown"),
                "아이디어 제목": idea.get("title", "제목 없음"),
                "아이디어 개요": idea.get("overview", "개요 없음"),
            }
        )

    return pd.DataFrame(df_data)


def get_idea_details(selection_data):
    """선택된 아이디어의 상세 정보 반환"""
    try:
        # 디버깅: selection_data의 구조 확인
        print(f"[DEBUG] selection_data 타입: {type(selection_data)}")
        print(f"[DEBUG] selection_data 내용: {selection_data}")

        # selection_data가 None이거나 비어있는 경우
        if selection_data is None:
            return "아이디어를 선택해주세요.", "", "", "", "", ""

        # Gradio dataframe.select()는 SelectData 객체를 전달함
        selected_index = None

        # SelectData 객체인 경우 (Gradio v4+)
        if SelectData and isinstance(selection_data, SelectData):
            if hasattr(selection_data, "index") and isinstance(
                selection_data.index, (list, tuple)
            ):
                selected_index = selection_data.index[0]  # 행 인덱스
                print(f"[DEBUG] SelectData 객체에서 추출한 인덱스: {selected_index}")
            else:
                print(f"[DEBUG] SelectData 객체에서 index 속성을 찾을 수 없음")

        # hasattr로 index 속성 확인 (일반적인 경우)
        elif hasattr(selection_data, "index"):
            if isinstance(selection_data.index, (list, tuple)):
                selected_index = selection_data.index[0]  # 행 인덱스
                print(
                    f"[DEBUG] index 속성(list/tuple)에서 추출한 인덱스: {selected_index}"
                )
            elif (
                hasattr(selection_data.index, "__len__")
                and len(selection_data.index) > 0
            ):
                selected_index = selection_data.index[0]
                print(f"[DEBUG] index 속성(pandas)에서 추출한 인덱스: {selected_index}")

        # 딕셔너리 형태인 경우
        elif isinstance(selection_data, dict):
            if "index" in selection_data:
                if isinstance(selection_data["index"], (list, tuple)):
                    selected_index = selection_data["index"][0]
                else:
                    selected_index = selection_data["index"]
                print(f"[DEBUG] 딕셔너리에서 추출한 인덱스: {selected_index}")

        # 정수 값이 직접 전달된 경우
        elif isinstance(selection_data, (int, float)):
            selected_index = int(selection_data)
            print(f"[DEBUG] 직접 전달된 인덱스: {selected_index}")

        # 인덱스를 찾지 못한 경우
        if selected_index is None:
            print(f"[DEBUG] 인덱스를 찾을 수 없음")
            return "아이디어를 선택해주세요.", "", "", "", "", ""

    except Exception as e:
        print(f"[DEBUG] get_idea_details 에러: {e}")
        print(f"[DEBUG] selection_data: {selection_data}")
        return "아이디어 선택 중 오류가 발생했습니다.", "", "", "", "", ""

    if selected_index >= len(dm.ideas_data):
        return "선택된 아이디어를 찾을 수 없습니다.", "", "", "", "", ""

    idea = dm.ideas_data[selected_index]

    title = idea.get("title", "제목 없음")
    problem = idea.get("problem", "문제의식 정보가 없습니다.")
    solution = idea.get("solution", "솔루션 정보가 없습니다.")
    implementation = idea.get("implementation", "구현방안 정보가 없습니다.")
    expected_effect = idea.get("expected_effect", "기대효과 정보가 없습니다.")

    # 공모전 정보
    contest_info = idea.get("contest_info", {})
    contest_details = f"""공모전 제목: {contest_info.get('title', 'N/A')}
주제: {contest_info.get('theme', 'N/A')}
설명: {contest_info.get('description', 'N/A')}
맥락: {contest_info.get('context', 'N/A')}"""

    return title, contest_details, problem, solution, implementation, expected_effect


def get_idea_details_by_index(selected_index):
    """인덱스를 직접 받아서 아이디어 상세 정보 반환"""
    try:
        print(f"[DEBUG] get_idea_details_by_index 호출됨, 인덱스: {selected_index}")
        print(f"[DEBUG] 현재 ideas_data 길이: {len(dm.ideas_data)}")

        if selected_index is None or selected_index < 0:
            return "올바르지 않은 인덱스입니다.", "", "", "", "", ""

        if selected_index >= len(dm.ideas_data):
            return "선택된 아이디어를 찾을 수 없습니다.", "", "", "", "", ""

        idea = dm.ideas_data[selected_index]
        print(f"[DEBUG] 선택된 아이디어: {idea.get('title', 'No Title')}")

        title = idea.get("title", "제목 없음")
        problem = idea.get("problem", "문제의식 정보가 없습니다.")
        solution = idea.get("solution", "솔루션 정보가 없습니다.")
        implementation = idea.get("implementation", "구현방안 정보가 없습니다.")
        expected_effect = idea.get("expected_effect", "기대효과 정보가 없습니다.")

        # 공모전 정보
        contest_info = idea.get("contest_info", {})
        contest_details = f"""공모전 제목: {contest_info.get('title', 'N/A')}
주제: {contest_info.get('theme', 'N/A')}
설명: {contest_info.get('description', 'N/A')}
맥락: {contest_info.get('context', 'N/A')}"""

        return (
            title,
            contest_details,
            problem,
            solution,
            implementation,
            expected_effect,
        )

    except Exception as e:
        print(f"[ERROR] get_idea_details_by_index 에러: {e}")
        return "아이디어 정보 로드 중 오류가 발생했습니다.", "", "", "", "", ""


def refresh_ideas():
    """아이디어 목록 새로고침"""
    dm.load_ideas()
    return get_ideas_dataframe()


def clear_ideas():
    """모든 아이디어 삭제"""
    dm.ideas_data = []
    dm.save_ideas()
    return get_ideas_dataframe()


def delete_idea(selected_index):
    """선택된 아이디어 삭제"""
    if selected_index is None or selected_index >= len(dm.ideas_data):
        return "삭제할 아이디어를 선택해주세요.", get_ideas_dataframe()

    deleted_idea = dm.ideas_data.pop(selected_index)
    dm.save_ideas()

    return (
        f"아이디어 '{deleted_idea.get('title', '제목 없음')}'가 삭제되었습니다.",
        get_ideas_dataframe(),
    )


# 추가: Gemini API 연동을 위한 준비 함수
def generate_idea_with_gemini(
    contest_title, contest_theme, contest_description, contest_context=""
):
    """Gemini를 이용해 아이디어 생성 (향후 구현 예정)"""
    return "Gemini API 연동은 아직 구현되지 않았습니다."
