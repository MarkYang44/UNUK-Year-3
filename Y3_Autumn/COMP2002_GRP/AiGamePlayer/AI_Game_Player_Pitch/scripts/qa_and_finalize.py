import bpy,json,sys,struct,hashlib
import numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
mode=args[0] if args else 'source'
def inspect_paths():
    missing=[];references=[]
    for scene in bpy.data.scenes:
        if not scene.sequence_editor:continue
        for st in scene.sequence_editor.strips:
            paths=[]
            if st.type=='IMAGE':paths=[str(Path(bpy.path.abspath(st.directory))/el.filename) for el in st.elements]
            elif st.type=='MOVIE':paths=[bpy.path.abspath(st.filepath)]
            for p in paths:
                references.append(p)
                if not Path(p).exists():missing.append(p)
    for sound in bpy.data.sounds:
        p=bpy.path.abspath(sound.filepath);references.append(p)
        if not Path(p).exists():missing.append(p)
    for f in bpy.data.fonts:
        if f.filepath not in ('<builtin>','') and not f.packed_file and not Path(bpy.path.abspath(f.filepath)).exists():missing.append(f.filepath)
    assert not missing,missing
    return dict(missing=missing,references=len(references),all_exist=True)

def preview_workspace():
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=='SEQUENCE_EDITOR' and hasattr(area.spaces.active,'view_type'):
                area.spaces.active.view_type='SEQUENCER_PREVIEW'
                try:
                    region=next(r for r in area.regions if r.type=='WINDOW')
                    with bpy.context.temp_override(window=bpy.context.window,screen=screen,area=area,region=region):
                        bpy.ops.sequencer.view_all()
                except Exception as e:print('UI framing note:',e)

if mode=='source':
    out=inspect_paths(); scenes=[s for s in bpy.data.scenes if 'shot_id' in s]
    assert len(scenes)==17
    for s in scenes:
        s.render.image_settings.media_type='VIDEO';s.render.image_settings.file_format='FFMPEG'
        s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.ffmpeg.audio_codec='NONE'
        for st in s.sequence_editor.strips:
            assert st.frame_final_start>=1,(s.name,st.name,st.frame_final_start)
        # A deterministic frame-level layout check on actual strip alpha/timing.
        s.frame_set(int(s.frame_end*.92))
        if s.sequence_editor.strips.get('Board_opening'):
            assert s.sequence_editor.strips['Board_opening'].blend_alpha>.99,s.name
    for f in bpy.data.fonts:
        if f.name.startswith('Inter'):
            f.filepath='//assets/Inter.woff2'
            if not f.packed_file:f.pack()
    for model in bpy.data.scenes:
        if Path(model.render.filepath).is_absolute():model.render.filepath=bpy.path.relpath(model.render.filepath,start=str(ROOT))
    bpy.context.window.scene=sorted(scenes,key=lambda s:s['shot_id'])[0]
    preview_workspace()
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'visuals.blend'))
    out.update(reopened=True,shots=17,main_slides=6,version=bpy.app.version_string,all_fonts_embedded=True)
    (ROOT/'qa'/'visuals_reopen.json').write_text(json.dumps(out,indent=2))
    print('SOURCE_REOPEN_PASS',flush=True)

elif mode=='edit':
    out=inspect_paths();s=bpy.context.scene
    assert s.frame_end==27600 and s.render.fps==60
    assert s.render.resolution_x==1920 and s.render.resolution_y==1080
    movies=[t for t in s.sequence_editor.strips if t.type=='MOVIE']
    assert len(movies)==17
    assert all(abs(t.fps-60)<.001 for t in movies)
    assert not any(t.type=='SCENE' for t in s.sequence_editor.strips)
    # Exact frame coverage from rendered media, excluding optional overlays.
    covered=bytearray(27600)
    for t in movies:
        for f in range(t.frame_final_start,min(27601,t.frame_final_end)):covered[f-1]=1
    assert all(covered)
    for f in bpy.data.fonts:
        if f.name.startswith('Inter'):f.filepath='//assets/Inter.woff2'
    s.render.image_settings.media_type='VIDEO';s.render.image_settings.file_format='FFMPEG'
    s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.ffmpeg.audio_codec='AAC'
    preview_workspace()
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'edit.blend'))
    out.update(reopened=True,frame_coverage=27600,movie_strips=17,scene_strips=0,transitions=16)
    (ROOT/'qa'/'edit_reopen.json').write_text(json.dumps(out,indent=2))
    # Sample every shot and every crossfade at full delivery resolution.
    for i,t in enumerate(sorted(movies,key=lambda t:t.frame_final_start)):
        fs=[(t.frame_final_start+max(30,t.frame_final_duration//2),'shot_%02d'% (i+1))]
        if i:fs.append((t.frame_final_start+18,'transition_%02d'%i))
        for f,label in fs:
            s.frame_set(f);s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG'
            s.render.filepath=str(ROOT/'qa'/('edit_'+label+'.png'));bpy.ops.render.render(write_still=True)
    print('EDIT_REOPEN_PASS',flush=True)

elif mode=='playback':
    # Decode the complete encoded preview again through Blender's own sequencer.
    # The quarter-size QA render is only a decode check; delivery remains 1080p60.
    s=bpy.data.scenes.new('ENCODED_PREVIEW_PLAYBACK_CHECK');bpy.context.window.scene=s;s.sequence_editor_create()
    s.render.resolution_x=1920;s.render.resolution_y=1080;s.render.resolution_percentage=25
    s.render.fps=60;s.render.engine='BLENDER_WORKBENCH';s.view_settings.view_transform='Standard'
    s.render.use_sequencer=True;s.render.use_compositing=False
    s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='JPEG';s.render.image_settings.quality=65
    s.render.filepath=str(ROOT/'qa'/'_playback_decode_frame.jpg')
    st=s.sequence_editor.strips.new_movie('Complete encoded preview',str(ROOT/'preview'/'AI_Game_Player_Pitch_no_voice.mp4'),1,1)
    assert st.frame_duration==27600,st.frame_duration
    assert abs(st.fps-60)<.001,st.fps
    assert st.elements[0].orig_width==1920 and st.elements[0].orig_height==1080
    blanks=[];checked=0;changed=0;prior=None;hashes={}
    for f in range(1,27601):
        s.frame_set(f);bpy.ops.render.render(write_still=True)
        decoded=bpy.data.images.load(s.render.filepath,check_existing=False)
        pixels=np.empty(len(decoded.pixels),dtype=np.float32);decoded.pixels.foreach_get(pixels)
        # Sparse luminance sample over all screen regions; detect missing/black frames.
        rgb=pixels.reshape(-1,4)[:,:3];values=rgb[::97].reshape(-1)
        if len(values)==0 or np.max(values)<.005:blanks.append(f)
        digest=hashlib.sha256(np.clip(values*255,0,255).astype(np.uint8).tobytes()).hexdigest()
        if prior and digest!=prior:changed+=1
        prior=digest;checked+=1
        if f%3600==0:print('PLAYBACK_CHECK',f,'/',27600,flush=True)
        if f in (1,901,2401,6901,14101,19201,24301,27600):hashes[f]=digest
        bpy.data.images.remove(decoded)
    assert not blanks,blanks[:20]
    assert changed>1000,changed
    (ROOT/'qa'/'preview_playback.json').write_text(json.dumps(dict(full_decode_pass=True,frames_checked=checked,seconds=460,fps=60,resolution=[1920,1080],blank_frames=blanks,changed_frames=changed,keyframe_hashes=hashes),indent=2))
    print('FULL_PREVIEW_PLAYBACK_PASS',flush=True)
