import bonds


def search_bonds(dictionary, keyword):
    results = {}
    for key in dictionary.keys():
        if keyword.lower() in key.lower():  # Teeb otsingu tõstutundetu
            results[key] = dictionary[key]
    return results

keyword = "big"
found_bonds = search_bonds(bonds.database, keyword)
print(found_bonds)

"""Valikus on 
{'Bigbank 8.00% subord.bond32': 'BIGB080032A', 'Bigbank 8.00% subord.bond33': 'BIGB080033A'}
Valikus on 2 võlakirja, vali millist neist soovid?
Kirjuta 1, 2, 3 või X, et uuesti otsida

"""