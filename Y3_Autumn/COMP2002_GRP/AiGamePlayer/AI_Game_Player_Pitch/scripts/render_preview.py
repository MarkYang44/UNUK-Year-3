import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=bpy.context.scene
assert s.name.startswith('EDIT_')
s.frame_start=1;s.frame_end=27600;s.render.resolution_percentage=100
s.render.image_settings.media_type='VIDEO';s.render.image_settings.file_format='FFMPEG'
s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264'
s.render.ffmpeg.constant_rate_factor='HIGH';s.render.ffmpeg.ffmpeg_preset='GOOD'
s.render.ffmpeg.audio_codec='AAC';s.render.ffmpeg.audio_mixrate=48000;s.render.ffmpeg.audio_bitrate=192
s.render.filepath=str(ROOT/'preview'/'AI_Game_Player_Pitch_no_voice.mp4')
bpy.ops.render.render(animation=True)
print('PREVIEW_RENDER_COMPLETE',flush=True)
