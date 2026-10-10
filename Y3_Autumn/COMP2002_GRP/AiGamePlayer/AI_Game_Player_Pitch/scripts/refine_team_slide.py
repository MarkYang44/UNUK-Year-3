import bpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
s=next(s for s in bpy.data.scenes if s.get('shot_id')==4)
changes={'Pending':'Skills → contribution','No_claim':'Proposed work areas · assignments follow confirmed experience.','Rules_body':'Legal movement + walls','AI_body':'Search + evaluation','GUI + testing_body':'Interface + integration','Placeholder_notice':'Whole team experience → shared project ownership'}
for name,words in changes.items():s.sequence_editor.strips[name].text=words
s['pending']='Confirmed whole-team experience is required for the S04 voiceover. Visual shows proposed work areas only; no skill claim.'
bpy.context.window.scene=next(s for s in bpy.data.scenes if s.get('shot_id')==1)
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'visuals.blend'))
print('TEAM_SLIDE_REFINED',flush=True)
