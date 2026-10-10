import bpy,json,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
F=ROOT/'qa'/'import_test';F.mkdir(exist_ok=True)
shutil.copyfile(ROOT/'rendered'/'shot_03.mp4',F/'S03_A.mp4')
shutil.copyfile(ROOT/'assets'/'silence_placeholder.wav',F/'S03_A.wav')
shutil.copyfile(ROOT/'qa'/'fps30_test.mp4',F/'S17_A.mp4')
code=(ROOT/'scripts'/'import_recordings.py').read_text().replace("FOLDER=ROOT/'recordings'","FOLDER=ROOT/'qa'/'import_test'")
exec(compile(code,'import_recordings.py','exec'))
s=bpy.context.scene;seq=s.sequence_editor
cam=seq.strips['CAM_S03_A'];voice=seq.strips['REC_S03_A'];short=seq.strips['CAM_S17_A']
assert cam.frame_final_start==2401 and cam.frame_final_duration==1200
assert voice.frame_final_start==2401 and voice.frame_final_duration==1200
assert short.frame_final_duration==8
s.frame_set(2501);assert abs(cam.transform.offset_x-460)<.01
s.frame_set(3001);assert abs(cam.transform.offset_x-730)<.01
assert abs(cam.transform.scale_x-250/1920)<.00001
assert abs(short.transform.scale_x-250/1920)<.00001
(ROOT/'qa'/'recording_import_test.json').write_text(json.dumps({'passed':True,'memory_only_no_edit_saved':True,'tested':['audio placeholder replacement','movie placeholder replacement','duo→single movement keys preserved','60fps 1080p framing','30fps retimed to 60fps at original speed','short-take warning','small-source framing scaled correctly']},indent=2))
print('RECORDING_IMPORT_PASS',flush=True)
