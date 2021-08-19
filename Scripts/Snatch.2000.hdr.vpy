import vapoursynth as vs
import awsmfunc as awf
import fvsfunc as fvf
import vsutil
from adptvgrnMod import adptvgrnMod
core = vs.get_core()

src = core.lsmas.LWLibavSource(
    r'Snatch.2000.REPACK.UHD.BluRay.2160p.TrueHD.Atmos.7.1.HEVC.REMUX-FraMeSToR.mkv.h265')
src = core.std.Crop(src, top=42, bottom=42)

# Finding new height
nh = round(1920 / src.width / 2 * src.height) * 2
# resizing
src = core.resize.Spline36(src, 1920, nh, dither_type='error_diffusion')

# Dithering to 16 bit depth
src = vsutil.depth(src, 16)

# Extracting luma plane
luma = vsutil.get_y(src)

# Finding retinex across luma plain so that our mask maintains color constancy
ret = core.retinex.MSRCP(luma, sigma=[50, 200, 350], upper_thr=0.005)

# Sobel mask across horizontal direction
sx = core.std.Convolution(ret, [-1, -2, -1, 0, 0, 0, 1, 2, 1], saturate=False)
# Sobel mask across vertical direction
sy = core.std.Convolution(ret, [-1, 0, 1, -2, 0, 2, -1, 0, 1], saturate=False)
# Finding the magnitude of the retinex sobel mask
res = core.std.Expr([sx, sy], 'x dup * y dup * +')

# Finding the depth of the luma plane
depth = vsutil.get_depth(luma)

# Maximum bit value the luma plane can have
maxval = (1 << depth)-1

# Finding edges using canny edge detection operator
canny = core.tcanny.TCanny(luma, mode=1, sigma=1)

# Adding retinex sobel edge detection max to canny edge detection mask and clamping it to the maximum bit it can have
mask = core.std.Expr([res, canny], f'x y + {maxval} min')

# Minimizing the mask
mask = core.std.Minimum(mask, coordinates=[1, 0, 1, 0, 0, 1, 0, 1])

# Inverting the mask so that the water is represented as black since I want the deband filter to be strongest on the water
mask = core.std.Invert(mask)

# Debanding
deband = core.neo_f3kdb.Deband(src, y=48, cr=45, cb=45, grainy=20,
                               grainc=20, dynamic_grain=False, keep_tv_range=True, output_depth=16)

# Deblocking and for better compression
deband = adptvgrnMod(deband, strength=0.50, size=0.60, sharp=50, static=False,
                     luma_scaling=40, grain_chroma=True, grainer=None, show_mask=False)

# Finally applying the deband filter based on our mask for darker scenes our deband filter will be strongest
src = core.std.MaskedMerge(deband, src, mask)

# Only applying filtering for frames 133868-134214
src = fvf.rfs(src, deband, "[133868 134214]")

# Dithering back to 10 bit depth
src = vsutil.depth(src, 10, dither_type='error_diffusion')


# Final output
src.set_output()
