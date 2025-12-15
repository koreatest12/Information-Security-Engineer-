import sys
import os

# 라이브러리 로드 (에러 발생 시 시스템 에러 메시지 출력)
try:
    from moviepy.editor import ColorClip, TextClip, CompositeVideoClip
except ImportError as e:
    print(f"::error::Library Import Failed: {e}")
    sys.exit(1)

def render_video(vid_id, text, color_name, duration_sec):
    print(f"🎬 Starting render: {vid_id}")
    
    # 색상 매핑
    colors = {
        "blue": (0, 0, 150),
        "green": (0, 100, 0),
        "red": (150, 0, 0),
        "black": (20, 20, 20),
        "navy": (0, 0, 80)
    }
    bg_color = colors.get(color_name, (50, 50, 50))

    try:
        # 1. 배경 생성
        bg_clip = ColorClip(size=(1280, 720), color=bg_color, duration=duration_sec)

        # 2. 폰트 파일 확인 (워크플로우에서 다운로드한 폰트 사용)
        font_path = "NanumGothic.ttf" 
        if not os.path.exists(font_path):
            # 폰트가 없으면 기본값(None)으로 시도하지만 경고 출력
            print("::warning::Font file not found. Using default font.")
            font_path = None

        # 3. 텍스트 생성
        # method='caption' + size 지정 = 자동 줄바꿈
        txt_clip = TextClip(
            text, 
            fontsize=70, 
            color='white', 
            font=font_path,
            size=(1000, None), 
            method='caption'
        )
        txt_clip = txt_clip.set_position('center').set_duration(duration_sec)
        
        # 4. 합성
        final_clip = CompositeVideoClip([bg_clip, txt_clip])

        # 5. 저장
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{vid_id}.mp4")
        
        # fps=24, 코덱 libx264 (가장 안정적)
        final_clip.write_videofile(output_path, fps=24, codec='libx264', audio=False, logger=None)
        print(f"✅ Completed: {output_path}")

    except Exception as e:
        print(f"::error::Error processing {vid_id}: {str(e)}")
        # GitHub Actions에서 에러로 인식하도록 exit code 1 반환
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python src/main.py <id> <text> <color> <duration>")
        sys.exit(1)

    render_video(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]))
