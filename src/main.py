import sys
import os
from moviepy.editor import ColorClip, TextClip, CompositeVideoClip

def render_video(vid_id, text, color_name, duration_sec):
    # 색상 매핑 (안전장치)
    colors = {"blue": (0, 0, 150), "green": (0, 150, 0), "red": (150, 0, 0)}
    bg_color = colors.get(color_name, (50, 50, 50))

    # 1. 배경 생성
    bg_clip = ColorClip(size=(1280, 720), color=bg_color, duration=duration_sec)

    # 2. 텍스트 생성 (폰트 에러 방지를 위해 print로 대체될 수 있음 - 실제 환경에선 폰트 경로 지정 필수)
    try:
        txt_clip = TextClip(text, fontsize=70, color='white')
        txt_clip = txt_clip.set_position('center').set_duration(duration_sec)
        final_clip = CompositeVideoClip([bg_clip, txt_clip])
    except Exception as e:
        print(f"Warning: TextClip failed ({e}), rendering background only.")
        final_clip = bg_clip

    # 3. 출력 폴더 및 파일 저장
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, f"{vid_id}.mp4")
    final_clip.write_videofile(output_path, fps=24)
    print(f"::notice::Rendered successfully: {output_path}")

if __name__ == "__main__":
    # GitHub Actions에서 넘어오는 인자 받기
    # args: [script_name, id, text, color, duration]
    if len(sys.argv) < 5:
        print("Error: Not enough arguments provided.")
        sys.exit(1)

    v_id = sys.argv[1]
    v_text = sys.argv[2]
    v_color = sys.argv[3]
    v_duration = int(sys.argv[4])

    render_video(v_id, v_text, v_color, v_duration)
