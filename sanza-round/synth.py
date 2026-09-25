# Synthesises sanza-round.mp3 from score.json (window.SCORE exported from sanza-round.html).
import json, numpy as np, wave
SR = 44100; LEN = 30; N = SR * (LEN + 2)
rng = np.random.default_rng(3)
L = np.zeros(N); R = np.zeros(N); send = np.zeros(N); drums = np.zeros(N)
hz = lambda m: 440 * 2 ** ((m - 69) / 12)
PAN = {0: -0.35, 1: 0.0, 2: 0.25, 3: -0.15, 4: 0.4, 5: -0.25}
SEND = {0: 0.5, 1: 0.05, 2: 0.35, 3: 0.2, 4: 0.45, 5: 0.5}

def place(sig, t, pan=0.0, wet=0.0):
    s = max(0, int(t * SR)); e = min(N, s + len(sig)); sig = sig[:e - s]
    L[s:e] += sig * np.sqrt(0.5 * (1 - pan)); R[s:e] += sig * np.sqrt(0.5 * (1 + pan)); send[s:e] += sig * wet

def sanza(f, dur, vel, dark=0):
    tt = np.arange(int(max(dur, 1.6) * SR)) / SR
    bend = 1 + 0.012 * np.exp(-tt * 40)
    sig = sum(a * np.sin(2 * np.pi * f * p * np.cumsum(bend) / SR) * np.exp(-tt * d)
              for p, a, d in ((1, 1, 3.2), (5.4, 0.22 / (1 + dark), 16), (8.93, 0.09 / (1 + 2 * dark), 28)))
    buzz = np.tanh(sig * 3) * 0.12 * np.exp(-tt * 9)  # the rattle on a real sanza
    return (sig + buzz) * np.minimum(tt / 0.002, 1) * 0.16 * vel

def voice(vi, f, dur, vel):
    if vi == 0: return sanza(f, dur, vel)
    tt = np.arange(int((dur + 0.6) * SR)) / SR
    gate = np.interp(tt, [0, 0.008, dur, dur + 0.08], [0, 1, 1, 0])
    if vi == 1:  # dub bass: round sine, a touch of second harmonic, soft saturation
        sig = np.tanh(1.6 * (np.sin(2 * np.pi * f * tt) + 0.18 * np.sin(4 * np.pi * f * tt))) * 0.34
        return sig * np.interp(tt, [0, 0.006, dur * 0.9, dur + 0.12], [0, 1, 0.8, 0]) * vel
    if vi == 2:  # Rhodes: FM with a bright attack that mellows
        idx = 1.6 * np.exp(-tt * 6) + 0.25
        sig = np.sin(2 * np.pi * f * tt + idx * np.sin(2 * np.pi * f * tt)) * np.exp(-tt * 2.2)
        return sig * (1 + 0.12 * np.sin(2 * np.pi * 4.5 * tt)) * np.interp(tt, [0, 0.003, dur + 0.3, dur + 0.6], [0, 1, 1, 0]) * 0.09 * vel
    if vi == 3:  # organ: drawbars 16' 8' 4' 2 2/3' 2' with a slow Leslie wobble
        wob = 1 + 0.003 * np.sin(2 * np.pi * 6.2 * tt)
        sig = sum(a * np.sin(2 * np.pi * f * h * np.cumsum(wob) / SR) for h, a in ((0.5, .6), (1, 1), (2, .6), (3, .3), (4, .25)))
        return sig * gate * 0.028 * vel
    if vi == 4:  # flute: sine, breath noise, delayed vibrato
        vib = 1 + 0.006 * np.sin(2 * np.pi * 5.2 * tt) * np.clip((tt - 0.15) * 4, 0, 1)
        ph = 2 * np.pi * f * np.cumsum(vib) / SR
        breath = np.convolve(rng.standard_normal(len(tt)), np.ones(8) / 8, 'same') * 0.18
        env = np.interp(tt, [0, 0.06, dur, dur + 0.1], [0, 1, 0.85, 0])
        return (np.sin(ph) + 0.15 * np.sin(2 * ph) + breath * (0.4 + 0.6 * np.exp(-tt * 10))) * env * 0.075 * vel
    if vi == 5:  # bells
        sig = sum(a * np.sin(2 * np.pi * f * p * tt) * np.exp(-tt * d) for p, a, d in ((1, 1, 1.8), (2, .5, 3), (3, .3, 4.5), (4.16, .2, 6), (5.43, .12, 8)))
        return sig * np.minimum(tt / 0.002, 1) * 0.045 * vel

def kick(vel):
    tt = np.arange(int(0.45 * SR)) / SR; f = 48 + 75 * np.exp(-tt * 25)
    sig = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 7) + np.exp(-tt * 300) * 0.4
    return np.tanh(sig * 1.5) * 0.7 * vel
def snare(vel):
    tt = np.arange(int(0.35 * SR)) / SR
    n = np.convolve(rng.standard_normal(len(tt)), [1, -0.6], 'same')
    return (n * np.exp(-tt * 17) * 0.5 + np.sin(2 * np.pi * 186 * tt) * np.exp(-tt * 28) * 0.5) * 0.5 * vel
def hat(vel, open_):
    tt = np.arange(int((0.5 if open_ else 0.08) * SR)) / SR
    n = np.diff(rng.standard_normal(len(tt) + 1))
    return n * np.exp(-tt * (8 if open_ else 55)) * 0.07 * vel

score = json.load(open('score.json'))
for e in score:
    t, ty, v = e['t'], e['type'], e['vel']
    if ty == 'note':
        vi = e['voice']; place(voice(vi, hz(e['pitch']), e['dur'], v), t, PAN[vi], SEND[vi])
    elif ty == 'throw':  # dub echo: the last thumb-piano note repeating and darkening
        for k in range(7):
            sig = sanza(hz(e['pitch']), 0.4, v * 0.62 ** k, dark=k)
            sig = np.convolve(sig, np.ones(1 + 3 * k) / (1 + 3 * k), 'same')
            place(sig, t + k * 0.469, -0.35 + 0.12 * k, 0.6)
    else:
        sig = kick(v) if ty == 'kick' else snare(v) if ty == 'snare' else hat(v, e.get('open'))
        s = int(t * SR); ee = min(N, s + len(sig)); drums[s:ee] += sig[:ee - s]
        if ty == 'snare' and v > 0.5: send[s:ee] += sig[:ee - s] * 0.15
        if e.get('echo'):
            for k in range(1, 6):
                d = np.convolve(sig, np.ones(2 + 4 * k) / (2 + 4 * k), 'same') * 0.55 ** k
                s2 = s + int(k * 0.469 * SR); e2 = min(N, s2 + len(d))
                L[s2:e2] += d[:e2 - s2] * (0.8 if k % 2 else 0.3); R[s2:e2] += d[:e2 - s2] * (0.3 if k % 2 else 0.8)
                send[s2:e2] += d[:e2 - s2] * 0.5

# Drums through a dusty sampler: 12-bit, half sample rate, rounded top end.
drums = np.round(drums * 2048) / 2048
drums[1::2] = drums[0::2][:len(drums[1::2])]
drums = np.tanh(np.convolve(drums, np.ones(3) / 3, 'same') * 1.3)
L += drums * 0.9; R += drums * 0.9

# Spring reverb: short metallic combs, then diffusion.
def comb(x, ms, g):
    k = int(ms * SR / 1000); y = x.copy()
    for s in range(k, len(y), k): y[s:s + k] += g * y[s - k:s][:len(y[s:s + k])]
    return y
spring = sum(comb(send, ms, 0.8) for ms in (23.1, 27.7, 31.3, 36.9)) / 4
spring = np.convolve(spring, np.ones(5) / 5, 'same') * 0.5
L += spring; R += np.roll(spring, 400)

# Vinyl: a low hiss and sparse crackle, louder at the start and in the tail.
tt = np.arange(N) / SR
surface = np.interp(tt, [0, 3, 5, 27, 30, 32], [1, 1, 0.45, 0.45, 1, 1])
hiss = np.convolve(rng.standard_normal(N), np.ones(12) / 12, 'same') * 0.004
clicks = np.zeros(N); idx = rng.choice(N, 260, replace=False); clicks[idx] = rng.uniform(-1, 1, 260) * 0.12
clicks = np.convolve(clicks, [1, 0.5, 0.2], 'same')
L += (hiss + clicks) * surface; R += (np.roll(hiss, 91) + np.roll(clicks, 37)) * surface

st = np.stack([L, R], 1)[:SR * LEN]
st = np.tanh(st * 1.2) / 1.2
fade = np.interp(np.arange(len(st)) / SR, [0, 0.05, LEN - 0.8, LEN], [0, 1, 1, 0])[:, None]
st = st * fade; st = st / np.abs(st).max() * 0.89
w = wave.open('sanza-round.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((st * 32767).astype('<i2').tobytes()); w.close()
