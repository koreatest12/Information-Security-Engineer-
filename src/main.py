import sys
import os

# 버전 호환성 이슈 해결을 위한 설정
try:
    from moviepy.editor import ColorClip, TextClip, CompositeVideoClip
except ImportError:
    # 만약 v2.0이 설치되었다면 경로가 다를 수 있음 (requirements.txt로 방지함)
    print("CRITICAL ERROR: Please install moviepy==1.0.3 using requirements.txt")
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

        # 2. 텍스트 생성 (ImageMagick 연동)
        # method='caption'은 자동 줄바꿈을 지원합니다.
        # stroke_color와 stroke_width로 가독성을 높입니다.
        txt_clip = TextClip(
            text, 
            fontsize=70, 
            color='white', 
            size=(1000, None), 
            method='caption',
            stroke_color='black', 
            stroke_width=2
        )
        txt_clip = txt_clip.set_position('center').set_duration(duration_sec)
        
        # 3. 합성
        final_clip = CompositeVideoClip([bg_clip, txt_clip])

        # 4. 저장
        output_dir = "output"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"{vid_id}.mp4")
        
        # codec='libx264'는 가장 호환성이 좋은 인코딩 방식입니다.
        # audio=False: 오디오가 없으므로 렌더링 속도 향상
        final_clip.write_videofile(output_path, fps=24, codec='libx264', audio=False, logger=None)
        print(f"✅ Completed: {output_path}")

    except Exception as e:
        print(f"❌ Error processing {vid_id}: {str(e)}")
        # 에러가 나도 프로세스를 죽이지 않고 로그만 남길 경우:
        # sys.exit(1) # 필요 시 주석 해제

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python src/main.py <id> <text> <color> <duration>")
        sys.exit(1)

    render_video(sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]))
