# Synthesises dawn-set.m4a from score.json (window.SCORE exported from dawn-set.html).
import json, numpy as np, wave
SR=44100; T=31; N=SR*T
rng=np.random.default_rng(7)
dry=np.zeros(N); send=np.zeros(N); arpbus=np.zeros(N); duck=np.ones(N)
hz=lambda m: 440*2**((m-69)/12)
def place(buf,t,sig):
    s=int(t*SR); e=min(N,s+len(sig)); buf[s:e]+=sig[:e-s]
def tone(f,dur,harm,roll=1.0,det=0.0):
    tt=np.arange(int(dur*SR))/SR; out=np.zeros_like(tt)
    for n in range(1,harm+1): out+=np.sin(2*np.pi*f*n*2**(det/1200)*tt+n)/n**roll
    return tt,out
score=json.load(open('score.json'))
for e in score:
    ty,t,v=e['type'],e['t'],e['vel']
    if ty=='kick':
        tt=np.arange(int(0.45*SR))/SR; f=45+85*np.exp(-tt*28)
        ph=2*np.pi*np.cumsum(f)/SR; sig=np.sin(ph)*np.exp(-tt*6.5)*0.9*v
        sig[:60]+=np.linspace(0.3,0,60); place(dry,t,sig)
        s=int(t*SR); k=np.arange(int(0.4*SR))/SR; e2=min(N,s+len(k))
        duck[s:e2]=np.minimum(duck[s:e2],(1-0.65*np.exp(-k*9))[:e2-s])
    elif ty=='hat':
        n=np.diff(rng.standard_normal(int(0.09*SR)+1)); tt=np.arange(len(n))/SR
        place(dry,t,n*np.exp(-tt*55)*0.05*v)
    elif ty=='clap':
        n=rng.standard_normal(int(0.25*SR)); n=np.diff(np.concatenate([[0],np.convolve(n,np.ones(4)/4,'same')]))
        tt=np.arange(len(n))/SR; env=np.exp(-tt*16)
        for o in (0.0,0.011,0.023): env+=np.where(tt>=o,np.exp(-(tt-o)*120),0)*0.6
        sig=n*env*0.22*v; place(dry,t,sig); place(send,t,sig*0.8)
    elif ty=='bass':
        tt,sig=tone(hz(e['pitch']),e['dur']+0.05,8,1.6)
        env=np.minimum(tt/0.004,1)*np.exp(-tt*9); place(dry,t,sig*env*0.28*v)
    elif ty=='arp':
        tt,a=tone(hz(e['pitch']),0.35,1)
        sq=a+0.33*np.sin(2*np.pi*hz(e['pitch'])*3*tt)+0.2*np.sin(2*np.pi*hz(e['pitch'])*5*tt)
        env=np.minimum(tt/0.003,1)*np.exp(-tt*16); place(arpbus,t,sq*env*0.07*v)
    elif ty=='pad':
        for m in e['pitch']:
            for d in (-8,0,8):
                tt,sig=tone(hz(m),e['dur']+0.6,6,1.4,d)
                env=np.interp(tt,[0,0.35,e['dur'],e['dur']+0.6],[0,1,1,0])
                place(send,t,sig*env*0.012*v); place(dry,t,sig*env*0.018*v)
    elif ty=='stab':
        dur=e['dur']; dec=1.3 if dur>1 else 5
        for m in e['pitch']:
            tt=np.arange(int((dur+1.5)*SR))/SR; f=hz(m); sig=np.zeros_like(tt)
            for n,a in ((1,1),(2,0.5),(3,0.25),(4,0.15),(5,0.08),(6,0.05)):
                sig+=a*np.sin(2*np.pi*f*n*tt)*np.exp(-tt*dec*(1+0.4*n))
            sig*=np.minimum(tt/0.002,1)*0.05*v; place(dry,t,sig); place(send,t,sig*0.7)
    elif ty=='riser':
        n=rng.standard_normal(int(e['dur']*SR)); tt=np.arange(len(n))/SR; u=tt/e['dur']
        lo=np.convolve(n,np.ones(24)/24,'same'); hi=np.diff(np.concatenate([[0],n]))
        sig=(lo*(1-u)+hi*u*0.5)*u**2*0.35; place(dry,t,sig); place(send,t,sig)
# arp: dotted-eighth echo with darkening feedback
d=int(0.375*SR); echo=arpbus.copy()
for i in range(1,6):
    tap=np.zeros(N); tap[d*i:]=arpbus[:-d*i]; tap=np.convolve(tap,np.ones(3*i)/(3*i),'same'); echo+=tap*0.42**i
send+=echo*0.6; dry+=echo
# reverb: parallel combs then allpass
def comb(x,ms,g):
    k=int(ms*SR/1000); y=x.copy()
    for s in range(k,len(y),k): y[s:s+k]+=g*y[s-k:s][:len(y[s:s+k])]
    return y
rev=sum(comb(send,ms,0.72) for ms in (29.7,37.1,41.1,43.7))/4
rev=np.convolve(rev,np.ones(6)/6,'same')
# sidechain: the mix ducks under each kick
mix=dry*(0.55+0.45*duck)+rev*0.55*duck
mix=np.tanh(mix*1.4)/1.4
mix=mix[:SR*30]; tt=np.arange(len(mix))/SR; mix*=np.interp(tt,[0,0.05,29.2,30],[0,1,1,0])
mix=mix/np.abs(mix).max()*0.89
st=np.stack([mix+0.12*np.roll(echo[:SR*30],220)/max(1e-9,np.abs(echo).max()), mix-0.12*np.roll(echo[:SR*30],-220)/max(1e-9,np.abs(echo).max())],1)
st=st/np.abs(st).max()*0.89
w=wave.open('ds.wav','wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((st*32767).astype('<i2').tobytes()); w.close(); print('ok')
