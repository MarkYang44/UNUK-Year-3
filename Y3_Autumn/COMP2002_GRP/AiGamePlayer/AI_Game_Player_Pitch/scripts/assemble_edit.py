"""Run in Blender AFTER render_visuals.py; final edit uses only rendered media."""
import bpy, json, re, math, struct, wave
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FPS=60; W=1920;H=1080;TOTAL=27600
shots=json.loads((ROOT/'shots.json').read_text())
font=bpy.data.fonts.load('/Applications/Blender.app/Contents/Resources/5.2/datafiles/fonts/Inter.woff2');font.pack()
for o in list(bpy.data.objects):bpy.data.objects.remove(o,do_unlink=True)
s=bpy.context.scene;s.name='EDIT_07m40s_1080p60';s.sequence_editor_create()
s.render.resolution_x=W;s.render.resolution_y=H;s.render.resolution_percentage=100;s.render.fps=FPS
s.render.fps_base=1;s.frame_start=1;s.frame_end=TOTAL;s.render.use_sequencer=True;s.render.use_compositing=False
s.view_settings.view_transform='Standard';s.render.engine='BLENDER_WORKBENCH'
s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.ffmpeg.constant_rate_factor='HIGH'
s.render.ffmpeg.ffmpeg_preset='GOOD';s.render.ffmpeg.audio_codec='AAC';s.render.ffmpeg.audio_bitrate=192;s.render.ffmpeg.audio_mixrate=48000
seq=s.sequence_editor
def key(o,p,v,f):setattr(o,p,v);o.keyframe_insert(data_path=p,frame=f)
def ease(scene):
    if not scene.animation_data or not scene.animation_data.action:return
    for l in scene.animation_data.action.layers:
        for st in l.strips:
            for b in st.channelbags:
                for c in b.fcurves:
                    for k in c.keyframe_points:k.interpolation='BEZIER';k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
def image(name,path,ch,a,b):
    x=seq.strips.new_image(name,str(path),ch,a);x.frame_final_duration=b-a;x.blend_type='ALPHA_OVER';return x
def txt(scene,name,words,ch,a,b,x=960,y=57,size=30):
    xst=scene.sequence_editor.strips.new_effect(name,'TEXT',ch,a,length=b-a)
    xst.text=words;xst.font=font;xst.font_size=size;xst.color=(.91,.95,1,1);xst.location=(x/W,y/H)
    xst.anchor_x='CENTER';xst.anchor_y='CENTER';xst.alignment_x='CENTER';xst.wrap_width=.84
    xst.blend_type='ALPHA_OVER';xst.use_box=True;xst.box_color=(.018,.03,.05,.92);xst.box_margin=.005
    return xst

# Original, very quiet UI tick synthesized inside Blender Python. Silence is a
# placeholder file only; it is not generated narration.
with wave.open(str(ROOT/'assets'/'silence_placeholder.wav'),'wb') as f:
    f.setnchannels(1);f.setsampwidth(2);f.setframerate(8000)
    for _ in range(460):f.writeframes(b'\0\0'*8000)
with wave.open(str(ROOT/'assets'/'soft_tick.wav'),'wb') as f:
    f.setnchannels(1);f.setsampwidth(2);f.setframerate(48000)
    samples=[]
    for i in range(5760):
        t=i/48000;v=.09*math.sin(2*math.pi*(720-180*t)*t)*math.exp(-t*55)*min(1,t/.004)
        samples.append(struct.pack('<h',int(v*32767)))
    f.writeframes(b''.join(samples))

# Presenter frames rendered in Blender; preview keeps their channels hidden.
for who,col in [('A',(.12,.6,.96)),('B',(1,.48,.18))]:
    p=bpy.data.scenes.new('PLACEHOLDER_'+who);bpy.context.window.scene=p;p.sequence_editor_create()
    p.render.resolution_x=W;p.render.resolution_y=H;p.render.resolution_percentage=100;p.render.use_sequencer=True
    p.render.engine='BLENDER_WORKBENCH';p.view_settings.view_transform='Standard';p.render.film_transparent=True
    p.render.image_settings.color_mode='RGBA'
    for j,(cx,cy,ww,hh) in enumerate([(1690,917,250,2),(1690,777,250,2),(1565,847,2,140),(1815,847,2,140)]):
        c=p.sequence_editor.strips.new_effect('Frame edge','COLOR',j+1,1,length=1);c.color=col;c.blend_type='ALPHA_OVER'
        c.transform.scale_x=ww/W;c.transform.scale_y=hh/H;c.transform.offset_x=cx-W/2;c.transform.offset_y=cy-H/2
    txt(p,'Presenter label','PERSON '+who+'\nReplace / hidden',6,1,2,1690,847,23)
    p.render.filepath=str(ROOT/'assets'/('person_'+who+'_placeholder.png'));p.frame_set(1);bpy.ops.render.render(write_still=True)
    bpy.data.scenes.remove(p)
bpy.context.window.scene=s

previous=None
for m in shots:
    i=m['shot'];a=m['first_frame'];b=m['last_frame']+1;ch=4+(i-1)%2
    path=ROOT/'rendered'/('shot_%02d.mp4'%i);assert path.exists(),path
    st=seq.strips.new_movie('S%02d | %s | %ds'%(i,m['title'],m['duration_seconds']),str(path),ch,a)
    st.blend_type='ALPHA_OVER';assert st.frame_duration==b-a,(i,st.frame_duration,b-a)
    st.frame_final_duration=b-a
    if previous:
        pm,pst,pch=previous
        hold=image('S%02d TRANSITION / extendable hold'%pm['shot'],ROOT/'rendered'/('shot_%02d_hold.png'%pm['shot']),pch,a,a+36)
        if ch>pch:
            key(st,'blend_alpha',0,a);key(st,'blend_alpha',1,a+36)
        else:
            key(hold,'blend_alpha',1,a);key(hold,'blend_alpha',0,a+35)
    previous=(m,st,ch)
    s.timeline_markers.new('S%02d | Slide %d | %s | %ds'%(i,m['slide'],m['speaker'],m['duration_seconds']),frame=a)
    s.timeline_markers.new('S%02d hold / extend here'%i,frame=b-121)
    s['S%02d_narration'%i]=m['narration']
    s['S%02d_expected_duration'%i]=m['duration_seconds']

    # Voice placeholders are individual silent audio strips on explicitly named lanes.
    voiceparts=[(m['speaker'],a,b)] if i!=17 else [('B',a,a+900),('A',a+900,b)]
    for who,va,vb in voiceparts:
        v=seq.strips.new_sound('VO_%s_S%02d / REPLACE / %ds'%(who,i,(vb-va)//FPS),str(ROOT/'assets'/'silence_placeholder.wav'),2 if who=='A' else 3,va)
        v.frame_final_duration=vb-va;v.mute=True
    # Hidden picture placeholders, with two presenters side by side in S03 and S17.
    for who,va,vb in voiceparts:
        q=image('PERSON_%s_S%02d / REPLACE'% (who,i),ROOT/'assets'/('person_'+who+'_placeholder.png'),8 if who=='A' else 9,va,vb)
        if i==3:
            key(q.transform,'offset_x',-270,va);key(q.transform,'offset_x',-270,va+330);key(q.transform,'offset_x',0,va+390)
        if i==17 and who=='A':
            key(q.transform,'offset_x',0,va);key(q.transform,'offset_x',0,b-391);key(q.transform,'offset_x',-270,b-331)
    if i==3:image('PERSON_B_S03_DUO / REPLACE',ROOT/'assets'/'person_B_placeholder.png',9,a,a+360)
    if i==17:image('PERSON_B_S17_DUO / REPLACE',ROOT/'assets'/'person_B_placeholder.png',9,b-360,b)

# Optional extra graphics lane is present and invisible.
g=seq.strips.new_effect('GRAPHICS / optional overlays','COLOR',6,1,length=TOTAL);g.blend_type='ALPHA_OVER';g.blend_alpha=0;g.mute=True
for j,f in enumerate([181,1321,14161,26701]):
    t=seq.strips.new_sound('SFX_soft_tick_%d'%j,str(ROOT/'assets'/'soft_tick.wav'),1,f);t.volume=.25

captions=[]
for m in shots:
    a=m['first_frame'];b=m['last_frame']+1;i=m['shot']
    text=m['narration'] if i!=4 else 'Team skills — pending confirmation. Replace this section after the team confirms its experience.'
    chunks=[]
    for sentence in re.split(r'(?<=[.!?])\s+',text):
        words=sentence.split()
        while words:
            n=min(15,len(words));chunks.append(' '.join(words[:n]));words=words[n:]
    weights=[len(c.split()) for c in chunks];denom=sum(weights);f=a;acc=0
    for j,(c,w) in enumerate(zip(chunks,weights)):
        acc+=w;end=b if j==len(chunks)-1 else a+round((b-a)*acc/denom)
        if end<=f:continue
        cue=txt(s,'SUB_DRAFT_S%02d_%02d'%(i,j+1),c,7,f,end)
        if i==4:cue.mute=True # No skill narration was provided; production note stays off screen.
        captions.append((f,end,c));f=end
def stamp(frame):
    ms=round((frame-1)/FPS*1000);return '%02d:%02d:%02d,%03d'%(ms//3600000,(ms//60000)%60,(ms//1000)%60,ms%1000)
(ROOT/'subtitles_draft.srt').write_text('\n\n'.join('%d\n%s --> %s\n%s'%(j+1,stamp(a),stamp(b),c) for j,(a,b,c) in enumerate(captions))+'\n')
names={1:'SFX / original soft ticks',2:'旁白 A / VO_A / replace silent strips',3:'旁白 B / VO_B / replace silent strips',4:'图形 / GRAPHICS_A / rendered shots',5:'图形 / GRAPHICS_B / rendered shots',6:'图形 / optional overlays (hidden)',7:'字幕 / DRAFT / sync after recording',8:'人物 A / PERSON_A (hidden)',9:'人物 B / PERSON_B (hidden)'}
for c in seq.channels:
    c.name=names.get(c.number,'Channel '+str(c.number))
    if c.number in (2,3,6,8,9):c.mute=True
s.timeline_markers.new('S17 B → A / adjust after recording',frame=26701)
s.timeline_markers.new('END / 07:40 / 27600 frames',frame=27601)
s['README']='See README_使用说明.md. All visual clips are rendered media; no final scene strips. Presenter channels hidden. Subtitle draft visible; retime after recording.'
s['presenter_safe_zone']='Upper right, 250×140 at center 1690,847; duo A shifts 270px left. Nothing important underneath.'
s['pending']='S04: confirmed skills and final narration still required. No invented skill claims.'
ease(s)
for x in seq.strips:
    if x.type=='IMAGE':x.directory=bpy.path.relpath(x.directory,start=str(ROOT))
    if x.type=='MOVIE':x.filepath=bpy.path.relpath(x.filepath,start=str(ROOT))
for snd in bpy.data.sounds:snd.filepath=bpy.path.relpath(snd.filepath,start=str(ROOT))
for label,file in [('使用说明','README_使用说明.md'),('镜头与台词','shots.json'),('录音导入脚本','scripts/import_recordings.py')]:
    p=ROOT/file
    if p.exists():t=bpy.data.texts.new(label);t.write(p.read_text())
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.type='SEQUENCE_EDITOR'
s.frame_set(361);s.render.filepath='//preview/AI_Game_Player_Pitch_no_voice.mp4'
s.render.image_settings.media_type='VIDEO';s.render.image_settings.file_format='FFMPEG';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.ffmpeg.audio_codec='AAC'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'edit.blend'))
(ROOT/'qa'/'edit_structure.json').write_text(json.dumps({'frames':TOTAL,'fps':FPS,'seconds':460,'resolution':[W,H],'scene_strips':0,'movies':17,'transitions':16,'transition_frames':36,'subtitle_cues':len(captions),'channels':names,'hidden_channels':[2,3,6,8,9],'pending':'S04 confirmed team skills','rendered_first':True},ensure_ascii=False,indent=2))
print('EDIT_COMPLETE',flush=True)
