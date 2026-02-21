import math

def generate_wave(wave_type, cycles, amplitude, steps):
    result = []
    for i in range(steps):
        p = (i/(steps-1))*cycles*math.pi*2 if steps>1 else 0
        if wave_type==0: v=(math.sin(p-math.pi/2)+1)/2*amplitude
        elif wave_type==1: v=amplitude if math.sin(p)>=0 else 0
        elif wave_type==2: v=((i*cycles/steps)%1)*amplitude
        else: v=(1-abs(((i*cycles/steps)%1)*2-1))*amplitude
        result.append(int(v))
    return result

def smooth_array(arr, n):
    r = list(arr)
    for i in range(1, n-1): r[i] = int(arr[i-1]*0.25 + arr[i]*0.5 + arr[i+1]*0.25)
    return r
