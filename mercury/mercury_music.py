import numpy as np, soundfile as sf
from scipy.signal import fftconvolve
SR = 44100; SEC = 30.0; N = int(SR * SEC); t = np.arange(N) / SR; rng = np.random.default_rng(80)
def note(m): return 440.0 * 2 ** ((m - 69) / 12)
CH = [[38, 45, 50, 53, 57], [41, 48, 53, 57, 60], [43, 50, 55, 58, 62], [45, 52, 57, 60, 64], [38, 45, 50, 54, 57]]
bounds = [0, 6, 12, 18, 24, 30]; pad = np.zeros(N)
for b, ch in enumerate(CH):
    t0, t1 = bounds[b], bounds[b + 1]; env = np.clip((t - (t0 - 1.0)) / 1.8, 0, 1) * np.clip((t1 + 1.8 - t) / 2.2, 0, 1)
    for m in ch:
        for det in (-0.1, 0, 0.1): pad += env * np.sin(2 * np.pi * note(m) * (1 + det / 100) * t + rng.random() * 6) / 3
pad *= 0.04
fx = np.zeros(N)
def add(sig, t0):
    i = int(t0 * SR); j = min(i + len(sig), N); fx[i:j] += sig[:j - i]
def tone(f, dur, dec, amp):
    n = int(dur * SR); x = np.arange(n) / SR
    return amp * (np.sin(2 * np.pi * f * x) + 0.3 * np.sin(4 * np.pi * f * x) * np.exp(-x * 3)) * np.exp(-x * dec) * np.minimum(1, x / 0.004)
def sweep(f0, f1, t0, t1, amp):
    n = int((t1 - t0) * SR); x = np.arange(n) / SR; f = f0 * (f1 / f0) ** (x / x[-1]); ph = 2 * np.pi * np.cumsum(f) / SR
    add(amp * np.sin(np.pi * x / x[-1]) ** 2 * np.sin(ph), t0)
def drip(t0, f=900, amp=0.12):
    n = int(0.25 * SR); x = np.arange(n) / SR; ff = f * (1 + 1.5 * np.exp(-x * 40))
    add(amp * np.sin(2 * np.pi * np.cumsum(ff) / SR) * np.exp(-x * 18), t0)
for tp in (0.2, 0.7, 1.3, 1.8): drip(tp, 700 + 200 * rng.random())                       # liquid opening
for tp in np.linspace(2.4, 4.2, 6): add(tone(1318.5, 0.5, 9, 0.05), tp)                   # crystal clicks into place
w = np.convolve(rng.standard_normal(N), np.ones(40) / 40, "same"); fx += 0.6 * w * np.exp(-((t - 5.3) / 0.5) ** 2)   # dive
sweep(220, 880, 6.0, 9.2, 0.10)                                                            # speed builds
add(tone(65.0, 2.0, 2.0, 0.5), 9.6)                                                        # contraction
sweep(880, 330, 16.6, 18.6, 0.09)                                                          # bonds fade
add(tone(1568.0, 0.6, 7.0, 0.05), 17.0)                                                    # cat ping
sweep(700, 250, 20.0, 23.2, 0.10)                                                          # temperature falls
for tp in np.linspace(21.4, 24.4, 9): drip(tp, 600 + 400 * rng.random(), 0.09)             # it melts
for f_, a_ in ((440.0, .22), (554.4, .17), (659.3, .14), (880.0, .09)): add(tone(f_, 4.0, 0.9, a_), 25.4)
add(tone(1046.5, 1.2, 4.0, 0.08), 27.0)
mus = pad + fx
L = int(3.0 * SR); x = np.arange(L) / SR
wl = fftconvolve(mus, rng.standard_normal(L) * np.exp(-x * 1.7))[:N]; wr = fftconvolve(mus, rng.standard_normal(L) * np.exp(-x * 1.7))[:N]
dry = mus / np.abs(mus).max(); st = np.stack([0.6 * dry + 0.4 * wl / np.abs(wl).max(), 0.6 * dry + 0.4 * wr / np.abs(wr).max()], 1)
st *= (np.minimum(1, t / 0.2) * np.minimum(1, (SEC - t) / 1.5))[:, None]; st = st / np.abs(st).max() * 0.85
sf.write("mercury_music.wav", st.astype(np.float32), SR); print("ok")
