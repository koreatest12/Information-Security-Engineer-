import json
import random
import os

def generate_bulk_data(count=50):
    data = []
    colors = ["blue", "green", "red", "black", "navy"]
    
    for i in range(1, count + 1):
        item = {
            # ID를 001, 002 형식으로 지정
            "id": f"video_{i:03d}",
            # 텍스트 내용 자동 생성
            "text": f"Batch Process\nSequence #{i}",
            # 색상 랜덤 지정
            "color": random.choice(colors),
            # 길이 랜덤 (3초~5초)
            "duration": random.randint(3, 5)
        }
        data.append(item)

    # data 폴더가 없으면 생성
    os.makedirs("data", exist_ok=True)
    
    # JSON 파일 쓰기
    file_path = "data/video_list.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Successfully generated {count} items in {file_path}")

if __name__ == "__main__":
    generate_bulk_data(50) # 여기서 숫자만 바꾸면 100개, 1000개 생성 가능
