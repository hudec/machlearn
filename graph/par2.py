import ipyparallel as ipp
#from timeit import default_timer as clock
import sys, time, argparse, signal, itertools
from contextlib import contextmanager
#from graph.seq1 import predpisy

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

ABCD  = [[0, 1, 3, 4], [0, 1, 3, 6], [0, 1, 5, 8]]

# PREDPIS = {0 : [0, 3], 1 : [4, 3], 3 : [1], 4: [0, 1]}
# print(vytvor_posloupnost(5, PREDPIS))
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
def generuj_predpisy(abcd, mapa):
    if len(abcd) != 4:
        raise ValueError('abeceda nema delku 4', abcd)
    predpisy = []
    for i in L123:
        for j in L023:
            for k in L0123:
                for l in L0123:
                    if k == l:
                        continue
                    obraz0 = [abcd[mapa[0]], abcd[mapa[i]]]
                    obraz1 = [abcd[mapa[j]]]
                    obraz2 = [abcd[mapa[k]], abcd[mapa[l]]]
                    if porovnej_obrazy(obraz0, obraz2):
                        continue
                    for m in L0123:
                        for n in L0123:
                            if m == n:
                                continue
                            obraz3 = [abcd[mapa[m]], abcd[mapa[n]]]
                            if porovnej_obrazy(obraz0, obraz3):
                                continue
                            if porovnej_obrazy(obraz2, obraz3):
                                continue
                            predpisy.append({abcd[mapa[0]] : obraz0, abcd[mapa[1]] : obraz1, abcd[mapa[2]] : obraz2, abcd[mapa[3]] : obraz3})
    return predpisy


# danou posloupnost prodlouzi o jednu iteraci - kazde cislo posle na svuj obraz
def iteruj_posloupnost(posloupnost, predpis):
    novy = []
    for p in posloupnost:
        novy.extend(predpis[p]) 
    return novy

# pro zadane pocatecni cislo a pocet iteraci vytvori posloupnost
def vytvor_posloupnost(predpis, pocet_iteraci):
    posloupnost = None
    for k in predpis.keys():
        if k == predpis[k][0]:
            posloupnost = [k]
            break
    if posloupnost == None:
        raise ValueError('predpis nema zacatek', predpis)
    for _ in range(pocet_iteraci):
        posloupnost = iteruj_posloupnost(posloupnost, predpis)
    return posloupnost

TIMEOUT = 1
TRETI_MOCNINA_OK = 2
TRETI_MOCNINA_NOK = 3

# zkontroluje, zda se v posloupnosti vyskytuji treti aditivni mocniny dane delky
def existuje_3_mocnina_pro_delku(posloupnost, delka, stare_delky, nove_delky, start_time = None):
    import time
    
    konec = len(posloupnost) - 3 * delka + 1
    for i in range(0, konec):
        if start_time != None and time.time() - start_time >= MAX_TIME:
            return TIMEOUT;
        
        if i in nove_delky:
            d1 = nove_delky[i]
        elif stare_delky != None:
            d1 = stare_delky[i] + posloupnost[i + delka - 1]
            nove_delky[i] = d1
        else: # delka = 1
            d1 = posloupnost[i]
            nove_delky[i] = d1
        j = i + delka
        if j in nove_delky:
            d2 = nove_delky[j]
        elif stare_delky != None:
            d2 = stare_delky[j] + posloupnost[j + delka - 1]
            nove_delky[j] = d2
        else: # delka = 1
            d2 = posloupnost[j]
            nove_delky[j] = d2
        k = j + delka
        if k in nove_delky:
            d3 = nove_delky[k]
        elif stare_delky != None:
            d3 = stare_delky[k] + posloupnost[k + delka - 1]
            nove_delky[k] = d3
        else: # delka = 1
            d3 = posloupnost[k]
            nove_delky[k] = d3
        
        if d1 == d2 == d3:
            return TRETI_MOCNINA_OK

    return TRETI_MOCNINA_NOK

# pro danou posloupnost zkontroluje vyskyt libovolnych tretich mocnin
def existuje_3_mocnina(predpis, posloupnost = None):
    stare_delky, nove_delky = None, {}
    # pokud zadnou treti mocninu nenajde, vypise danou posloupnost
    for delka in range(1, len(posloupnost) // 3):
        if existuje_3_mocnina_pro_delku(posloupnost, delka, stare_delky, nove_delky) == TRETI_MOCNINA_OK:
            return TRETI_MOCNINA_OK, posloupnost, predpis
        stare_delky, nove_delky = nove_delky, {}
    return TRETI_MOCNINA_NOK, posloupnost, predpis

def najdi_bez_3_mocniny(predpis, pocet_iteraci, posloupnost = None, max_time = None):
    if posloupnost == None:
        posloupnost = vytvor_posloupnost(predpis, pocet_iteraci)

    if max_time == None:
        return existuje_3_mocnina(predpis, posloupnost)
    
    try:
        with time_limit(max_time):
            return existuje_3_mocnina(predpis, posloupnost)
    except Exception:
        print('Timeout pro ', predpis)
        return TIMEOUT, posloupnost, predpis
    return posloupnost, predpis

def main_sync(cfg, mapa, index = 0, posloupnosti = None):
    start_time = time.time()

    if posloupnosti == None:
        print(index, 'abeceda', ABCD[cfg.abeceda], 'mapa', mapa if mapa != None else cfg.mapa)
        predpisy = generuj_predpisy(ABCD[cfg.abeceda], mapa if mapa != None else cfg.mapa)
        print('pocet predpisu', len(predpisy))
        _vysledky = [najdi_bez_3_mocniny(predpis, cfg.pocet_iteraci, cfg.max_doba_1_zpracovani) for predpis in predpisy]
    else:
        print('pocet posloupnosti', len(posloupnosti))
        _vysledky = [najdi_bez_3_mocniny(pr, None, po, cfg.max_doba_1_zpracovani) for (po, pr) in posloupnosti]

    vysledky = [(st, po, pr) for (st, po, pr) in _vysledky if st == TIMEOUT or st == TRETI_MOCNINA_NOK]
    print('vysledky', len(vysledky))
    vysledky_ok = [(po, pr) for (st, po, pr) in vysledky if st == TRETI_MOCNINA_NOK]
    print('vysledky_ok', len(vysledky_ok)) #, vysledky_ok)

    elapsed_time = time.time() - start_time
    print('Doba zpracovani (s)', elapsed_time)

#     print_prof_data()
    return vysledky_ok

def posloupnosti_sync(cfg):
    start_time = time.time()

    print('abeceda', ABCD[cfg.abeceda])
    predpisy = []
    if cfg.permutace:
        permutace = list(itertools.permutations(cfg.mapa))
        print('pocet permutaci', len(permutace))
        for index, mapa in enumerate(permutace):
#             print(index, mapa)
            predpisy.extend(generuj_predpisy(ABCD[cfg.abeceda], mapa))
    else:
        predpisy.extend(generuj_predpisy(ABCD[cfg.abeceda], cfg.mapa))
    print('pocet predpisu', len(predpisy))
    
    posloupnosti = []
    _posloupnosti = set()
            
    for pr in predpisy: 
        po = vytvor_posloupnost(pr, cfg.pocet_iteraci)
        _po = '-'.join(map(str, po))
        if not _po in _posloupnosti:
            posloupnosti.append((po, pr))
            _posloupnosti.add(_po)
    print('pocet posloupnosti', len(posloupnosti))

    elapsed_time = time.time() - start_time
    print('Doba zpracovani (s)', elapsed_time)

    return posloupnosti

# pro danou posloupnost zkontroluje vyskyt libovolnych tretich mocnin
def existuje_3_mocnina_async(posloupnost, predpis, start_time):
    import time
    
    stare_delky, nove_delky = None, {}
    # pokud zadnou treti mocninu nenajde, vypise danou posloupnost
    for delka in range(1, len(posloupnost) // 3):
        if time.time() - start_time >= MAX_TIME:
            return TIMEOUT, posloupnost, predpis
        st = existuje_3_mocnina_pro_delku(posloupnost, delka, stare_delky, nove_delky, start_time)
        if st != TRETI_MOCNINA_NOK:
            return st, posloupnost, predpis
        stare_delky, nove_delky = nove_delky, {}
    return TRETI_MOCNINA_NOK, posloupnost, predpis

def existuje_3_mocnina_async2(posloupnost_predpis):
    import time

    start_time = time.time()
    (posloupnost, predpis) = posloupnost_predpis
    return existuje_3_mocnina_async(posloupnost, predpis, start_time)

def najdi_bez_3_mocniny_async(predpis):
    import time

    if MAX_TIME == None:
        return najdi_bez_3_mocniny(predpis, POCET_ITERACI)
    
    start_time = time.time()
    posloupnost = vytvor_posloupnost(predpis, POCET_ITERACI)
    if time.time() - start_time >= MAX_TIME:
        return TIMEOUT, posloupnost, predpis
        
    return existuje_3_mocnina_async(posloupnost, predpis, start_time)

POCET_ITERACI = None
MAX_TIME = None

def main_async(cfg, mapa = None, index = 0, posloupnosti = None):
    start_time = time.time()
    
    # ipcluster start -n 7
    client = ipp.Client(profile = cfg.async_profil)
    client[:].block = True
    print(client.ids)
    client[:].push(dict(vytvor_posloupnost = vytvor_posloupnost, 
                        iteruj_posloupnost = iteruj_posloupnost, 
                        existuje_3_mocnina_pro_delku = existuje_3_mocnina_pro_delku, 
                        existuje_3_mocnina = existuje_3_mocnina,
                        najdi_bez_3_mocniny = najdi_bez_3_mocniny,
                        existuje_3_mocnina_async = existuje_3_mocnina_async,
                        existuje_3_mocnina_async2 = existuje_3_mocnina_async2,
                        najdi_bez_3_mocniny_async = najdi_bez_3_mocniny_async,
                        POCET_ITERACI = cfg.pocet_iteraci,
                        MAX_TIME = cfg.max_doba_1_zpracovani, 
                        TIMEOUT = TIMEOUT,
                        TRETI_MOCNINA_OK = TRETI_MOCNINA_OK,
                        TRETI_MOCNINA_NOK = TRETI_MOCNINA_NOK))
#     view = client.load_balanced_view()
    view = client.load_balanced_view()
    view.block = True

    if posloupnosti == None:
        print(index, 'abeceda', ABCD[cfg.abeceda], 'mapa', mapa if mapa != None else cfg.mapa)
        predpisy = generuj_predpisy(ABCD[cfg.abeceda], mapa if mapa != None else cfg.mapa)
        print('pocet predpisu', len(predpisy))
        _vysledky = view.map(najdi_bez_3_mocniny_async, predpisy)
    else:
        lpo = len(posloupnosti)
        print('pocet posloupnosti', lpo)
        _vysledky = []
        l = 0
        while l + cfg.max_vzdalenych_ukolu <= lpo:
            print('zpracovavam', l, l + cfg.max_vzdalenych_ukolu)
            _vysledky.extend(view.map(existuje_3_mocnina_async2, posloupnosti[l:l + cfg.max_vzdalenych_ukolu]))
            l += cfg.max_vzdalenych_ukolu
    
    vysledky_nezpracovane_pocet = 0
    vysledky_nezpracovane = []
    vysledky_ok = {}
    for ix, (st, po, pr) in enumerate(_vysledky):
        if st == TRETI_MOCNINA_OK:
            continue
        if st == TRETI_MOCNINA_NOK:
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

#         lvn = len(vysledky_nezpracovane)
#         if lvn <= cfg.max_delka_2_zpracovani:
#             _vysledky2 = []
#             l = 0
#             while l + cfg.max_vzdalenych_ukolu <= lvn:
#                 print('zpracovavam', l, l + cfg.max_vzdalenych_ukolu, time.time() - start_time)
#                 _vysledky2.extend(view.map(existuje_3_mocnina_pro_delku_async2, vysledky_nezpracovane[l:l + cfg.max_vzdalenych_ukolu]))
#                 l += cfg.max_vzdalenych_ukolu
#             print('zpracovavam', l, lvn, time.time() - start_time)
#             _vysledky2.extend(view.map(existuje_3_mocnina_pro_delku_async2, vysledky_nezpracovane[l:lvn]))
#             print('_vysledky2', len(_vysledky2))
#             
#             for (ix, po, pr, de, tm) in _vysledky2:
#                 if de == None:
#                     if ix in vysledky_ok:
#                         del vysledky_ok[ix]
#                 else:
#                     if not ix in vysledky_ok:
#                         vysledky_ok[ix] = (po, pr)    
                        
    print('vysledky_ok', len(vysledky_ok)) #, vysledky_ok)
    for (po, pr) in vysledky_ok.values():
        print(len(po))

    elapsed_time = time.time() - start_time
    print('Doba zpracovani (s)', elapsed_time)
    
    return vysledky_ok.values()

def vytvor_posloupnost_async(predpis):
    return (vytvor_posloupnost(predpis, POCET_ITERACI), predpis)

PREDPISY = None
def vytvor_posloupnosti_async():
    posloupnosti = []
    for predpis in PREDPISY:
        posloupnosti.append(vytvor_posloupnost_async(predpis))
    return posloupnosti

def posloupnosti_async(cfg):
    start_time = time.time()

    client = ipp.Client(profile = cfg.async_profil)
    client[:].block = True
    print(client.ids)

    print('abeceda', ABCD[cfg.abeceda])
    predpisy = []
    if cfg.permutace:
        permutace = list(itertools.permutations(cfg.mapa))
        print('pocet permutaci', len(permutace))
        for index, mapa in enumerate(permutace):
#             print(index, mapa)
            predpisy.extend(generuj_predpisy(ABCD[cfg.abeceda], mapa))
    else:
        predpisy.extend(generuj_predpisy(ABCD[cfg.abeceda], cfg.mapa))
    lpr = len(predpisy)
    print('pocet predpisu', lpr)
    
    client[:].push(dict(vytvor_posloupnost_async = vytvor_posloupnost_async, 
                        vytvor_posloupnost = vytvor_posloupnost, 
                        iteruj_posloupnost = iteruj_posloupnost, 
                        POCET_ITERACI = cfg.pocet_iteraci))
#     view = client.load_balanced_view()
#     view.block = True
# 
#     posloupnosti = []
#     l = 0
#     while l + cfg.max_vzdalenych_ukolu <= lpr:
#         print('zpracovavam', l, l + cfg.max_vzdalenych_ukolu)
#         posloupnosti.extend(view.map(vytvor_posloupnost_async, predpisy[l:l + cfg.max_vzdalenych_ukolu]))
#         l += cfg.max_vzdalenych_ukolu
    dview = client[:]
    dview.block = True
    dview.scatter('PREDPISY', predpisy)
    ar = dview.apply(vytvor_posloupnosti_async)
    
    _posloupnosti = set()
    posloupnosti_ok = []
    for posloupnosti in ar:
        for (po, pr) in posloupnosti: 
            _po = '-'.join(map(str, po))
            if not _po in _posloupnosti:
                posloupnosti_ok.append((po, pr))
                _posloupnosti.add(_po)
    print('pocet posloupnosti', len(posloupnosti_ok))

    elapsed_time = time.time() - start_time
    print('Doba castecneho zpracovani (s)', elapsed_time)

    return posloupnosti_ok

class Config:
    def __init__(self):
        self.default_pocet_iteraci = 10
        self.default_async_profil = 'default'
        self.default_async_zpracovani = False
        self.default_max_doba_1_zpracovani = None
        self.default_max_vzdalenych_ukolu = 1024
        self.default_max_delka_2_zpracovani = 10000
        self.default_abeceda = 0
        self.default_mapa = [0, 2, 1, 3]
        self.default_permutace = False
        self.default_generuj_posloupnosti = False
        self.default_async_generuj_posloupnosti = False
        
        parser = argparse.ArgumentParser(description='Generovani posloupnosti bez tretich mocnin.')
        parser.add_argument('-i', '--iter', type=int, dest = 'pocet_iteraci', default = self.default_pocet_iteraci,
                            help='pocet iteraci pri generovani posloupnosti')
        parser.add_argument('-p', '--prof', dest = 'async_profil', default = self.default_async_profil,
                            help='profil pro ipyparallel)')
        parser.add_argument('-a', '--async', dest = 'async_zpracovani', default = self.default_async_zpracovani, action='store_true',
                            help='asynchronni zpracovani (ipyparallel)')
        parser.add_argument('-d', '--doba', type=int, dest = 'max_doba_1_zpracovani', default = self.default_max_doba_1_zpracovani,
                            help='maximalni doba pro prvni fazi asynchronniho zpracovani')
        parser.add_argument('-P', '--perm', dest = 'permutace', default = self.default_permutace, action='store_true',
                            help='permutace zakladni mapy')
        parser.add_argument('-u', '--ukoly', type=int, dest = 'max_vzdalenych_ukolu', default = self.default_max_vzdalenych_ukolu,
                            help='maximalni pocet ukolu pro jednu distribuci')
        parser.add_argument('-D', '--delka', type=int, dest = 'max_delka_2_zpracovani', default = self.default_max_delka_2_zpracovani,
                            help='maximalni delka ukolu pro asynchronni zpracovani')
        parser.add_argument('-m', '--mapa', dest = 'mapa', nargs = '+', default = self.default_mapa,
                            help='mapa pro generovani predpisu')
        parser.add_argument('-g', '--gen', dest = 'generuj_posloupnosti', default = self.default_generuj_posloupnosti, action='store_true',
                            help='generuje pro vsechny mapy a predpisy jednu mnozinu posloupnosti')
        parser.add_argument('-G', '--agen', dest = 'async_generuj_posloupnosti', default = self.default_async_generuj_posloupnosti, action='store_true',
                            help='generuje pro vsechny mapy a predpisy jednu mnozinu posloupnosti asynchronne')
        parser.add_argument('-A', '--abcd', type=int, dest = 'abeceda', default = self.default_abeceda,
                            help='index abecedy [0, 1, 3, 4], [0, 1, 3, 6], [0, 1, 5, 8]')
        parser.parse_args(namespace = self)

def main(cfg, mapa = None, index = 0):
    if cfg.async_zpracovani:
        return main_async(cfg, mapa, index)
    else:
        return main_sync(cfg, mapa, index)
                
if __name__ == '__main__':
    start_time = time.time()
    
    cfg = Config()
    posloupnosti = None
    vysledky = []
    
    if cfg.generuj_posloupnosti or cfg.async_generuj_posloupnosti:
        if cfg.async_generuj_posloupnosti:
            posloupnosti = posloupnosti_async(cfg)
        else:
            posloupnosti = posloupnosti_sync(cfg)
        if cfg.async_zpracovani:
            if cfg.max_doba_1_zpracovani == None:
                cfg.max_doba_1_zpracovani = 5
            vysledky.extend(main_async(cfg, None, None, posloupnosti))
        else:
            vysledky.extend(main_sync(cfg, None, None, posloupnosti))
        print('VYSLEDKY, POCET', len(vysledky))
    
    else:
        if cfg.permutace:
            permutace = list(itertools.permutations(cfg.mapa))
            print('pocet permutaci', len(permutace))
            for index, mapa in enumerate(permutace):
                vysledky.extend(main(cfg, mapa, index))
        else:
            vysledky.extend(main(cfg))
    
        print('VYSLEDKY, POCET', len(vysledky))
        _vysledky = set()
        for (po, pr) in vysledky:
            _vysledky.add('-'.join(map(str, po))) 
        print('VYSLEDKY, POCET JEDNOZNACNY', len(_vysledky))

    elapsed_time = time.time() - start_time
    print('Doba zpracovani (s)', elapsed_time)
