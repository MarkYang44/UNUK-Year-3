"""Blender-only export cache. Editable source remains in visuals.blend.
Rasterize invariant glyphs/color generators once, keep every original keyframe.
"""
import bpy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'assets'/'export_cache';CACHE.mkdir(exist_ok=True)
def cache_scene(s):
    originals=[st for st in s.sequence_editor.strips if st.type in ('TEXT','COLOR')]
    for old in originals:
        kind=old.type;name=old.name;a=old.frame_final_start;b=old.frame_final_end;ch=old.channel
        tr=old.transform;transform={p:getattr(tr,p) for p in ['scale_x','scale_y','offset_x','offset_y','rotation']}
        motion=[]
        if s.animation_data and s.animation_data.action:
            for l in s.animation_data.action.layers:
                for astr in l.strips:
                    for bag in astr.channelbags:
                        for fc in bag.fcurves:
                            if '["'+name+'"]' in fc.data_path:
                                motion.append((fc.data_path.rsplit('].',1)[-1],[(k.co.x,k.co.y,k.interpolation) for k in fc.keyframe_points]))
        if kind=='TEXT':
            props={p:getattr(old,p) for p in ['text','font_size','space_line','wrap_width','anchor_x','anchor_y','alignment_x','use_shadow','use_outline','use_box']}
            for p in ['color','location','shadow_color','outline_color','box_color']:props[p]=tuple(getattr(old,p))
            fingerprint=hashlib.sha256(repr(props).encode()).hexdigest()[:20];size=(1920,1080)
        else:
            props={'color':tuple(old.color)};fingerprint=hashlib.sha256(repr(props).encode()).hexdigest()[:20];size=(32,32)
        path=CACHE/(kind.lower()+'_'+fingerprint+'.png')
        if not path.exists():
            r=bpy.data.scenes.new('EXPORT_CACHE');bpy.context.window.scene=r;r.sequence_editor_create()
            r.render.engine='BLENDER_WORKBENCH';r.render.use_sequencer=True;r.render.use_compositing=False
            r.render.resolution_x=size[0];r.render.resolution_y=size[1];r.render.resolution_percentage=100
            r.render.film_transparent=True;r.view_settings.view_transform='Standard';r.render.image_settings.color_mode='RGBA'
            new=r.sequence_editor.strips.new_effect('Invariant graphics',kind,1,1,length=1)
            for p,v in props.items():setattr(new,p,v)
            if kind=='TEXT':new.font=old.font;new.box_margin=old.box_margin;new.outline_width=old.outline_width
            r.render.filepath=str(path);bpy.ops.render.render(write_still=True)
            bpy.context.window.scene=s;bpy.data.scenes.remove(r)
        # Remove old animation curves before recreating them under the same name.
        if s.animation_data and s.animation_data.action:
            for l in s.animation_data.action.layers:
                for astr in l.strips:
                    for bag in astr.channelbags:
                        for fc in list(bag.fcurves):
                            if '["'+name+'"]' in fc.data_path:bag.fcurves.remove(fc)
        mute=old.mute;alpha=old.blend_alpha
        s.sequence_editor.strips.remove(old)
        new=s.sequence_editor.strips.new_image(name,str(path),ch,a);new.frame_final_duration=b-a
        new.blend_type='ALPHA_OVER';new.blend_alpha=alpha;new.mute=mute
        for p,v in transform.items():setattr(new.transform,p,v*(1920/32 if p=='scale_x' else 1080/32 if p=='scale_y' else 1) if kind=='COLOR' else v)
        for suffix,points in motion:
            if suffix.startswith('transform.'):
                obj=new.transform;prop=suffix.split('.')[-1]
            elif suffix=='blend_alpha':obj=new;prop=suffix
            else:continue
            multiplier=(1920/32 if prop=='scale_x' else 1080/32 if prop=='scale_y' else 1) if kind=='COLOR' else 1
            for f,v,interp in points:
                setattr(obj,prop,v*multiplier);obj.keyframe_insert(data_path=prop,frame=f)
        if s.animation_data and s.animation_data.action:
            for l in s.animation_data.action.layers:
                for astr in l.strips:
                    for bag in astr.channelbags:
                        for fc in bag.fcurves:
                            if '["'+name+'"]' in fc.data_path:
                                for k in fc.keyframe_points:
                                    k.interpolation='BEZIER';k.handle_left_type='AUTO_CLAMPED';k.handle_right_type='AUTO_CLAMPED'
    s.frame_set(s.frame_current)
    print('CACHED_SCENE',s.name,len(originals),flush=True)

if __name__=='__main__':
    import sys,time
    s=next(s for s in bpy.data.scenes if s.get('shot_id')==6);bpy.context.window.scene=s
    cache_scene(s)
    s.frame_set(1900);s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG'
    s.render.filepath=str(ROOT/'qa'/'cached_06.png');bpy.ops.render.render(write_still=True)
    s.frame_start=180;s.frame_end=239;s.render.image_settings.media_type='VIDEO';s.render.image_settings.file_format='FFMPEG'
    s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.filepath=str(ROOT/'qa'/'cached_benchmark.mp4')
    start=time.time();bpy.ops.render.render(animation=True);print('CACHED_BENCHMARK',time.time()-start,flush=True)
