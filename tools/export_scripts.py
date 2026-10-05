#!/usr/bin/env python3
"""Export every Script/LocalScript/ModuleScript from a saved .rbxlx place into src/.

Usage (from the repo root):  python3 tools/export_scripts.py place/StarfallForge.rbxlx
Studio is the live editing surface; this keeps src/ (git) in sync for review and history.
File naming: <DataModel path>/<Name>.server.luau | .client.luau | .luau (ModuleScript)
"""
import os, sys, shutil
import xml.etree.ElementTree as ET

SCRIPT_CLASSES = {"Script": ".server.luau", "LocalScript": ".client.luau", "ModuleScript": ".luau"}
SKIP_TOP = {"CoreGui", "CorePackages", "PluginGuiService"}

def prop(item, tag, name):
    props = item.find("Properties")
    if props is None:
        return None
    for el in props:
        if el.get("name") == name and (tag is None or el.tag == tag):
            return el.text or ""
    return None

def walk(item, path, out):
    cls = item.get("class")
    name = prop(item, "string", "Name") or cls
    here = path + [name]
    if cls in SCRIPT_CLASSES:
        src = prop(item, "ProtectedString", "Source") or ""
        out.append(("/".join(path), name + SCRIPT_CLASSES[cls], src))
    for child in item.findall("Item"):
        walk(child, here, out)

def main():
    place = sys.argv[1] if len(sys.argv) > 1 else "place/StarfallForge.rbxlx"
    root = ET.parse(place).getroot()
    out = []
    for top in root.findall("Item"):
        name = prop(top, "string", "Name") or top.get("class")
        if name in SKIP_TOP:
            continue
        walk(top, [], out)
    dest = "src"
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    for folder, fname, src in out:
        d = os.path.join(dest, folder)
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, fname), "w", encoding="utf-8", newline="\n") as f:
            f.write(src if src.endswith("\n") else src + "\n")
    print(f"exported {len(out)} scripts to {dest}/")
    for folder, fname, _ in sorted(out):
        print(" ", os.path.join(folder, fname))

if __name__ == "__main__":
    main()
