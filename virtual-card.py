#!/usr/bin/env python3
"""Virtuelle Karten auf dem Folk-Tisch anlegen, platzieren und entfernen.

Nachbau von builtin-programs/web/new.folk: setzt per Hold! die Statements
`has program code`, `has resolved geometry`, `has quad` und `has a canvas`.
Übertragen wird per HTTP-POST an den Folk-Webserver (wertet den Body als Tcl aus).
Anders als bei /new bleibt die Karte, bis sie entfernt wird (mit --save auch
über einen Folk-Neustart hinaus).

Beispiele:
  ./virtual-card.py add hallo -c 'Wish $this is outlined blue' --x 40% --y 30%
  ./virtual-card.py add uhr -f uhr.folk --x 800 --y 400 --w 600 --h 400 --angle 15
  ./virtual-card.py ls
  ./virtual-card.py rm hallo
"""
import argparse
import base64
import sys
import urllib.request

PREFIX = "virtual-card-"
KEYS = ("canv", "geom", "quad", "code")


def tcl_word(s: str) -> str:
    """Wert als Tcl-Wort in geschweiften Klammern (nur einfache Werte erlaubt)."""
    if any(c in s for c in "{}\\[]$\"; \n"):
        sys.exit(f"Ungültiger Wert: {s!r}")
    return "{" + s + "}"


def post(host: str, tcl: str) -> str:
    req = urllib.request.Request(f"http://{host}/", data=tcl.encode(), method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        out = r.read().decode()
    if out.startswith("Error:"):
        sys.exit(out)
    return out


def hold(card: str, key: str, body: str, save: bool) -> str:
    flags = "-noncapturing" + (" -save" if save else "")
    return f"Hold! {flags} -on {card} -key {key} {{\n{body}\n}}\n"


def quad_body(card, x, y, w, h, angle):
    # Wie in new.folk: Rechteck in Projektorpixeln über die Intrinsics in 3D
    # (Tiefe 1,5 m) umrechnen, um den Mittelpunkt drehen, Quad erzeugen.
    return f"""
package require linalg
namespace import ::math::linearalgebra::add
namespace import ::math::linearalgebra::sub
namespace import ::math::linearalgebra::matmul
namespace import ::math::linearalgebra::scale

Require! the quad library is /quadLib/
Require! display /disp/ has width /displayWidth/ height /displayHeight/
Require! display $disp has intrinsics /in/

proc px {{v total}} {{
    if {{[string match *% $v]}} {{
        return [expr {{double([string range $v 0 end-1]) / 100.0 * $total}}]
    }}
    return [expr {{double($v)}}]
}}
set w [px {w} $displayWidth]; set h [px {h} $displayHeight]
# x/y = Mittelpunkt der Karte
set x [expr {{[px {x} $displayWidth] - $w / 2.0}}]
set y [expr {{[px {y} $displayHeight] - $h / 2.0}}]

set depth 1.5
set sx [expr {{[dict get $in width] / double($displayWidth)}}]
set sy [expr {{[dict get $in height] / double($displayHeight)}}]
set fx [dict get $in fx]; set fy [dict get $in fy]
set cx [dict get $in cx]; set cy [dict get $in cy]
set x1 [expr {{($x * $sx - $cx) * $depth / $fx}}]
set y1 [expr {{($y * $sy - $cy) * $depth / $fy}}]
set x2 [expr {{(($x + $w) * $sx - $cx) * $depth / $fx}}]
set y2 [expr {{(($y + $h) * $sy - $cy) * $depth / $fy}}]
set vs [list [list $x1 $y1 $depth] [list $x2 $y1 $depth] \\
             [list $x2 $y2 $depth] [list $x1 $y2 $depth]]

set a [expr {{{angle} * 3.14159265 / 180.0}}]
set c [expr {{cos($a)}}]; set s [expr {{sin($a)}}]
set R [list [list $c [expr {{-$s}}] 0.0] [list $s $c 0.0] [list 0.0 0.0 1.0]]
lassign $vs v1 v2 v3 v4
set m [scale 0.25 [add [add $v1 $v2] [add $v3 $v4]]]
set rvs [lmap v $vs {{add [matmul $R [sub $v $m]] $m}}]

Claim {card} has quad [$quadLib create "display $disp" $rvs]
"""


def cmd_add(a):
    card = PREFIX + a.name
    if a.file:
        with open(a.file, encoding="utf-8") as f:
            code = f.read()
    else:
        code = a.code
    b64 = base64.b64encode(code.encode()).decode()
    # Größe der Karte in Metern wie in new.folk: Pixel / 2000
    geom_w = geom_h = None
    for v in (a.w, a.h):
        if v.endswith("%"):
            sys.exit("--w/--h: bitte Pixel angeben (keine Prozent)")
    geom_w, geom_h = float(a.w) / 2000, float(a.h) / 2000
    x, y, w, h = map(tcl_word, (a.x, a.y, a.w, a.h))

    tcl = hold(card, "canv", f"Wish {card} has a canvas", a.save)
    tcl += hold(card, "geom",
                f"Claim {card} has resolved geometry {{width {geom_w} height {geom_h}}}",
                a.save)
    tcl += hold(card, "code",
                f"package require base64\n"
                f"Claim {card} has program code [binary decode base64 {b64}]",
                a.save)
    tcl += hold(card, "quad", quad_body(card, x, y, w, h, float(a.angle)), a.save)
    post(a.host, tcl)
    print(f"Karte {card} angelegt.")


def cmd_rm(a):
    card = PREFIX + a.name
    flags = "-save " if a.save else ""
    tcl = "".join(f"Hold! {flags}-on {card} -key {k} {{}}\n" for k in KEYS)
    post(a.host, tcl)
    print(f"Karte {card} entfernt.")


def cmd_ls(a):
    out = post(a.host, f"""
set r [list]
foreach m [Query! /p/ has program code /c/] {{
    set p [dict get $m p]
    if {{[string match {PREFIX}* $p]}} {{ lappend r [string range $p {len(PREFIX)} end] }}
}}
join [lsort -unique $r] \\n
""")
    print(out or "(keine virtuellen Karten)")


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--host", default="carthag.local:4273")
    sub = p.add_subparsers(dest="cmd", required=True)

    add = sub.add_parser("add", help="Karte anlegen oder verschieben (gleicher Name ersetzt)")
    add.add_argument("name")
    src = add.add_mutually_exclusive_group(required=True)
    src.add_argument("-c", "--code", help="Programmcode")
    src.add_argument("-f", "--file", help="Datei mit Programmcode")
    add.add_argument("--x", default="50%", help="Mitte x in Projektorpixeln oder %% (Standard 50%%)")
    add.add_argument("--y", default="50%", help="Mitte y in Projektorpixeln oder %% (Standard 50%%)")
    add.add_argument("--w", default="400", help="Breite in Projektorpixeln (Standard 400)")
    add.add_argument("--h", default="300", help="Höhe in Projektorpixeln (Standard 300)")
    add.add_argument("--angle", default="0", help="Drehung in Grad")
    add.add_argument("--save", action="store_true", help="Folk-Neustart überdauern")
    add.set_defaults(func=cmd_add)

    rm = sub.add_parser("rm", help="Karte entfernen")
    rm.add_argument("name")
    rm.add_argument("--save", action="store_true", help="auch gespeicherte Karte löschen")
    rm.set_defaults(func=cmd_rm)

    ls = sub.add_parser("ls", help="virtuelle Karten auflisten")
    ls.set_defaults(func=cmd_ls)

    a = p.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
