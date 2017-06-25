import ipyparallel as ipp

client = ipp.Client()
print(client.ids)
view = client.load_balanced_view()

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
def zkontroluj_delku(posloupnost, delka):
    # pokud takovou mocninu najde, ihned skonci a vrati jednicku
    for i in range(0, len(posloupnost) - 3*delka):
#         print(secti_usek(posloupnost, i, i + delka), (secti_usek(posloupnost, i + delka, i + 2 * delka)), (secti_usek(posloupnost, i + 2 * delka, i + 3 * delka)))
        if secti_usek(posloupnost, i, i + delka) == secti_usek(posloupnost, i + delka, i + 2 * delka) == secti_usek(posloupnost, i + 2 * delka, i + 3 * delka):
#             print(posloupnost[i : i + delka], posloupnost[i + delka : i + 2 * delka], posloupnost[i + 2 * delka : i + 3 * delka])
            return True
    return False

# pro danou posloupnost zkontroluje vyskyt libovolnych tretich mocnin
def zkontroluj(posloupnost): 
    # pokud zadnou treti mocninu nenajde, vypise danou posloupnost
    nalezeno = False
    for delka in range(1, len(posloupnost) // 3):
        if zkontroluj_delku(posloupnost, delka):
            nalezeno = True
            break
    if not nalezeno:
        print('nalezeno', posloupnost)
    return nalezeno

# posloupnost_12 = vytvor_posloupnost(12, PREDPIS)
# print(12, PREDPIS, zkontroluj(posloupnost_12))

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

def zkontroluj_predpis(delka, predpis):
    posloupnost = vytvor_posloupnost(delka, predpis)
    if not zkontroluj(posloupnost):
        print('predpis', predpis)

mapa = [0, 2, 1, 3]
predpisy = generuj_predpisy(ABCD, mapa)
print(ABCD, mapa, len(predpisy))

for predpis in predpisy:
#     print(predpis)
#     zkontroluj_predpis(12, predpis)
    print(view.apply(zkontroluj_predpis, 15, predpis).result)



