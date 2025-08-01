import json
import os

# 전역 변수
nodes_data = []
ideas_data = []


def save_nodes():
    """노드 데이터를 JSON 파일로 저장"""
    try:
        # data 디렉토리 생성
        os.makedirs("data", exist_ok=True)

        with open("data/nodes_data.json", "w", encoding="utf-8") as f:
            json.dump(nodes_data, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"[ERROR] save_nodes 실패: {e}")
        raise e


def save_ideas():
    """아이디어 데이터를 JSON 파일로 저장"""
    try:
        # data 디렉토리 생성
        os.makedirs("data", exist_ok=True)

        with open("data/ideas_data.json", "w", encoding="utf-8") as f:
            json.dump(ideas_data, f, ensure_ascii=False, indent=2)

    except Exception as e:
        print(f"[ERROR] save_ideas 실패: {e}")
        raise e


def load_nodes():
    """저장된 노드 데이터 불러오기"""
    global nodes_data
    if os.path.exists("data/nodes_data.json"):
        try:
            with open("data/nodes_data.json", "r", encoding="utf-8") as f:
                nodes_data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            nodes_data = []
    else:
        nodes_data = []


def load_ideas():
    """저장된 아이디어 데이터 불러오기"""
    global ideas_data
    if os.path.exists("data/ideas_data.json"):
        try:
            with open("data/ideas_data.json", "r", encoding="utf-8") as f:
                ideas_data = json.load(f)
        except (json.JSONDecodeError, ValueError):
            ideas_data = []
    else:
        ideas_data = []


def initialize_data():
    """앱 시작 시 데이터 초기화"""
    load_nodes()
    load_ideas()


def get_ideas_data():
    """ideas_data 반환"""
    return ideas_data


def get_nodes_data():
    """nodes_data 반환"""
    return nodes_data
