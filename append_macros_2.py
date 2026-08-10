search_sites_2 = [
    ("walgreens", "https://www.walgreens.com/search/results.jsp?Ntt="),
    ("cvs", "https://www.cvs.com/search/?searchTerm="),
    ("rite aid", "https://www.riteaid.com/shop/catalogsearch/result/?q="),
    ("sephora", "https://www.sephora.com/search?keyword="),
    ("ulta", "https://www.ulta.com/search?search="),
    ("gamestop", "https://www.gamestop.com/search/?q="),
    ("barnes and noble", "https://www.barnesandnoble.com/s/"),
    ("zappos", "https://www.zappos.com/search?term="),
    ("overstock", "https://www.overstock.com/search?keywords="),
    ("chewy", "https://www.chewy.com/s?query="),
    ("petco", "https://www.petco.com/shop/SearchDisplay?searchTerm="),
    ("petsmart", "https://www.petsmart.com/search/?q="),
    ("staples", "https://www.staples.com/"),
    ("office depot", "https://www.officedepot.com/catalog/search.do?Ntt="),
    ("dick's sporting goods", "https://www.dickssportinggoods.com/f/?query="),
    ("rei", "https://www.rei.com/search?q="),
    ("foot locker", "https://www.footlocker.com/search?query="),
    ("nike", "https://www.nike.com/w?q="),
    ("adidas", "https://www.adidas.com/us/search?q="),
    ("under armour", "https://www.underarmour.com/en-us/search/?q="),
    ("puma", "https://www.puma.com/us/en/search?q="),
    ("h&m", "https://www2.hm.com/en_us/search-results.html?q="),
    ("zara", "https://www.zara.com/us/en/search?searchTerm="),
    ("forever 21", "https://www.forever21.com/us/shop/Search/"),
    ("asos", "https://www.asos.com/us/search/?q="),
    ("shein", "https://us.shein.com/pdsearch/"),
    ("boohoo", "https://us.boohoo.com/search?q="),
    ("missguided", "https://www.missguidedus.com/search?q="),
    ("nasty gal", "https://www.nastygal.com/search?q="),
    ("fashion nova", "https://www.fashionnova.com/pages/search-results-page?q="),
    ("urban outfitters", "https://www.urbanoutfitters.com/search?q="),
    ("anthropologie", "https://www.anthropologie.com/search?q="),
    ("free people", "https://www.freepeople.com/search?q="),
    ("gap", "https://www.gap.com/browse/search.do?searchText="),
    ("old navy", "https://oldnavy.gap.com/browse/search.do?searchText="),
    ("banana republic", "https://bananarepublic.gap.com/browse/search.do?searchText="),
    ("j.crew", "https://www.jcrew.com/search?q="),
    ("madewell", "https://www.madewell.com/search?q="),
    ("abercrombie & fitch", "https://www.abercrombie.com/shop/us/search?departmentCategoryId=10000&searchTerm="),
    ("hollister", "https://www.hollisterco.com/shop/us/search?departmentCategoryId=10000&searchTerm="),
    ("american eagle", "https://www.ae.com/us/en/s/"),
    ("aeropostale", "https://www.aeropostale.com/search?q="),
    ("pacsun", "https://www.pacsun.com/search?q="),
    ("zumiez", "https://www.zumiez.com/search/?q="),
    ("tillys", "https://www.tillys.com/search?q="),
    ("vans", "https://www.vans.com/en-us/search?q="),
    ("converse", "https://www.converse.com/shop/search?q="),
    ("new balance", "https://www.newbalance.com/search/?q="),
    ("asics", "https://www.asics.com/us/en-us/search/?q="),
    ("brooks", "https://www.brooksrunning.com/en_us/search?q="),
    ("saucony", "https://www.saucony.com/en/search?q="),
    ("hoka", "https://www.hoka.com/en/us/search/?q="),
    ("on running", "https://www.on-running.com/en-us/search?q="),
    ("merrell", "https://www.merrell.com/en/search?q="),
    ("keen", "https://www.keenfootwear.com/search?q="),
    ("columbia", "https://www.columbia.com/search?q="),
    ("the north face", "https://www.thenorthface.com/en-us/search?q="),
    ("patagonia", "https://www.patagonia.com/search/?q="),
    ("marmot", "https://www.marmot.com/search?q="),
    ("arcteryx", "https://arcteryx.com/us/en/c/search?search="),
    ("salomon", "https://www.salomon.com/en-us/search?q="),
    ("timberland", "https://www.timberland.com/en-us/search?q="),
    ("drmartens", "https://www.drmartens.com/us/en/search/?text="),
    ("ugg", "https://www.ugg.com/search/?q="),
    ("crocs", "https://www.crocs.com/search?q=")
]

code = "\n# AUTO-GENERATED 60+ MORE UNIVERSAL MACROS\n"
code += "more_universal_2 = [\n"
for name, url in search_sites_2:
    if url.endswith("=") or url.endswith("?q=") or url.endswith("text=") or url.endswith("term=") or url.endswith("search="):
        code += f"""    {{"intent": "search {{query}} on {name}", "actions": [
        {{"type": "key", "key": "win+r"}},
        {{"type": "sleep", "ms": 800}},
        {{"type": "type", "text": "brave {url}{{query}}"}},
        {{"type": "sleep", "ms": 800}},
        {{"type": "key", "key": "enter"}}
    ]}},\n"""
    else:
        code += f"""    {{"intent": "open {name}", "actions": [
        {{"type": "key", "key": "win+r"}},
        {{"type": "sleep", "ms": 800}},
        {{"type": "type", "text": "brave {url}"}},
        {{"type": "sleep", "ms": 800}},
        {{"type": "key", "key": "enter"}}
    ]}},\n"""

code = code.rstrip(",\n") + "\n]\n"
code += "skills.extend(more_universal_2)\n"

# Append to train_skills.py before the writing block
with open("train_skills.py", "r") as f:
    content = f.read()

# Insert before '# Write to disk'
content = content.replace("# Write to disk", code + "\n# Write to disk")

with open("train_skills.py", "w") as f:
    f.write(content)

print(f"Added {len(search_sites_2)} more universal search macros to train_skills.py!")
