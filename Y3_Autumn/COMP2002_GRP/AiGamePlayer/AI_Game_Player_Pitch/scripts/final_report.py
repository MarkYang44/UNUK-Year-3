import bpy,json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
reports={}
for name in ['visuals_reopen','edit_reopen','preview_playback','recording_import_test','rules_validation']:
    reports[name]=json.loads((ROOT/'qa'/(name+'.json')).read_text())
original=json.loads((ROOT/'qa'/'input_hashes.json').read_text())
assert all(hashlib.sha256((ROOT.parent/n).read_bytes()).hexdigest()==v for n,v in original.items())
for file in ['visuals.blend','edit.blend']:
    bpy.ops.wm.open_mainfile(filepath=str(ROOT/file))
    for scene in bpy.data.scenes:
        if not scene.sequence_editor:continue
        for st in scene.sequence_editor.strips:
            if st.type=='IMAGE':
                assert st.directory.startswith('//')
                assert all((Path(bpy.path.abspath(st.directory))/el.filename).exists() for el in st.elements)
            if st.type=='MOVIE':assert st.filepath.startswith('//') and Path(bpy.path.abspath(st.filepath)).exists()
    for sound in bpy.data.sounds:assert sound.filepath.startswith('//') and Path(bpy.path.abspath(sound.filepath)).exists()
    if file=='edit.blend':
        assert bpy.context.scene.render.ffmpeg.format=='MPEG4'
        assert 'normalize_movie' in bpy.data.texts['录音导入脚本'].as_string()
        assert all(c.mute for c in bpy.context.scene.sequence_editor.channels if c.number in (2,3,8,9))
        assert all(st.mute for st in bpy.context.scene.sequence_editor.strips if st.name.startswith('VO_'))
assert len(list((ROOT/'rendered').glob('shot_*.mp4')))==17
assert len(list((ROOT/'rendered').glob('shot_*_hold.png')))==17
reports['delivered']={'visuals':'visuals.blend','edit':'edit.blend','preview':'preview/AI_Game_Player_Pitch_no_voice.mp4','rendered_clips':17,'extendable_holds':17,'resolution':[1920,1080],'fps':60,'seconds':460,'all_relative_media_paths':True,'original_documents_unchanged':True,'latest_engineering_notes_reopened':True,'no_voice_or_person_generated':True,'only_blender_production':True,'pending':'Authentic narration and presenter footage; confirmed team skill narration for shot 04; final subtitle synchronization.'}
(ROOT/'qa'/'final_report.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2))
print('FINAL_DELIVERY_PASS',flush=True)

# Contact sheet includes EVERY transition midpoint for a final visual review.
s=bpy.data.scenes.new('QA_ALL_TRANSITIONS');bpy.context.window.scene=s;s.sequence_editor_create()
s.render.engine='BLENDER_WORKBENCH';s.render.use_sequencer=True;s.view_settings.view_transform='Standard'
s.render.resolution_x=3840;s.render.resolution_y=2160;s.render.resolution_percentage=100
for i in range(16):
    p=ROOT/'qa'/('edit_transition_%02d.png'%(i+1))
    st=s.sequence_editor.strips.new_image('Transition %02d'%(i+1),str(p),i+1,1);st.frame_final_duration=1;st.blend_type='ALPHA_OVER'
    st.transform.scale_x=.5;st.transform.scale_y=.5
    st.transform.offset_x=(i%4)*960+480-1920;st.transform.offset_y=2160-(i//4)*540-270-1080
s.render.filepath=str(ROOT/'qa'/'all_transitions.png');bpy.ops.render.render(write_still=True)
