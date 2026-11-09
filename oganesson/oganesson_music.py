import numpy as np, soundfile as sf
from scipy.signal import fftconvolve
SR = 44100; SEC = 30.0; N = int(SR * SEC); t = np.arange(N) / SR; rng = np.random.default_rng(118)
def note(m): return 440.0 * 2 ** ((m - 69) / 12)
CH = [[45, 52, 57, 60, 64], [45, 52, 57, 60, 64], [41, 48, 53, 57, 60], [43, 50, 55, 59, 62], [40, 47, 52, 56, 59], [38, 45, 50, 53, 57], [45, 52, 57, 61, 64]]
bounds = [0, 2.45, 7.3, 12.3, 17.7, 21.8, 25.6, 30]; pad = np.zeros(N)
for b in range(len(CH)):
    t0, t1 = bounds[b], bounds[b + 1]; env = np.clip((t - (t0 - 0.8)) / 1.3, 0, 1) * np.clip((t1 + 1.3 - t) / 1.6, 0, 1)
    if b == 0: env = np.clip(t / 0.03, 0, 1) * np.clip((2.45 - t) / 0.1, 0, 1)
    for m in CH[b]:
        for det in (-0.12, 0, 0.12): pad += env * np.sin(2 * np.pi * note(m) * (1 + det / 100) * t + rng.random() * 6) / 3
pad *= 0.035
fx = np.zeros(N)
def add(sig, t0):
    i = int(t0 * SR); j = min(i + len(sig), N); fx[i:j] += sig[:j - i]
def tone(f, dur, dec, amp):
    n = int(dur * SR); x = np.arange(n) / SR
    return amp * (np.sin(2 * np.pi * f * x) + 0.3 * np.sin(4 * np.pi * f * x) * np.exp(-x * 3)) * np.exp(-x * dec) * np.minimum(1, x / 0.004)
add(tone(55.0, 2.5, 1.3, 0.55), 0.02); add(tone(note(76), 2.5, 1.4, 0.12), 0.03)
add(tone(41.2, 2.0, 1.5, 0.5), 1.3)                                    # "and Einstein melts it"
n = int(0.5 * SR); x = np.arange(n) / SR; add(0.45 * np.convolve(rng.standard_normal(n), np.ones(8) / 8, "same") * (x / 0.5) ** 3, 1.95)
# electrons speed up: a rising shimmer
shim = np.sin(2 * np.pi * np.cumsum(600 + 900 * np.clip((t - 7.4) / 2.6, 0, 1)) / SR) * 0.03 * np.clip((t - 7.4) / 0.6, 0, 1) * np.clip((12.4 - t) / 0.6, 0, 1)
fx += shim * (1 + 0.5 * np.sin(2 * np.pi * 7 * t))
# melting: a slow detuned swell
melt = sum(np.sin(2 * np.pi * note(57) * (1 + d / 100) * t) for d in (-1.5, -0.6, 0.4, 1.3)) * 0.03 * np.clip((t - 12.3) / 3, 0, 1) * np.clip((17.8 - t) / 0.8, 0, 1)
fx += melt
add(tone(2349.0, 0.6, 7.0, 0.05), 16.0); add(tone(1760.0, 0.6, 7.0, 0.035), 16.12)          # the hidden tile
for k in range(5): add(tone(note(88), 0.25, 14, 0.05), 21.9 + k * 0.6)                        # 5 atoms, 5 ticks
for f_, a_ in ((note(57), .15), (note(64), .12), (note(73), .08)): add(tone(f_, 4.0, 0.9, a_), 25.6)
mus = pad + fx
L = int(3.2 * SR); x = np.arange(L) / SR
wl = fftconvolve(mus, rng.standard_normal(L) * np.exp(-x * 1.5))[:N]; wr = fftconvolve(mus, rng.standard_normal(L) * np.exp(-x * 1.5))[:N]
dry = mus / np.abs(mus).max(); st = np.stack([0.6 * dry + 0.4 * wl / np.abs(wl).max(), 0.6 * dry + 0.4 * wr / np.abs(wr).max()], 1)
st *= (np.minimum(1, t / 0.03) * np.minimum(1, (SEC - t) / 1.5))[:, None]; st = st / np.abs(st).max() * 0.85
sf.write("oganesson_music.wav", st.astype(np.float32), SR); print("ok")
