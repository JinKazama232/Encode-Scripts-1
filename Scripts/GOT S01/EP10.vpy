import vapoursynth as vs
import awsmfunc as awf
from vapoursynth import core


src = core.lsmas.LWLibavSource(
    r'E:\Game.of.Thrones.S01E10.Fire.and.Blood.2160p.TrueHD.Atmos.7.1.DV.HEVC.REMUX-FraMeSToR_Video01.h265')
src = core.resize.Spline36(src, 1920, 1080, dither_type='error_diffusion')
#src = awf.SelectRangeEvery(clip=src, every=3000, length=50, offset=10000)
src.set_output()
