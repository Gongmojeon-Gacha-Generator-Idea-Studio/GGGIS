import json
import os
from typing import List, Dict, Any

# 전역 변수
nodes_data = []
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

def initialize_data():
    """앱 시작 시 데이터 초기화"""
    load_nodes()
    load_ideas()
