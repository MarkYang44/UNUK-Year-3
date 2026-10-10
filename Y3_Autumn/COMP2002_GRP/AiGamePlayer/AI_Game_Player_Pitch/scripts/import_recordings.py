"""Optional convenience tool. Run from edit.blend's Text Editor.
Place S01_A.wav / S01_A.mp4 etc in recordings/. It never generates a voice/person.
Existing placeholders are removed only when the matching recording exists.
"""
import bpy,re,hashlib
from pathlib import Path
ROOT=Path(bpy.path.abspath('//'))
FOLDER=ROOT/'recordings'
scene=bpy.context.scene;seq=scene.sequence_editor
if seq is None:raise RuntimeError('Open edit.blend first.')
def find(stem,extensions):
    return next((FOLDER/(stem+ext) for ext in extensions if (FOLDER/(stem+ext)).exists()),None)
count=0
def normalize_movie(file):
    """Convert mismatched rates in a separate Blender scene starting at frame 1.
    Blender 5.2 retiming at large timeline offsets can crash; never do it in edit.
    """
    prep=bpy.data.scenes.new('PREP_RECORDING_60FPS');bpy.context.window.scene=prep;prep.sequence_editor_create()
    prep.render.fps=scene.render.fps;prep.render.resolution_x=1920;prep.render.resolution_y=1080;prep.render.resolution_percentage=100
    movie=prep.sequence_editor.strips.new_movie('Original recording',str(file),1,1,fit_method='FIT')
    if abs(movie.fps-scene.render.fps)<.01:
        bpy.context.window.scene=scene;bpy.data.scenes.remove(prep);return file
    target=round(movie.frame_duration*scene.render.fps/movie.fps)
    stamp=hashlib.sha256((str(file)+str(file.stat().st_mtime_ns)+str(scene.render.fps)).encode()).hexdigest()[:10]
    folder=file.parent/'.blender_cache';folder.mkdir(exist_ok=True)
    normalized=folder/(file.stem+'_'+stamp+'_60fps.mp4')
    if not normalized.exists():
        prep.frame_set(1);movie.retiming_keys.add(timeline_frame=1)
        list(movie.retiming_keys)[-1].timeline_frame=target+1
        prep.frame_start=1;prep.frame_end=target;prep.render.engine='BLENDER_WORKBENCH';prep.view_settings.view_transform='Standard'
        prep.render.use_sequencer=True;prep.render.use_compositing=False
        prep.render.image_settings.media_type='VIDEO';prep.render.image_settings.file_format='FFMPEG'
        prep.render.ffmpeg.format='MPEG4';prep.render.ffmpeg.codec='H264';prep.render.ffmpeg.constant_rate_factor='HIGH';prep.render.ffmpeg.audio_codec='NONE'
        temporary=folder/(normalized.stem+'_partial.mp4');prep.render.filepath=str(temporary)
        bpy.ops.render.render(animation=True);temporary.replace(normalized)
    bpy.context.window.scene=scene;bpy.data.scenes.remove(prep)
    return normalized

for st in list(seq.strips):
    m=re.match(r'(VO|PERSON)_([AB])_S(\d{2})(_DUO)?',st.name)
    if not m:continue
    kind,who,shot,duo=m.groups();stem='S'+shot+'_'+who
    file=find(stem,['.wav','.flac','.mp3','.m4a']) if kind=='VO' else find(stem,['.mp4','.mov','.mkv'])
    if not file:continue
    if kind=='PERSON':file=normalize_movie(file)
    a=st.frame_final_start;length=st.frame_final_duration;ch=st.channel
    dx=st.transform.offset_x if kind=='PERSON' else 0
    # Preserve position animation by transferring its F-curves after renaming.
    old_name=st.name
    motion=[]
    if scene.animation_data and scene.animation_data.action:
        for layer in scene.animation_data.action.layers:
            for actionstrip in layer.strips:
                for bag in actionstrip.channelbags:
                    for curve in bag.fcurves:
                        if ('["'+old_name+'"]') in curve.data_path:
                            motion.append((curve.data_path.rsplit('].',1)[-1],[(int(k.co.x),float(k.co.y)) for k in curve.keyframe_points]))
    if kind=='VO':
        seq.strips.remove(st)
        new=seq.strips.new_sound('REC_'+stem,bpy.path.relpath(str(file)),ch,a)
    else:
        seq.strips.remove(st)
        new=seq.strips.new_movie('CAM_'+stem+('_DUO' if duo else ''),bpy.path.relpath(str(file)),ch,a,fit_method='FIT')
        new.blend_type='ALPHA_OVER';new.transform.scale_x*=250/1920;new.transform.scale_y*=250/1920
        # Recorded image is centered into the reserved upper-right safe area.
        new.transform.offset_x=1690-960+dx;new.transform.offset_y=847-540
    available=new.frame_duration
    new.frame_final_duration=min(length,available)
    if available<length:print('SHORT RECORDING: '+stem+'; adjust shot timing or supply a longer take.')
    new.mute=False;count+=1
    for channel in seq.channels:
        if channel.number==ch:channel.mute=False
    for suffix,points in motion:
        if suffix not in ('transform.offset_x','transform.offset_y','blend_alpha'):continue
        owner=new.transform if suffix.startswith('transform.') else new
        attr=suffix.split('.')[-1]
        shift=(1690-960 if attr=='offset_x' else 847-540 if attr=='offset_y' else 0) if kind=='PERSON' else 0
        for f,v in points:
            setattr(owner,attr,v+shift);owner.keyframe_insert(data_path=attr,frame=f)
scene.frame_set(scene.frame_current)
for pending in seq.strips:
    if pending.name.startswith('PERSON_'):pending.mute=True
print('Imported',count,'recordings. Save a new edit version after checking alignment.')
