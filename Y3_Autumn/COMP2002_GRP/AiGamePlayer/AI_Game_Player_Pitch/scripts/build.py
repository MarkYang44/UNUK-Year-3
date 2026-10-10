"""Run inside Blender 5.2. All image, animation and video output uses Blender."""
import bpy, math, json, re, os, sys, hashlib, wave, struct
from pathlib import Path
from collections import deque
ROOT=Path(__file__).resolve().parents[1]
FPS=60
W,H=1920,1080
NAVY=(.025,.045,.075)
PANEL=(.06,.09,.14)
WHITE=(.88,.93,.98)
MUTED=(.45,.57,.68)
BLUE=(.12,.60,.96)
ORANGE=(1,.48,.18)
TEAL=(.22,.82,.68)
RED=(.98,.26,.29)
FONT_PATH='/Applications/Blender.app/Contents/Resources/5.2/datafiles/fonts/Inter.woff2'
font=bpy.data.fonts.load(FONT_PATH)
font.pack()

def set_render(s):
    s.render.resolution_x=W; s.render.resolution_y=H; s.render.resolution_percentage=100
    s.render.fps=FPS; s.render.fps_base=1
    s.render.image_settings.file_format='PNG'; s.render.image_settings.color_mode='RGBA'
    s.view_settings.view_transform='Standard'
    s.render.engine='BLENDER_WORKBENCH'
    s.render.use_compositing=False
    s.display.render_aa='8'
    s.render.ffmpeg.format='MPEG4'; s.render.ffmpeg.codec='H264'
    s.render.ffmpeg.constant_rate_factor='HIGH'; s.render.ffmpeg.ffmpeg_preset='GOOD'
    s.render.ffmpeg.audio_codec='NONE'

def switch(s): bpy.context.window.scene=s
def key(o,p,v,f):
    setattr(o,p,v); o.keyframe_insert(data_path=p,frame=f)

def ease(o):
    owner=o if hasattr(o,'animation_data') else o.id_data
    if not owner.animation_data or not owner.animation_data.action: return
    for layer in owner.animation_data.action.layers:
        for st in layer.strips:
            for bag in st.channelbags:
                for fc in bag.fcurves:
                    for k in fc.keyframe_points:
                        k.interpolation='BEZIER'; k.handle_left_type='AUTO_CLAMPED'; k.handle_right_type='AUTO_CLAMPED'

def edges(w):
    orient,x,y=w
    if orient=='h': return {frozenset(((x,y),(x,y+1))),frozenset(((x+1,y),(x+1,y+1)))}
    return {frozenset(((x,y),(x+1,y))),frozenset(((x,y+1),(x+1,y+1)))}

def route(p,goal,walls,avoid=None):
    blocked=set().union(*(edges(w) for w in walls)) if walls else set()
    q=deque([p]); prev={p:None}
    while q:
        a=q.popleft()
        if a[1]==goal:
            out=[]
            while a is not None: out.append(a); a=prev[a]
            return out[::-1]
        for dx,dy in ((0,1),(0,-1),(-1,0),(1,0)):
            b=(a[0]+dx,a[1]+dy)
            if 0<=b[0]<9 and 0<=b[1]<9 and b!=avoid and b not in prev and frozenset((a,b)) not in blocked:
                prev[b]=a;q.append(b)
    return None

def wall_legal(w,ws,ps):
    o,x,y=w
    if not (o in ('h','v') and 0<=x<8 and 0<=y<8): return False
    for z in ws:
        if edges(w)&edges(z) or (z[1:]==w[1:] and z[0]!=w[0]): return False
    return all(route(p,g,ws+[w]) for p,g in zip(ps,(8,0)))

def legal_moves(p,other,walls):
    blocked=set().union(*(edges(w) for w in walls)) if walls else set()
    def free(a,b): return 0<=b[0]<9 and 0<=b[1]<9 and frozenset((a,b)) not in blocked
    out=set()
    for dx,dy in ((1,0),(-1,0),(0,1),(0,-1)):
        n=(p[0]+dx,p[1]+dy)
        if not free(p,n):continue
        if n!=other:out.add(n);continue
        behind=(n[0]+dx,n[1]+dy)
        if free(n,behind):out.add(behind)
        else:
            for vx,vy in ((dy,dx),(-dy,-dx)):
                side=(n[0]+vx,n[1]+vy)
                if free(n,side):out.add(side)
    return out

checks=[]
def check(name,condition):
    assert condition,name;checks.append({'check':name,'passed':True})
check('Opening is reached by H e1-e2, AI e9-e8, with H to act',(4,1) in legal_moves((4,0),(4,8),[]) and (4,7) in legal_moves((4,8),(4,1),[]))
check('Move alternative e2-e3 is legal',(4,2) in legal_moves((4,1),(4,7),[]))
check('Wall alternative h(4,5) legal and both routes retained',wall_legal(('h',4,5),[],[(4,1),(4,7)]))
check('Crossing wall rejected',not wall_legal(('v',4,5),[('h',4,5)],[(4,1),(4,7)]))
check('Overlapping wall rejected',not wall_legal(('h',5,5),[('h',4,5)],[(4,1),(4,7)]))
check('Existing rule fixture retains both routes',bool(route((0,0),8,[('h',0,1)])) and bool(route((4,7),0,[('h',0,1)])))
check('Red proposed wall seals human route and is rejected',not wall_legal(('v',1,0),[('h',0,1)],[(0,0),(4,7)]))
check('Straight pawn jump legal',(4,5) in legal_moves((4,3),(4,4),[]))
check('Diagonal exception only when jump blocked',(3,4) in legal_moves((4,3),(4,4),[('h',4,4)]) and (5,4) in legal_moves((4,3),(4,4),[('h',4,4)]))
check('Ordinary diagonal rejected',(3,4) not in legal_moves((4,3),(4,7),[]))

# Source material read without modification. These are narration data, not commands.
md=(ROOT.parent/'AI_Game_Player_Pitch_分镜与台词.md').read_text()
parts=re.split(r'### 镜头 ',md)[1:]
durations=[15,25,20,25,30,35,25,30,30,30,25,30,35,25,25,25,30]
speakers=['A','B','A','A','B','B','B','A','B','A','B','A','B','A','B','A','B / A']
slides=[1,1,2,2,2,3,3,3,3,4,4,4,5,5,5,6,6]
titles=['One move changes everything','Move or wall?','We are Team 26','Strengths into contributions','A simple goal. Difficult choices.','How our AI would decide','Two rollout approaches','A reliable game underneath','Keep the interface responsive','Challenge without the wait','Difficulty we can calibrate','Evidence before claims','A plan we can deliver','Shared ownership','Risks with a response','Responsible by design','An opponent worth playing']
section_titles=['One move changes everything','A simple goal with difficult choices','How our AI would decide','Challenge without the wait','A plan we can deliver','An opponent worth playing']
manifest=[]; t=0
for i,part in enumerate(parts):
    speech=' '.join(re.findall(r'^> (.*)$',part.split('## 制作与排练检查')[0],re.M))
    manifest.append(dict(shot=i+1,slide=slides[i],title=titles[i],speaker=speakers[i],start_seconds=t,duration_seconds=durations[i],narration=speech,first_frame=t*FPS+1,last_frame=(t+durations[i])*FPS))
    t+=durations[i]
assert t==460
(ROOT/'shots.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2))
(ROOT/'qa'/'rules_validation.json').write_text(json.dumps({'official_rulebook':'https://export.gigamic.com/wp-content/uploads/2021/01/INS-RULES-QUORIDOR_10-2016.pdf','coordinate_convention':'x,y zero based; human goal y=8; AI goal y=0; h blocks vertical edges, v blocks horizontal edges','checks':checks,'opening_history':['H e1-e2','AI e9-e8'],'alternatives':'Independent alternatives on human turn, not consecutive moves. Route guides use graph reachability and are not played move sequences.','wall_inventory':{'opening':[10,10],'move_branch':[10,10],'wall_branch':[9,10]},'invalid_preview':'Rule test fixture; red v(1,0) is a rejected preview, never a committed move.'},indent=2))

for o in list(bpy.data.objects): bpy.data.objects.remove(o,do_unlink=True)
bpy.context.scene.name='PROJECT_INFO'

# All geometry is original. A top view keeps the rules and wall placement legible.
def material(name,c):
    m=bpy.data.materials.get(name) or bpy.data.materials.new(name);m.diffuse_color=(*c,1);return m
def cube(name,loc,scale,col,bevel=.06):
    bpy.ops.mesh.primitive_cube_add(size=1,location=loc);o=bpy.context.object;o.name=name;o.dimensions=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(material(name.split('_')[0]+'_'+str(col),col))
    if bevel:
        m=o.modifiers.new('Soft edges','BEVEL');m.width=bevel;m.segments=3
        o.modifiers.new('Weighted normals','WEIGHTED_NORMAL')
    return o
def obj_text(txt,loc,size,col):
    c=bpy.data.curves.new(txt,'FONT');c.body=txt;c.size=size;c.font=font;c.align_x='CENTER';c.align_y='CENTER'
    o=bpy.data.objects.new(txt,c);bpy.context.scene.collection.objects.link(o);o.location=loc;c.materials.append(material('text_'+txt,col));return o
def board_scene(name,ps=((4,1),(4,7)),walls=(),pawn_only=None):
    s=bpy.data.scenes.new('MODEL_'+name);switch(s);set_render(s)
    s.render.film_transparent=True;s.render.use_sequencer=False
    s.display.shading.light='STUDIO';s.display.shading.studiolight_rotate_z=.5
    s.display.shading.color_type='MATERIAL';s.display.shading.show_shadows=True;s.display.shading.show_cavity=False
    s.display.shading.cavity_type='BOTH';s.display.shading.show_specular_highlight=False
    cam=bpy.data.cameras.new('Camera_'+name);co=bpy.data.objects.new('Camera_'+name,cam);s.collection.objects.link(co);co.location=(0,0,20);cam.type='ORTHO';cam.ortho_scale=19.2;s.camera=co
    def xy(p):return (-3.7+(p[0]-4)*.72,-.35+(p[1]-4)*.72)
    if pawn_only is None:
        cube('Board_base',(-3.7,-.35,-.15),(6.7,6.7,.32),(.13,.20,.27),.16)
        for x in range(9):
            for y in range(9):
                a,b=xy((x,y));cube('Tile_%d_%d'%(x,y),(a,b,.03),(.64,.64,.10),(.32,.41,.47),.055)
        for y,c in ((8,BLUE),(0,ORANGE)):
            a,b=xy((4,y));b+=.33 if y==8 else -.33
            cube('Goal_band', (a,b,.095),(6.35,.07,.02),c,.02)
        for orient,x,y in walls:
            a,b=xy((x+.5,y+.5))
            cube('Wall_'+orient+str(x)+str(y),(a,b,.22),(1.36,.10,.25) if orient=='h' else (.10,1.36,.25),(.85,.76,.54),.035)
    for i,(p,c,label) in enumerate(zip(ps,(BLUE,ORANGE),('H','AI'))):
        if pawn_only is not None and pawn_only!=i:continue
        a,b=xy(p)
        if i==0:
            bpy.ops.mesh.primitive_uv_sphere_add(segments=32,ring_count=16,radius=.25,location=(a,b,.31));o=bpy.context.object;o.name='Human_circle';o.scale.z=.6;o.data.materials.append(material('Human',c))
        else: o=cube('AI_square',(a,b,.27),(.48,.48,.30),c,.08)
        obj_text(label,(a,b,.55),.21,NAVY)
    # Keep physically meaningful editable pawn movement in the source model.
    if name=='MOVE':
        for o in list(s.objects):
            if o.name.startswith('Human_circle') or (o.type=='FONT' and o.data.body=='H'):
                dest=o.location.copy();o.location.y-=.72;o.keyframe_insert('location',frame=1)
                o.location=dest;o.keyframe_insert('location',frame=90);ease(o)
        s.frame_set(90)
    s['purpose']='Editable source geometry. Rerender plate via scripts/build.py after model edits.'
    s.frame_end=180
    path=ROOT/'assets'/('board_'+name.lower()+'.png');s.render.filepath=str(path)
    bpy.ops.render.render(write_still=True)
    return str(path)

plates={}
plates['base']=board_scene('BASE',pawn_only=-1) # full board omitted for pawn_only, repaired below
# A clean board without pawns: create full model and remove the two pawn labels + meshes.
s=bpy.data.scenes['MODEL_BASE']
for o in list(s.objects):
    if o.type!='CAMERA': bpy.data.objects.remove(o,do_unlink=True)
temp=board_scene('CLEAN')
s=bpy.context.scene
for o in list(s.objects):
    if o.name.startswith(('Human_circle','AI_square')) or (o.type=='FONT' and o.data.body in ('H','AI')):bpy.data.objects.remove(o,do_unlink=True)
s.render.filepath=str(ROOT/'assets'/'board_clean.png');bpy.ops.render.render(write_still=True);plates['clean']=s.render.filepath
plates['opening']=board_scene('OPENING')
plates['move']=board_scene('MOVE',ps=((4,2),(4,7)))
plates['wall']=board_scene('WALL',walls=(('h',4,5),))
plates['human']=board_scene('HUMAN_SPRITE',pawn_only=0)
plates['ai']=board_scene('AI_SPRITE',pawn_only=1)
plates['fixture']=board_scene('RULE_FIXTURE',ps=((0,0),(4,7)),walls=(('h',0,1),))

# Native VSE motion design: every title, card, path, highlight and transition is editable.
def effect(s,name,typ,ch,start,end):return s.sequence_editor.strips.new_effect(name,typ,ch,start,length=end-start)
def alpha(st,start,end,fade=24,out=False):
    if fade:
        key(st,'blend_alpha',0,start);key(st,'blend_alpha',1,start+fade)
        if out:key(st,'blend_alpha',1,end-fade);key(st,'blend_alpha',0,end-1)
    ease(st)
def rect(s,name,x,y,w,h,c,ch,start=1,end=None,fade=0):
    end=end or s.frame_end+1
    st=effect(s,name,'COLOR',ch,start,end);st.color=c;st.blend_type='ALPHA_OVER'
    st.transform.scale_x=w/W;st.transform.scale_y=h/H;st.transform.offset_x=x-W/2;st.transform.offset_y=y-H/2
    alpha(st,start,end,fade)
    return st
def text(s,name,txt,x,y,size=40,c=WHITE,ch=10,start=1,end=None,fade=24,align='LEFT'):
    end=end or s.frame_end+1
    # Allocate a separate upper channel at creation time. Moving occupied channels
    # later causes Blender 5.2 to shuffle strips AND their keyframe times.
    ch=94+s.get('_text_count',0);s['_text_count']=s.get('_text_count',0)+1
    assert ch<=128
    st=effect(s,name,'TEXT',ch,start,end);st.text=txt;st.font=font;st.font_size=size;st.color=(*c,1)
    st.location=(x/W,y/H);st.anchor_x=align;st.anchor_y='CENTER';st.alignment_x=align
    st.blend_type='ALPHA_OVER';st.use_shadow=False;st.wrap_width=0
    alpha(st,start,end,fade)
    # Small purposeful rise, then hold. Typography is never scaled.
    if fade:
        key(st.transform,'offset_y',-10,start);key(st.transform,'offset_y',0,start+fade);ease(st.transform)
    return st
def image(s,name,path,ch,start=1,end=None,scale=1,dx=0,dy=0,fade=24):
    st=s.sequence_editor.strips.new_image(name,path,ch,start);st.frame_final_duration=(end or s.frame_end+1)-start
    st.blend_type='ALPHA_OVER';st.transform.scale_x=scale;st.transform.scale_y=scale;st.transform.offset_x=dx;st.transform.offset_y=dy
    alpha(st,start,st.frame_final_end,fade);return st
def base(i):
    m=manifest[i-1];s=bpy.data.scenes.new('S%02d_SLIDE%d_%s'%(i,m['slide'],m['title'].replace(' ','_').replace('?','')))
    switch(s);set_render(s);s.sequence_editor_create();s.render.use_sequencer=True
    s.frame_end=m['duration_seconds']*FPS
    s['shot_id']=i;s['slide']=m['slide'];s['speaker']=m['speaker'];s['narration']=m['narration'];s['target_duration_seconds']=m['duration_seconds']
    s['hold_instructions']='All IMAGE and TEXT strips may be extended. Motion keys are local to this shot. Rendered tail image is supplied for edit holds.'
    rect(s,'Canvas',960,540,W,H,NAVY,1)
    rect(s,'Header_rule',960,966,1720,2,PANEL,2)
    text(s,'Brand','TEAM 26  /  AI GAME PLAYER',104,1012,25,MUTED,3,fade=0)
    text(s,'Section','%02d  /  %s'%(m['slide'],section_titles[m['slide']-1]),1816,1012,22,MUTED,4,fade=0,align='RIGHT')
    text(s,'Title',m['title'],104,895,60,WHITE,5,fade=30)
    text(s,'Shot','%02d / 17'%i,1816,92,23,MUTED,6,fade=0,align='RIGHT')
    # Continuous, quiet reading progress; not a performance chart.
    p=rect(s,'Reading_progress',104,157,1,3,BLUE,7)
    key(p.transform,'scale_x',1/W,1);key(p.transform,'scale_x',1712/W,s.frame_end)
    key(p.transform,'offset_x',104-W/2,1);key(p.transform,'offset_x',960-W/2,s.frame_end)
    # Reserve camera window at x=1515..1815,y=220..405. Not baked in exported clips.
    return s

def card(s,title,body,x,y,w=400,h=180,c=BLUE,ch=20,start=60,end=None):
    rect(s,title+'_panel',x,y,w,h,PANEL,ch,start,end,30)
    rect(s,title+'_accent',x-w/2+4,y,5,h-30,c,ch+1,start,end,30)
    text(s,title,title,x-w/2+28,y+h/2-43,35,WHITE,ch+2,start,end,30)
    text(s,title+'_body',body,x-w/2+28,y-22,27,MUTED,ch+3,start,end,30)

def board(s,mode='opening',scale=.86,dx=0,dy=0,start=1,end=None,ch=10):
    image(s,'Board_'+mode,plates[mode],ch,start,end,scale,dx,dy)
    if scale==.86 and dx==0:
        text(s,'Human_legend','H  /  Human · circle',353,198,23,BLUE,ch+1,start,end)
        text(s,'AI_legend','AI  /  Opponent · square',635,198,23,ORANGE,ch+2,start,end)
        text(s,'Position_status','Illustrative position',353,824,25,MUTED,ch+3,start,end)
def coords(p,scale=.86,dx=0,dy=0):
    return ((960+(-3.7+(p[0]-4)*.72)*100)*scale+960*(1-scale)+dx,(540+(-.35+(p[1]-4)*.72)*100)*scale+540*(1-scale)+dy)
def route_anim(s,p,g,walls,c,start,ch=40,scale=.86,dx=0,dy=0,name='Route',until=None):
    # Display a valid ordinary-step guide around the other pawn, never through it.
    other=(4,7) if g==8 else (4,1)
    path=route(p,g,walls,avoid=other)
    check('%s shot %s route obeys walls'%(name,s['shot_id']),bool(path))
    for j,(a,b) in enumerate(zip(path,path[1:])):
        x1,y1=coords(a,scale,dx,dy);x2,y2=coords(b,scale,dx,dy)
        st=rect(s,'%s_segment_%02d'%(name,j),(x1+x2)/2,(y1+y2)/2,abs(x2-x1)+5,abs(y2-y1)+5,c,ch+j,start+j*14,until,14)
    # Moving marker follows the exact route continuously, repeating slowly for reading time.
    px,py=coords(path[0],scale,dx,dy)
    marker=rect(s,name+'_traveller',px,py,10,10,c,ch+len(path),start,until,24)
    last=until or s.frame_end+1
    interval=45
    cycle=max(120,(len(path)-1)*interval)
    f=start+len(path)*14+30
    while f<last-30:
        for j,p in enumerate(path):
            ff=f+j*interval
            if ff>=last-1:break
            x,y=coords(p,scale,dx,dy);key(marker.transform,'offset_x',x-W/2,ff);key(marker.transform,'offset_y',y-H/2,ff)
        # Fade between cycles so the marker never moves backward through a wall.
        stop=min(f+(len(path)-1)*interval,last-2)
        key(marker,'blend_alpha',1,stop-10);key(marker,'blend_alpha',0,stop+10)
        if stop+50<last:
            x,y=coords(path[0],scale,dx,dy);key(marker.transform,'offset_x',x-W/2,stop+30);key(marker.transform,'offset_y',y-H/2,stop+30);key(marker,'blend_alpha',0,stop+31);key(marker,'blend_alpha',1,stop+55)
        f+=cycle+80
    ease(marker);ease(marker.transform)
    return path

shots=[]
# 01: opening question, with route revealed and two distinct choices.
s=base(1);shots.append(s);board(s)
route_anim(s,(4,1),8,[],BLUE,90,ch=40,name='Human_goal_guide')
text(s,'Question','What would you do?',1060,724,43,WHITE,20,start=180)
card(s,'Move','Advance one square',1275,570,430,165,BLUE,21,240)
card(s,'Place a wall','Change the routes',1275,365,430,165,ORANGE,25,330)
text(s,'Wall_stock','10 walls each · human to act',1060,238,26,MUTED,29,start=390)

# 02: independent branches; board spatial continuity is preserved.
s=base(2);shots.append(s)
board(s,'clean',scale=.74,dx=-80,dy=-5,ch=10)
image(s,'Human_move',plates['human'],14,1,scale=.74,dx=-80,dy=-5)
human=s.sequence_editor.strips['Human_move'];key(human.transform,'offset_y',-5,75);key(human.transform,'offset_y',-5+72*.74,165);ease(human.transform)
image(s,'AI_stays',plates['ai'],15,1,scale=.74,dx=-80,dy=-5)
board(s,'wall',scale=.74,dx=820,dy=-5,ch=17,start=420)
text(s,'Move_branch','MOVE  /  one legal step',285,804,32,BLUE,21,start=35)
text(s,'Wall_branch','WALL  /  routes change',1185,804,32,ORANGE,22,start=420)
text(s,'Different_futures','Same position. Two possible futures.',104,233,38,WHITE,23,start=620)
text(s,'No_claim','Illustrative alternatives · no claim of an optimal move',104,190,26,MUTED,24,start=620)
text(s,'Wall_inventory','H: 9 walls   /   AI: 10 walls',1265,233,25,MUTED,25,start=720)
route_anim(s,(4,2),8,[],BLUE,220,40,.74,-80,-5,'Move_guide')
route_anim(s,(4,1),8,[('h',4,5)],BLUE,520,60,.74,820,-5,'Wall_human_guide')
route_anim(s,(4,7),0,[('h',4,5)],ORANGE,660,80,.74,820,-5,'Wall_AI_guide')

# 03: product proposition, four sparse outcomes.
s=base(3);shots.append(s);board(s,scale=.78,dx=-100,dy=-5)
for j,(a,b) in enumerate([('Rules-correct','Standard two-player Quoridor'),('MCTS opponent','Decisions under a time limit'),('Selectable difficulty','Calibrated through evaluation'),('Clear handover','Design notes + user manual')]):
    card(s,a,b,1250,720-j*155,620,130,BLUE if j%2==0 else ORANGE,20+j*4,80+j*170)
text(s,'Proposal','PROPOSAL  /  Human versus MCTS AI',104,210,30,MUTED,40,start=90)

# 04: truthful editable team placeholder; domains are work areas, not skill claims.
s=base(4);shots.append(s)
text(s,'Pending','Skills → contribution',104,736,44,ORANGE,10,start=60)
text(s,'No_claim','Proposed work areas · assignments follow confirmed experience.',104,678,31,MUTED,11,start=100)
for j,(a,b) in enumerate([('Rules','Legal movement + walls'),('AI','Search + evaluation'),('GUI + testing','Interface + integration')]):
    card(s,a,b,370+j*590,495,535,210,(BLUE,ORANGE,TEAL)[j],20+j*4,180+j*200)
text(s,'Placeholder_notice','Whole team experience → shared project ownership',104,263,28,MUTED,40,start=850)

# 05: goal / action / path, plus source link.
s=base(5);shots.append(s);board(s)
route_anim(s,(4,1),8,[],BLUE,90,40,name='Goal_route')
for j,(a,b) in enumerate([('01  Goal','Reach the opposite edge'),('02  Your turn','Move OR place one wall'),('03  Keep a path','Both players must retain a route')]):
    card(s,a,b,1305,690-j*190,650,160,(BLUE,ORANGE,TEAL)[j],20+j*4,150+j*430)
text(s,'Reference','Board Game Arena reference',104,112,25,MUTED,35,start=1320)
text(s,'Reference_URL','boardgamearena.com/gamepanel?game=quoridor',510,112,25,MUTED,36,start=1320)

# 06: board gives way to an illustrative tree; four stages take enough time to read.
s=base(6);shots.append(s);board(s,scale=.72,dx=-140,dy=-5)
text(s,'Illustrative','Illustrative search',965,797,28,ORANGE,20,start=70)
nodes=[(1320,690),(1130,535),(1510,535),(1040,375),(1220,375),(1430,375),(1610,375)]
links=[(0,1),(0,2),(1,3),(1,4),(2,5),(2,6)]
for j,(a,b) in enumerate(links):
    x1,y1=nodes[a];x2,y2=nodes[b];length=math.hypot(x2-x1,y2-y1)
    st=rect(s,'Tree_edge_%d'%j,(x1+x2)/2,(y1+y2)/2,length,3,MUTED,25+j,90+j*18,fade=30);st.transform.rotation=math.atan2(y2-y1,x2-x1)
for j,(x,y) in enumerate(nodes):
    rect(s,'Node_%d'%j,x,y,62,45,BLUE if j in (0,1,4) else PANEL,35+j,90+j*22,fade=30)
text(s,'Move_label','Move',1065,590,25,MUTED,43,start=140);text(s,'Wall_label','Wall',1490,590,25,MUTED,44,start=140)
for j,(a,b) in enumerate([('Selection','Follow a promising branch'),('Expansion','Add a legal candidate'),('Simulation','Play out a possible future'),('Backpropagation','Return the result to the tree')]):
    a0=180+j*450;b0=180+(j+1)*450 if j<3 else s.frame_end+1
    card(s,'%02d  %s'%(j+1,a),b,1235,238,770,120,BLUE if j%2==0 else ORANGE,50,a0,b0)
    # A small tree cursor descends then returns; no fictitious scores.
cursor=rect(s,'Search_cursor',1320,690,18,18,ORANGE,60,180,fade=24)
for f,idx in [(180,0),(360,1),(610,4),(1000,4),(1450,1),(1680,0),(1950,0)]:
    x,y=nodes[idx];key(cursor.transform,'offset_x',x-W/2,f);key(cursor.transform,'offset_y',y-H/2,f)
ease(cursor.transform)

# 07: rollout diagrams without a synthetic result.
s=base(7);shots.append(s)
text(s,'Approach','Proposed approach · Illustrative search',104,791,28,ORANGE,10,start=30)
card(s,'Random','Sample legal continuations',500,595,730,300,BLUE,20,90)
card(s,'Route-aware','Use a simple path-distance guide',1350,595,730,300,ORANGE,24,430)
for j,points in enumerate([[(220,550),(310,480),(410,530),(490,450),(640,500)],[(1070,500),(1160,500),(1250,550),(1370,550),(1480,580)]]):
    for k,((x1,y1),(x2,y2)) in enumerate(zip(points,points[1:])):
        st=rect(s,'Rollout_%d_%d'%(j,k),(x1+x2)/2,(y1+y2)/2,math.hypot(x2-x1,y2-y1),4,(BLUE,ORANGE)[j],40+j*6+k,200+j*360+k*30,fade=20);st.transform.rotation=math.atan2(y2-y1,x2-x1)
text(s,'Budget','Bounded move budget',104,322,38,WHITE,60,start=760)
text(s,'Cutoff','Cutoff → documented path-distance estimate',104,265,30,MUTED,61,start=820)
text(s,'Filtering','Profile branching; evaluate candidate filtering if needed',104,211,28,MUTED,62,start=1020)

# 08: architecture plus a precisely validated rejected wall fixture.
s=base(8);shots.append(s);board(s,'fixture',scale=.82,dx=-80,dy=-10,end=1180)
text(s,'Fixture_label','Rule test fixture · rejected preview',190,790,27,ORANGE,14,start=35,end=1140)
x,y=coords((1.5,.5),.82,-80,-10)
bad=rect(s,'Rejected_wall_preview',x,y,9,136*.82,RED,15,450,end=1140,fade=30)
alpha(bad,450,1140,30,True)
text(s,'Reject','×  No route → reject wall',960,297,35,RED,16,start=490,end=1140)
for j,(a,b) in enumerate([('Rules','Legal actions + state transitions'),('AI','Search copied states'),('GUI','Present state + legal feedback')]):
    card(s,a,b,1330,710-j*160,650,135,(TEAL,ORANGE,BLUE)[j],20+j*4,90+j*250)
text(s,'Independent','Independent modules. Independent tests.',960,240,30,MUTED,35,start=1080)
text(s,'Uncommitted','Red wall is a preview only; live state is unchanged.',190,217,25,MUTED,36,start=750,end=1140)
text(s,'Rules_to_AI','↓',970,628,29,MUTED,37,start=370)
text(s,'AI_to_GUI','↓',970,468,29,MUTED,38,start=620)
board(s,'wall',scale=.82,dx=-80,dy=-10,start=1140,ch=11)
text(s,'Valid_fixture','Valid wall · both routes retained',190,790,27,TEAL,39,start=1160)
text(s,'Accept','✓  Both routes retained',960,297,35,TEAL,40,start=1200)
route_anim(s,(4,1),8,[('h',4,5)],BLUE,1210,60,.82,-80,-10,'Valid_human_route')
route_anim(s,(4,7),0,[('h',4,5)],ORANGE,1320,80,.82,-80,-10,'Valid_AI_route')

# 09: concurrent tracks with bounded search visualized by a moving token.
s=base(9);shots.append(s)
for j,(a,b) in enumerate([('Java','Game model'),('JavaFX','Presentation'),('Maven','Builds'),('JUnit','Tests')]):card(s,a,b,330+j*420,725,365,145,(BLUE,TEAL,ORANGE,BLUE)[j],20+j*4,60+j*120)
text(s,'UI_track','Interface',130,517,33,BLUE,40,start=240)
text(s,'AI_track','Background AI',130,360,33,ORANGE,41,start=400)
rect(s,'UI_track_line',1080,517,1230,4,BLUE,42,300,fade=24);rect(s,'AI_track_line',1080,360,1230,4,ORANGE,43,420,fade=24)
text(s,'UI_note','Input · feedback · status',600,569,29,MUTED,44,start=500)
text(s,'AI_note','Copied state → bounded search → legal action',600,414,29,MUTED,45,start=620)
token=rect(s,'Background_work',480,360,22,22,ORANGE,46,720,fade=20)
for f,x in [(720,480),(1020,1040),(1260,1560),(1440,1560)]:key(token.transform,'offset_x',x-W/2,f)
key(token.transform,'offset_y',360-H/2,1260);key(token.transform,'offset_y',517-H/2,1440);ease(token.transform)
text(s,'Isolation','Search never modifies the live board.',130,243,34,WHITE,47,start=1300)

# 10: a self-made proposed GUI, no screenshot or fake application capture.
s=base(10);shots.append(s)
rect(s,'Interface_shell',905,507,1590,570,PANEL,9,40,fade=30)
board(s,scale=.76,dx=-150,dy=-15,ch=10)
text(s,'Interface_label','Proposed interface',955,743,31,ORANGE,14,start=70)
text(s,'Turn','Your turn · human',955,680,40,WHITE,15,start=110)
text(s,'Walls_left','Walls remaining: 10',955,627,28,MUTED,16,start=160)
for j,(a,b) in enumerate([('Legal moves','Clear feedback before committing'),('Wall preview','Valid / invalid + a reason'),('Difficulty','Easy     Medium     Hard')]):card(s,a,b,1240,538-j*120,570,103,BLUE if j!=1 else ORANGE,20+j*4,270+j*430)
xx,yy=coords((4,2),.76,-150,-15);rect(s,'Legal_target',xx,yy,32,32,TEAL,40,270,fade=30)
xx,yy=coords((4.5,5.5),.76,-150,-15);rect(s,'Proposed_valid_wall',xx,yy,136*.76,7,TEAL,41,700,fade=30)
text(s,'Goal_note','An opponent you enjoy playing against.',104,194,31,WHITE,42,start=1450)

# 11: initial budgets labelled provisional, no proven strength claim.
s=base(11);shots.append(s)
text(s,'Provisional','Provisional budgets · to be calibrated',104,790,30,ORANGE,10,start=30)
for j,(a,b) in enumerate([('Easy','0.2 s'),('Medium','0.5 s'),('Hard','1.0 s')]):
    card(s,a,'',385+j*575,575,505,285,(BLUE,TEAL,ORANGE)[j],20+j*4,120+j*330)
    text(s,a+'_value',b,165+j*575,562,68,WHITE,40+j,150+j*330)
    text(s,a+'_budget','Initial search budget',165+j*575,481,27,MUTED,44+j,180+j*330)
text(s,'Calibration','Measure strength + response time → adjust',104,311,39,WHITE,50,start=1060)
text(s,'Not_proven','These values are starting points, not proven difficulty levels.',104,242,29,MUTED,51,start=1150)

# 12: empty measurement checklist, never fabricated bars or win rates.
s=base(12);shots.append(s)
for j,(a,b) in enumerate([('Win rate','Report denominators'),('Move latency','Median + 95th percentile'),('Unfinished games','Report separately')]):card(s,a,b,385+j*575,644,505,220,(BLUE,TEAL,ORANGE)[j],20+j*4,90+j*300)
text(s,'Study_plan','Provisional evaluation: 100 games per matchup',104,438,37,WHITE,40,start=880)
text(s,'Balance','Balanced first-player assignments · specified hardware',104,376,29,MUTED,41,start=960)
text(s,'Baseline','Compare levels + movement-only shortest-path baseline',104,319,29,MUTED,42,start=1100)
text(s,'Tests','Rules + integration tests',104,251,32,TEAL,43,start=1240)
text(s,'Tests_detail','Jumps · blocked paths · conflicts · restart · victory · state isolation',104,201,26,MUTED,44,start=1330)

# 13: original dates retained; no invented sprint schedule.
s=base(13);shots.append(s)
text(s,'Milestones_label','Provisional milestones — subject to supervisor agreement',104,790,29,ORANGE,10,start=30)
rect(s,'Milestone_track',950,552,1540,4,MUTED,15,90,fade=30)
for j,(a,b) in enumerate([('NOV 2026','Playable rules'),('DEC 2026','MCTS baseline'),('FEB 2027','Difficulty evaluation'),('APR 2027','Integrated + documented'),('MAY 2027','Showcase')]):
    x=185+j*385
    rect(s,'Milestone_%d'%j,x,552,17,17,BLUE if j%2==0 else ORANGE,20+j*3,150+j*300,fade=30)
    text(s,'Date_'+str(j),a,x-25,636,30,WHITE,21+j*3,start=150+j*300)
    # Split long milestones deliberately, keeping dates easy to scan.
    body=b.replace('Difficulty evaluation','Difficulty\nevaluation').replace('Integrated + documented','Integrated +\ndocumented')
    text(s,'Deliverable_'+str(j),body,x-25,472,28,MUTED,22+j*3,start=180+j*300)
text(s,'Iteration','Each iteration produces something demonstrable.',104,298,40,WHITE,40,start=1710)
text(s,'Align','Align dates with module deadlines and supervisor advice.',104,232,29,MUTED,41,start=1810)

# 14: work areas, not member skill claims.
s=base(14);shots.append(s)
for j,(a,b) in enumerate([('Rules','Lead + reviewer'),('AI','Lead + reviewer'),('GUI','Lead + reviewer'),('Testing + docs','Lead + reviewer')]):card(s,a,b,330+j*420,649,365,215,(TEAL,ORANGE,BLUE,TEAL)[j],20+j*4,80+j*220)
text(s,'Skills','Assignments follow confirmed team skills.',104,446,33,MUTED,40,start=910)
for j,a in enumerate(['Weekly meetings','Shared backlog','Reviewed PRs']):
    text(s,'Coordination_'+str(j),a,125+j*570,326,37,WHITE,45+j,start=970+j*100)
text(s,'Documentation','Design notes + user manual grow alongside the software.',104,233,31,BLUE,50,start=1260)

# 15: reveal each risk then its mitigation on the same line.
s=base(15);shots.append(s)
for j,(a,b) in enumerate([('Limited MCTS experience','Early prototypes + paired learning'),('Slow search / weak rollouts','Profile + bound + evaluate'),('Integration / coursework','Regular review + shared backlog')]):
    y=718-j*172
    text(s,'Risk_'+str(j),a,130,y,37,ORANGE,20+j*3,start=60+j*330)
    text(s,'Arrow_'+str(j),'→',840,y,42,MUTED,21+j*3,start=170+j*330)
    text(s,'Response_'+str(j),b,945,y,32,WHITE,22+j*3,start=190+j*330)
text(s,'Priority','Priority: a correct, usable two-player game.',130,233,37,TEAL,40,start=1160)

# 16: ethics and support, no accounts, no invented assets.
s=base(16);shots.append(s)
for j,(a,b) in enumerate([('Licensed assets','Original or licensed material'),('No accounts required','No personal-data collection'),('Accessible controls','Clear labels + feedback')]):card(s,a,b,385+j*575,629,505,235,(BLUE,TEAL,ORANGE)[j],20+j*4,90+j*260)
text(s,'Human_testing','Human playtesting → supervisor guidance on consent and ethics',104,417,32,MUTED,40,start=890)
text(s,'Guidance','Guidance from supervisor',104,318,42,WHITE,41,start=1060)
text(s,'Guidance_detail','Search evaluation + game complexity',104,249,32,BLUE,42,start=1130)

# 17: visual return to the exact original position, then three promises.
s=base(17);shots.append(s);board(s)
route_anim(s,(4,1),8,[],BLUE,60,40,name='Return_to_opening')
text(s,'Return','Move, or place a wall?',1000,731,42,WHITE,20,start=90)
for j,a in enumerate(['Rules-correct','Responsive','Evaluated']):card(s,a,['Standard game rules','Clear, usable interface','Explainable evidence'][j],1280,586-j*148,570,125,(TEAL,BLUE,ORANGE)[j],22+j*4,780+j*150)
text(s,'Thank_you','TEAM 26  /  AI Game Player',104,119,30,WHITE,35,start=1570)
s.timeline_markers.new('B → A narration handoff (adjust after recording)',frame=901)
s.timeline_markers.new('Final hold / thank you',frame=1681)

# Save source scenes and native motion graphics together. No scene strips in final edit.
for s in shots:
    for f,name in [(1,'IN'),(31,'Title readable'),(max(31,s.frame_end-120),'Extendable final hold'),(s.frame_end,'OUT')]:s.timeline_markers.new(name,frame=f)
    s.render.filepath='//rendered/shot_%02d.mp4'%s['shot_id']
    s.render.image_settings.media_type='VIDEO'; s.render.image_settings.file_format='FFMPEG';s.render.ffmpeg.format='MPEG4';s.render.ffmpeg.codec='H264'
    for strip in s.sequence_editor.strips:
        if strip.type=='IMAGE':strip.directory=bpy.path.relpath(strip.directory,start=str(ROOT))

for name in ['Production notes','Narration and shot timing']:
    tx=bpy.data.texts.new(name)
    tx.write('All visuals built and rendered in Blender 5.2.2 LTS.\n17 shots / 6 slides / 460 seconds / 1920x1080 / 60 fps.\nSource MODEL scenes contain original geometry; S01–S17 contain editable VSE animation.\nNo performance results, member skills, narration voice or presenter likeness have been generated.\nShot 04 is intentionally pending confirmed team skills.\n\n'+json.dumps(manifest,ensure_ascii=False,indent=2))
switch(shots[0]);bpy.context.scene.frame_set(360)
for screen in bpy.data.screens:
    for area in screen.areas:
        if area.type=='VIEW_3D':area.type='SEQUENCE_EDITOR'
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT/'visuals.blend'))
(ROOT/'qa'/'rules_validation.json').write_text(json.dumps({'official_rulebook':'https://export.gigamic.com/wp-content/uploads/2021/01/INS-RULES-QUORIDOR_10-2016.pdf','checks':checks,'opening_history':['H e1-e2','AI e9-e8'],'route_note':'Graph route guides; not a sequence of played pawn moves.','alternatives':'Independent move/wall alternatives with H to act.','wall_stock':'Opening and move: H10/AI10; wall branch: H9/AI10.','invalid_wall':'Red v(1,0), after h(0,1), seals the corner human route and is only a rejected preview.'},indent=2))
print('BUILD_COMPLETE',ROOT,flush=True)
