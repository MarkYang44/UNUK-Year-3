import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
for name,path in [('使用说明','README_使用说明.md'),('录音导入脚本','scripts/import_recordings.py'),('快速开始','快速开始.md')]:
    text=bpy.data.texts.get(name) or bpy.data.texts.new(name);text.clear();text.write((ROOT/path).read_text())
bpy.context.scene.frame_set(361)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'edit.blend'))
print('NOTES_UPDATED',flush=True)
