import ipyparallel as ipp
from timeit import default_timer as clock
import sys, time

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
def iteruj_posloupnost(seznam, predpis):
    novy = []
    for i in range(len(seznam)):
        novy = novy + predpis[seznam[i]]
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
@profile
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

@profile
def najdi_bez_3_mocniny_sync(predpis, delka):
    posloupnost = vytvor_posloupnost(delka, predpis)
    if existuje_3_mocnina(posloupnost):
        return None, None
    return posloupnost, predpis

def main_sync(delka):
    t1 = clock()

    mapa = [0, 2, 1, 3]
    print('abeceda', ABCD, 'mapa', mapa)
    predpisy = generuj_predpisy(ABCD, mapa)
    print('pocet predpisu', len(predpisy))

    vysledky = [najdi_bez_3_mocniny_sync(predpis, delka) for predpis in predpisy]

    for posloupnost, predpis in vysledky:
        if posloupnost != None:
            print(posloupnost)
            print(predpis)

    t2 = clock()
    print('Doba zpracovani (s)', t2 - t1)

    print_prof_data()

DELKA = 10

def najdi_bez_3_mocniny_async(predpis):
    posloupnost = vytvor_posloupnost(DELKA, predpis)
    if existuje_3_mocnina(posloupnost):
        return None, None
    return posloupnost, predpis

def main_async(delka, profile):
    t1 = clock()
    
    # ipcluster start -n 3
    client = ipp.Client(profile = profile)
#     client = ipp.Client()
    print(client.ids)
    client[:].push(dict(vytvor_posloupnost = vytvor_posloupnost, 
                        iteruj_posloupnost = iteruj_posloupnost, 
                        existuje_3_mocnina = existuje_3_mocnina, 
                        existuje_3_mocnina_pro_delku = existuje_3_mocnina_pro_delku,
                        secti_usek = secti_usek,
                        DELKA = delka))
#     view = client.load_balanced_view()
    view = client.load_balanced_view()
    view.block = True

    mapa = [0, 2, 1, 3]
    print('abeceda', ABCD, 'mapa', mapa)
    predpisy = generuj_predpisy(ABCD, mapa)
    print('pocet predpisu', len(predpisy))

    vysledky = view.map(najdi_bez_3_mocniny_async, predpisy)
 
    for posloupnost, predpis in vysledky:
        if posloupnost != None:
            print(posloupnost)
            print(predpis)

    t2 = clock()
    print('Doba zpracovani (s)', t2 - t1)


if __name__ == '__main__':
    delka = 15 if not len(sys.argv) > 1 else int(sys.argv[1])
    profile = 'default' if not len(sys.argv) > 2 else (sys.argv[2] + 'profile')
    func = 'main_sync' if not len(sys.argv) > 3 else ('main_' + sys.argv[3])
    if func == 'main_async':
        main_async(delka, profile)
    elif func == 'main_sync':
        main_sync(delka)

