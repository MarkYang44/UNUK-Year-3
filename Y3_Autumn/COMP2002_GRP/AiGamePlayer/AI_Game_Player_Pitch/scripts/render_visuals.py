import bpy, sys, json, time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
args=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
mode=args[0] if args else 'all'
sys.path.insert(0,str(ROOT/'scripts'))
from cache_graphics import cache_scene
scenes=sorted([s for s in bpy.data.scenes if s.name.startswith('S') and 'shot_id' in s],key=lambda s:s['shot_id'])
for s in scenes:
    i=s['shot_id'];bpy.context.window.scene=s
    if mode=='qa':
        for frac,label in [(0.18,'early'),(.55,'mid'),(.92,'tail')]:
            s.frame_set(max(1,int(s.frame_end*frac)));s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG'
            s.render.filepath=str(ROOT/'qa'/('shot_%02d_%s.png'%(i,label)))
            bpy.ops.render.render(write_still=True)
        continue
    if mode=='benchmark':
        if i!=1: continue
        s.frame_start=1;s.frame_end=120;s.render.filepath=str(ROOT/'qa'/'vse_benchmark.mp4')
        s.render.image_settings.media_type='VIDEO';s.render.image_settings.file_format='FFMPEG';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.ffmpeg.constant_rate_factor='HIGH';s.render.ffmpeg.audio_codec='NONE'
        a=time.time();bpy.ops.render.render(animation=True);print('BENCHMARK_SECONDS',time.time()-a,flush=True);break
    if mode.isdigit() and i!=int(mode):continue
    clip=ROOT/'rendered'/('shot_%02d.mp4'%i)
    if clip.exists() and clip.stat().st_size>10000:
        print('SKIP',i,flush=True)
    else:
        cache_scene(s)
        s.frame_start=1;s.render.filepath=str(clip);s.render.image_settings.media_type='VIDEO';s.render.image_settings.file_format='FFMPEG';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264';s.render.ffmpeg.constant_rate_factor='HIGH';s.render.ffmpeg.audio_codec='NONE'
        a=time.time();print('RENDER_START',i,flush=True);bpy.ops.render.render(animation=True);print('RENDER_DONE',i,time.time()-a,flush=True)
    # Extendable tail plate is a rendered asset, not a scene strip.
    s.frame_set(s.frame_end);s.render.image_settings.media_type='IMAGE';s.render.image_settings.file_format='PNG'
    s.render.filepath=str(ROOT/'rendered'/('shot_%02d_hold.png'%i));bpy.ops.render.render(write_still=True)
print('RENDER_COMPLETE',mode,flush=True)
