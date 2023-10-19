####

path_to_current = '/home/surtur/me/else/projs/code/src/automata/current'
path_to_imgs = '/home/surtur/me/atma_imgs/0_io_wip'

####

import sys, webp, random
from PIL import Image, ImageFilter, ImageEnhance
import blend_modes as bm
import numpy as np

sys.path.append('lib')
import functions as f
import scroll_sky as ssk
import scroll_sun as ssu
import _wave

sys.path.append(path_to_current)
from libraries.general.img import manipulate as manip
from libraries.general._math.interpolate import int_across_list

####

global rn
rn = random.SystemRandom()

##

rainbow = Image.open('imgs/rainbow.png')
rainbow_left = Image.open('imgs/rainbow_left.png')
rainbow_right = Image.open('imgs/rainbow_right.png')

mtns = Image.open('imgs/mtns.png')
mtns_water = Image.open('imgs/mtns_water.png')
concrete = Image.open('imgs/concrete.png')
rain = [Image.open(f'imgs/rain/{x}.png') for x in range(5)]
clouds = Image.open('imgs/clouds.png')
clouds_water = Image.open('imgs/clouds_water.png')

birds25 = [Image.open(f'{path_to_imgs}/input/archive/gliders/{x}.png').resize((25,25),resample=0) for x in range(4)]
birds20 = [Image.open(f'{path_to_imgs}/input/archive/gliders/{x}.png').resize((20,20),resample=0) for x in range(4)]
birds15 = [Image.open(f'{path_to_imgs}/input/archive/gliders/{x}.png').resize((15,15),resample=0) for x in range(4)]

frames_n = 60
img_size = (1080,1080)
shift = 40
roll = 27
duration = 125
fps = 6 #8
wave_amp = 15
wave_len = 27
sun_radius = 432

sun_rot = 360/15

save_frames = 0
redo_wave_buildings = False
redo_skys_water = False

def _bird20_coords(coords, pt, terms):
	lx, ly = coords[-1] # last_coord

	dx = int_across_list(pt[0]-lx, 15)
	dy = int_across_list(pt[1]-ly, 15)

	for t in range(terms):
		lx += dx[t]
		ly += dy[t]
		coord = (lx, ly)
		coords.append(coord)

	return coords

def construct():
	sw_i = 0 # sky_water_index

	bird_delta = img_size[0]//30
	bird25_coords = [(1080-x*bird_delta, 324) for x in range(30)]
	bird20_coords = [(1080-x*bird_delta+25, 324+25) for x in range(30)][:15]
	l = bird20_coords[-1]
	bird20_coords = _bird20_coords(bird20_coords, (l[0]-100,l[1]+50), 15)
	bird15_coords = [(1080-x*bird_delta+50, 324+50) for x in range(30)]

	bird20_sizes = [20]*15
	a = int_across_list(20, 15)
	b = 20
	for i in range(15):
		bird20_sizes.append(b)
		b -= a[i]

	_wave.gold(frames_n,img_size[0],mtns_water,'mtns_water_wave',2,5,False)
	f.skys_water_construct(redo_skys_water,'skys_water',img_size)

	_wave.gold(frames_n,img_size[0],rainbow_left,'rainbow_left_wave',4,10,False)
	_wave.gold(frames_n,img_size[0],rainbow_right,'rainbow_right_wave',4,10,False)
	mtns_bg = Image.open('imgs/mtns_bg.png')
	mtns_bg = manip.new_alpha_w_alpha_mask(mtns_bg,40)
	mtns_bg_water = Image.open('imgs/mtns_bg_water.png')
	_wave.gold(frames_n,img_size[0],mtns_bg_water,'mtns_bg_water_wave',4,10,False)
	_wave.gold(frames_n,img_size[0],clouds_water,'clouds_water_wave',4,10,False)

	# rain_intensity
	ri = [0,15,30,45]
	for i in range(4):
		ri = ri + ri[::-1][1:]

	ri = ri + [15, 30, 45, 30, 15, 0, 15, 30, 45, 30, 15]

	ri = ri[:30] + [0]*30

	# sky_rainbow_left_opacities
	srlo = [.2]*25 + [(.2/4)*x for x in range(5)][::-1] + [0]*25 + [(.2/4)*x for x in range(5)]
	srro = [.12]*25 + [(.12/4)*x for x in range(5)][::-1] + [0]*25 + [(.12/4)*x for x in range(5)]
	wrlo = [.1]*25 + [(.1/4)*x for x in range(5)][::-1] + [0]*25 + [(.1/4)*x for x in range(5)]
	wrro = [.22]*25 + [(.22/4)*x for x in range(5)][::-1] + [0]*25 + [(.22/4)*x for x in range(5)]

	# rain_img opacities
	rio = [.33]*25 + [(.33/4)*x for x in range(5)][::-1] + [0]*25 + [(.33/4)*x for x in range(5)]
	# water_tint_opacities
	wto = [1]*25 + [1 - (.5/4)*x for x in range(5)] + [.5]*25 + [.5 + (.5/4)*x for x in range(5)]
	# cloud_values
	cv = [25]*25 + [((225-25)/4)*x+25 for x in range(5)] + [225]*25 + [225-((225-25)/4)*x for x in range(5)]

	frames = []
	for i in range(frames_n):
		print(f'frame:{i+1} of {frames_n}...',end='\r')
		base = Image.new('RGBA',img_size)

		# sky
		sky = Image.open(f'imgs/skys_water/skys_use/{sw_i%4}.png')
		base_sky = Image.new('RGBA',img_size)
		base_sky.paste(sky,mask=sky)

		#base_sky.paste(mtns_bg,mask=mtns_bg)
		#base_sky = f.blend(base_sky, mtns_bg, func=bm.overlay,opacity=.5)
		base_sky.alpha_composite(mtns_bg)
		base_sky = f.blend(base_sky, rainbow_right, coords=(0,0), func=bm.addition, times=1, opacity=srro[i])
		base_sky = f.blend(base_sky, rainbow_left, coords=(0,0), func=bm.soft_light, times=1, opacity=srlo[i])
		#base_sky = f.blend(base_sky, mtns, coords=(0,0), func=bm.soft_light, times=1, opacity=1)
		base_sky.paste(mtns,mask=mtns)

		if i > frames_n//2:
			bird25 = manip.pil_flip(birds25[i%4],['left_right'])
			a = bird20_sizes[i%30]
			bird20 = manip.pil_flip(birds20[i%4].resize((a,a),resample=0),['left_right'])
			bird15 = manip.pil_flip(birds15[i%4], ['left_right'])
			base_sky.paste(bird25,bird25_coords[i%30],mask=bird25)
			base_sky.paste(bird20,bird20_coords[i%30],mask=bird20)
			base_sky.paste(bird15,bird15_coords[i%30],mask=bird15)

		clouds_valueImg = Image.new('RGBA',img_size,(int(cv[i]),)*3+(255,))
		clouds_use = Image.new('RGBA',img_size)
		clouds_use.paste(clouds_valueImg,mask=clouds)
		clouds_blur = manip.pil_blur(clouds_use, radius=9)
		#base_sky.alpha_composite(clouds_blur)
		#base_sky.paste(clouds_blur,mask=clouds_blur)
		if cv[i] < 127:
			base_sky = f.blend(base_sky,clouds_blur,func=bm.darken_only)
		else:
			base_sky = f.blend(base_sky,clouds_blur,func=bm.lighten_only)

		_rain_img = Image.new('RGBA',(1080,540),(ri[i],ri[i],255))
		rain_img = Image.new('RGBA',img_size,(0,0,0,0))
		rain_img.paste(_rain_img,mask=_rain_img)
		base_sky = f.blend(base_sky, rain_img, coords=(0,0), func=bm.hard_light, times=1, opacity=rio[i])

		# water
		water = Image.open(f'imgs/skys_water/water_use/{sw_i%4}.png')
		base_water = Image.new('RGBA',img_size)
		base_water.paste(water,(0,0),mask=water)

		mtns_u = Image.open(f'imgs/mtns_water_wave/{i:04}.png').convert('RGBA')

		mtns_bg_water = Image.open(f'imgs/mtns_bg_water_wave/{i:04}.png').convert('RGBA')
		mtns_bg_water = manip.new_alpha_w_alpha_mask(mtns_bg_water,60)
		#base_water.paste(mtns_bg_water,mask=mtns_bg_water)
		base_water.alpha_composite(mtns_bg_water)
		#base_water = f.blend(base_water, mtns_bg_water, func=bm.difference,opacity=.5)
		base_water.paste(mtns_u, mask=mtns_u)

		rainbow_leftWater = manip.pil_flip(Image.open(f'imgs/rainbow_left_wave/{i:04}.png').convert('RGBA'), ['top_bottom'])
		rainbow_rightWater = manip.pil_flip(Image.open(f'imgs/rainbow_right_wave/{i:04}.png').convert('RGBA'), ['top_bottom'])
		base_water = f.blend(base_water, rainbow_rightWater, coords=(0,0), func=bm.soft_light, times=1, opacity=wrro[i])
		base_water = f.blend(base_water, rainbow_leftWater, coords=(0,0), func=bm.soft_light, times=1, opacity=wrlo[i])

		_water_clouds = Image.open(f'imgs/clouds_water_wave/{i:04}.png').convert('RGBA')
		water_clouds = Image.new('RGBA',img_size)
		water_clouds.paste(clouds_valueImg,mask=_water_clouds)
		#water_cloudsBlur = manip.pil_flip(clouds_blur,['top_bottom'])
		#water_cloudsBlur = manip.pil_blur(water_clouds, radius=9)
		water_cloudsBlur = water_clouds
		if cv[i] < 127:
			base_water = f.blend(base_water,water_cloudsBlur,func=bm.hard_light, opacity=.5)
		else:
			base_water = f.blend(base_water,water_cloudsBlur,func=bm.lighten_only, opacity=.25)

		# together
		base.paste(base_water,(0,0),mask=base_water)
		base.paste(base_sky,mask=base_sky)
		#base.paste(concrete,mask=concrete)

		_water_tint = Image.new('RGBA',(1080,540),(255,0,255,255))
		water_tint = Image.new('RGBA',img_size,(0,0,0,0))
		water_tint.paste(_water_tint,(0,540),mask=_water_tint)
		base = f.blend(base, water_tint, func=bm.darken_only, opacity=wto[i])

		sw_i = (sw_i + 1)%15 if i%4 == 0 else sw_i

		if save_frames:
			base.save(f'imgs/frames/original/{i:04}.png')
		frames.append(base)

	return frames

frames = construct()
print()
print('Making gif...')
f.make_gif(frames,duration)
#print('Making webp...')
#webp.save_images(frames, 'a.webp', fps=fps, lossless=True)
