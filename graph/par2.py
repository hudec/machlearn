import ipyparallel as ipp
#from timeit import default_timer as clock
import sys, time
import signal
from contextlib import contextmanager

class TimeoutException(Exception): pass

@contextmanager
def time_limit(seconds):
    def signal_handler(signum, frame):
        raise Exception("Timed out!")
    signal.signal(signal.SIGALRM, signal_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)

PROF_DATA = {}

def profile(fn):
#     @wraps(fn)
    def with_profiling(*args, **kwargs):
        start_time = time.time()
        ret = fn(*args, **kwargs)
        elapsed_time = time.time() - start_time
        if fn.__name__ not in PROF_DATA:
            PROF_DATA[fn.__name__] = [0, []]
        PROF_DATA[fn.__name__][0] += 1
        PROF_DATA[fn.__name__][1].append(elapsed_time)
        return ret
    return with_profiling

def print_prof_data():
    for fname, data in PROF_DATA.items():
        max_time = max(data[1])
        avg_time = sum(data[1]) / len(data[1])
        print("Function %s called %d times." % (fname, data[0]))
        print('Execution time max: %.3f, average: %.3f' % (max_time, avg_time))
        n_1, n_10, n_20, n_30, n_40 = 0, 0, 0, 0, 0
        for et in data[1]:
            if et >= 40:
                n_40 += 1
            elif et >= 30:
                n_30 += 1
            elif et >= 20:
                n_20 += 1
            elif et >= 10:
                n_10 += 1
            elif et >= 1:
                n_1 += 1
        print('40', n_40)
        print('30', n_30)
        print('20', n_20)
        print('10', n_10)
        print('1', n_1)
        #print('Time series', data[1])

def clear_prof_data():
    global PROF_DATA
    PROF_DATA = {}

ABCD = [0, 1, 3, 4]
# PREDPIS = {0 : [0, 3], 1 : [4, 3], 3 : [1], 4: [0, 1]}

# danou posloupnost prodlouzi o jednu iteraci - kazde cislo posle na svuj obraz
def iteruj_posloupnost(posloupnost, predpis):
    novy = []
    for p in posloupnost:
        novy.extend(predpis[p])
    return novy

# pro zadane pocatecni cislo a pocet iteraci vytvori posloupnost
def vytvor_posloupnost(pocet, predpis):
    posloupnost = None
    for k in predpis.keys():
        if k == predpis[k][0]:
            posloupnost = [k]
            break
    if posloupnost == None:
        raise ValueError('predpis nema zacatek', predpis)
    for _ in range(pocet):
        posloupnost = iteruj_posloupnost(posloupnost, predpis)
    return posloupnost

# print(vytvor_posloupnost(5, PREDPIS))

# secte dany usek posloupnosti
def secti_usek(posloupnost, c1, c2):
    soucet = 0
    for i in range(c1, c2):
        soucet = soucet + posloupnost[i]
    return soucet      

# zkontroluje, zda se v posloupnosti vyskytuji treti aditivni mocniny dane delky
def existuje_3_mocnina_pro_delku(posloupnost, delka):
    # pokud takovou mocninu najde, ihned skonci a vrati jednicku
    for i in range(0, len(posloupnost) - 3 * delka):
#         print(secti_usek(posloupnost, i, i + delka), (secti_usek(posloupnost, i + delka, i + 2 * delka)), (secti_usek(posloupnost, i + 2 * delka, i + 3 * delka)))
        if secti_usek(posloupnost, i, i + delka) == secti_usek(posloupnost, i + delka, i + 2 * delka) == secti_usek(posloupnost, i + 2 * delka, i + 3 * delka):
#             print(posloupnost[i : i + delka], posloupnost[i + delka : i + 2 * delka], posloupnost[i + 2 * delka : i + 3 * delka])
            return True
    return False

# pro danou posloupnost zkontroluje vyskyt libovolnych tretich mocnin
def existuje_3_mocnina(posloupnost):
    # pokud zadnou treti mocninu nenajde, vypise danou posloupnost
    for delka in range(1, len(posloupnost) // 3):
        if existuje_3_mocnina_pro_delku(posloupnost, delka):
            return True
    return False

# posloupnost_12 = vytvor_posloupnost(12, PREDPIS)
# print(12, PREDPIS, existuje_3_mocnina(posloupnost_12))

def porovnej_obrazy(o1, o2):
    if o1[0] == o2[0] and o1[1] == o2[1]:
        return True
    return False

L123 = [1, 2, 3]
L023 = [0, 2, 3]
L0123 = [0, 1, 2, 3]
# generuje vsechny mozne predpisy z abecedy o 4 prvcich
# ix[0] je index zacatku
# ix[1] je index predpisu 1 : 1
# ix[2] je index predpisu 1 : 2
# ix[3] je index predpisu 1 : 2
# ix obsahuje ruzne hodnoty z mnoziny [0, 1, 2, 3]
def generuj_predpisy(abcd, ix):
    if len(abcd) != 4:
        raise ValueError('abeceda nema delku 4', abcd)
    predpisy = []
    for i in L123:
        for j in L023:
            for k in L0123:
                for l in L0123:
                    if k == l:
                        continue
                    obraz0 = [abcd[ix[0]], abcd[ix[i]]]
                    obraz1 = [abcd[ix[j]]]
                    obraz2 = [abcd[ix[k]], abcd[ix[l]]]
                    if porovnej_obrazy(obraz0, obraz2):
                        continue
                    for m in L0123:
                        for n in L0123:
                            if m == n:
                                continue
                            obraz3 = [abcd[ix[m]], abcd[ix[n]]]
                            if porovnej_obrazy(obraz0, obraz3):
                                continue
                            if porovnej_obrazy(obraz2, obraz3):
                                continue
                            predpisy.append({abcd[ix[0]] : obraz0, abcd[ix[1]] : obraz1, abcd[ix[2]] : obraz2, abcd[ix[3]] : obraz3})
    return predpisy

def najdi_bez_3_mocniny(predpis, delka):
    posloupnost = vytvor_posloupnost(delka, predpis)
    if existuje_3_mocnina(posloupnost):
        return None, None
    return posloupnost, predpis

def najdi_bez_3_mocniny_sync(predpis, delka, max_time = None):
    if max_time == None:
        return najdi_bez_3_mocniny(predpis, delka)
    
    try:
        posloupnost = vytvor_posloupnost(delka, predpis)
        with time_limit(max_time):
            if existuje_3_mocnina(posloupnost):
                return None, None
    except Exception:
        print('Timeout pro ', predpis)
        return posloupnost, None
    return posloupnost, predpis

def main_sync(delka, max_time = None):
    start_time = time.time()

    mapa = [0, 2, 1, 3]
    print('abeceda', ABCD, 'mapa', mapa)
    predpisy = generuj_predpisy(ABCD, mapa)
    print('pocet predpisu', len(predpisy))

    _vysledky = [najdi_bez_3_mocniny_sync(predpis, delka, max_time) for predpis in predpisy]
    vysledky = [(po, pr) for (po, pr) in _vysledky if po != None]
    print('vysledky', len(vysledky))
    vysledky_ok = [(po, pr) for (po, pr) in vysledky if pr != None]
    print('vysledky_ok', len(vysledky_ok), vysledky_ok)

    elapsed_time = time.time() - start_time
    print('Doba zpracovani (s)', elapsed_time)

#     print_prof_data()

DELKA = 10
MAX_TIME = None

# zkontroluje, zda se v posloupnosti vyskytuji treti aditivni mocniny dane delky
def existuje_3_mocnina_pro_delku_async(posloupnost, delka, start_time):
    import time
    
    # pokud takovou mocninu najde, ihned skonci a vrati jednicku
    for i in range(0, len(posloupnost) - 3 * delka):
        if time.time() - start_time >= MAX_TIME:
            return -1;
#         print(secti_usek(posloupnost, i, i + delka), (secti_usek(posloupnost, i + delka, i + 2 * delka)), (secti_usek(posloupnost, i + 2 * delka, i + 3 * delka)))
        if secti_usek(posloupnost, i, i + delka) == secti_usek(posloupnost, i + delka, i + 2 * delka) == secti_usek(posloupnost, i + 2 * delka, i + 3 * delka):
#             print(posloupnost[i : i + delka], posloupnost[i + delka : i + 2 * delka], posloupnost[i + 2 * delka : i + 3 * delka])
            return 1
    return 0

# pro danou posloupnost zkontroluje vyskyt libovolnych tretich mocnin
def existuje_3_mocnina_async(posloupnost, predpis, start_time):
    import time
    
    # pokud zadnou treti mocninu nenajde, vypise danou posloupnost
    for delka in range(1, len(posloupnost) // 3):
        if time.time() - start_time >= MAX_TIME:
            return posloupnost, None
        rc = existuje_3_mocnina_pro_delku_async(posloupnost, delka, start_time)
        if rc == 1:
            return None, None
        if rc == -1:
            return posloupnost, None
    return posloupnost, predpis

def najdi_bez_3_mocniny_async(predpis):
    import time

    if MAX_TIME == None:
        return najdi_bez_3_mocniny(predpis, delka)

    start_time = time.time()
    posloupnost = vytvor_posloupnost(DELKA, predpis)
    if time.time() - start_time >= MAX_TIME:
        return posloupnost, None
        
    return existuje_3_mocnina_async(posloupnost, predpis, start_time)

# zkontroluje, zda se v posloupnosti vyskytuji treti aditivni mocniny dane delky
def existuje_3_mocnina_pro_delku_async2(in_po_pr_de):
    import time

    start_time = time.time()
    
    (index, posloupnost, predpis, delka) = in_po_pr_de
    
    # pokud takovou mocninu najde, ihned skonci a vrati jednicku
    for i in range(0, len(posloupnost) - 3 * delka):
#         print(secti_usek(posloupnost, i, i + delka), (secti_usek(posloupnost, i + delka, i + 2 * delka)), (secti_usek(posloupnost, i + 2 * delka, i + 3 * delka)))
        if secti_usek(posloupnost, i, i + delka) == secti_usek(posloupnost, i + delka, i + 2 * delka) == secti_usek(posloupnost, i + 2 * delka, i + 3 * delka):
#             print(posloupnost[i : i + delka], posloupnost[i + delka : i + 2 * delka], posloupnost[i + 2 * delka : i + 3 * delka])
            return index, posloupnost, None, delka, time.time() - start_time
    return index, posloupnost, predpis, delka, time.time() - start_time

MAX_TASKS = 1024

def main_async(delka, profile, max_time = None):
    start_time = time.time()
    
    # ipcluster start -n 7
    client = ipp.Client(profile = profile)
    client[:].block = True
    print(client.ids)
    client[:].push(dict(vytvor_posloupnost = vytvor_posloupnost, 
                        iteruj_posloupnost = iteruj_posloupnost, 
                        existuje_3_mocnina = existuje_3_mocnina, 
                        existuje_3_mocnina_async = existuje_3_mocnina_async,
                        existuje_3_mocnina_pro_delku = existuje_3_mocnina_pro_delku,
                        existuje_3_mocnina_pro_delku_async = existuje_3_mocnina_pro_delku_async,
                        existuje_3_mocnina_pro_delku_async2 = existuje_3_mocnina_pro_delku_async2,
                        secti_usek = secti_usek,
                        DELKA = delka,
                        MAX_TIME = max_time,
                        MAX_TASKS = MAX_TASKS))
#     view = client.load_balanced_view()
    view = client.load_balanced_view()
    view.block = True

    mapa = [0, 2, 1, 3]
    print('abeceda', ABCD, 'mapa', mapa)
    predpisy = generuj_predpisy(ABCD, mapa)
    print('pocet predpisu', len(predpisy))

    _vysledky = view.map(najdi_bez_3_mocniny_async, predpisy)
    vysledky_nezpracovane_pocet = 0
    vysledky_nezpracovane = []
    vysledky_ok = {}
    for ix, (po, pr) in enumerate(_vysledky):
        if po == None:
            continue
        if pr != None:
            vysledky_ok[ix] = (po, pr)
            continue
        vysledky_nezpracovane_pocet += 1
        print('len(po) // 3', len(po) // 3)
        for delka in range(1, (len(po) // 3) + 1):
            vysledky_nezpracovane.append((ix, po, predpisy[ix], delka))
#         vysledky_nezpracovane.append((po, predpisy[ix]))
    
    if len(vysledky_nezpracovane) > 0:    
        print('vysledky (pozitivni)', len(vysledky_ok))
        print('vysledky (nezpracovane)', vysledky_nezpracovane_pocet)
        elapsed_time = time.time() - start_time
        print('Doba castecneho zpracovani (s)', elapsed_time)
        print('vysledky_nezpracovane', len(vysledky_nezpracovane))

        lvn = len(vysledky_nezpracovane)
        if lvn < 20000:
            _vysledky2 = []
            l = 0
            while l + MAX_TASKS <= lvn:
                print('zpracovavam', l, l + MAX_TASKS)
                _vysledky2.extend(view.map(existuje_3_mocnina_pro_delku_async2, vysledky_nezpracovane[l:l + MAX_TASKS]))
                l += MAX_TASKS
            print('zpracovavam', l, lvn)
            _vysledky2.extend(view.map(existuje_3_mocnina_pro_delku_async2, vysledky_nezpracovane[l:lvn]))
            print('_vysledky2', len(_vysledky2))
            
            for (ix, po, pr, de, tm) in _vysledky2:
                if de == None:
                    if ix in vysledky_ok:
                        del vysledky_ok[ix]
                else:
                    if not ix in vysledky_ok:
                        vysledky_ok[ix] = (po, pr)    
                        
    print('vysledky_ok', len(vysledky_ok), vysledky_ok)
    for (po, pr) in vysledky_ok:
        print(len(po))

    elapsed_time = time.time() - start_time
    print('Doba zpracovani (s)', elapsed_time)


if __name__ == '__main__':
    delka = 18 if not len(sys.argv) > 1 else int(sys.argv[1])
    profile = 'default' if not len(sys.argv) > 2 else (sys.argv[2])
    func = 'main_async' if not len(sys.argv) > 3 else (sys.argv[3])
    max_time = None if not len(sys.argv) > 4 else int(sys.argv[4])
    if func == 'async':
        main_async(delka, profile, max_time)
    else:
        main_sync(delka, max_time)

