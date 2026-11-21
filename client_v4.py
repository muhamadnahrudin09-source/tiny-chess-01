import engine as sunfish
import urllib.request as ZU, json as ZJ, os as ZO

ZENV = ZO.getenv("MAKEFUN_ENV_URL")
ZB = {"depth-2": 40000, "depth-3": 70000, "depth-4": 120000,
      "nodes-100k": 40000, "nodes-250k": 70000, "nodes-500k": 100000}

def Zpost(path, data=None):
    return ZJ.loads(ZU.urlopen(ZU.Request(ZENV + path, data=ZJ.dumps(data or {}).encode())).read())

def Zf(m, wp):
    return m if wp else sunfish.Move(119 - m[0], 119 - m[1], m[2])

def Ztm(u, wp):
    return Zf(sunfish.Move(sunfish.parse(u[0:2]), sunfish.parse(u[2:4]), u[4:].upper() or None), wp)

def Zru(m, wp):
    m = Zf(m, wp)
    return sunfish.render(m[0]) + sunfish.render(m[1]) + (m[2] or "").lower()

def Zmain():
    while 1:
        st = Zpost("/game")
        if st["status"] == "done":
            break
        moves = st["moves"]
        b = ZB.get(st["opponent"], 60000)
        wp = len(moves) % 2 == 0
        pos = sunfish.Position(sunfish.initial, 0, (True, True), (True, True), 0, 0)
        hist = [pos]
        for k, u in enumerate(moves):
            hist.append(hist[-1].move(Ztm(u, k % 2 == 0)))
        s = Searcher()
        s.budget = b
        mv = None
        try:
            for q in s.search(hist):
                mv = q[3] or mv
        except Stop:
            mv = s.tp_move.get(s.root) or mv
        seen = {h.board for h in hist}
        u = Zru(mv, wp)
        if hist[-1].move(mv).board in seen:
            for lu in st["legal_moves"]:
                if not hist[-1].move(Ztm(lu, wp)).board in seen:
                    u = lu
                    break
        Zpost("/move", {"game": st["game"], "move": u})

Zmain()
