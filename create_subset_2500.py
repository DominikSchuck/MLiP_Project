"""
Erstelle ein 2500-Bilder-Subset aus dem MLiP_data Dataset
mit stratifizierter Auswahl nach Labels
"""

import json
import random
from pathlib import Path
from collections import defaultdict
import shutil
import csv

# ============= KONFIGURATION =============
SOURCE_JSON = Path("C:/Users/domin/Desktop/MLiP_data/al5083/train/train.json")
SOURCE_IMG_DIR = Path("C:/Users/domin/Desktop/MLiP_data/al5083/train")
OUTPUT_DIR = Path("C:/Users/domin/Documents/MLiP/subset_2500")
TARGET_SIZE = 2500
FRAME_SKIP = 1  # 1 = alle Frames, 2 = jeden 2. Frame, etc.
SEED = 42

# ============= LADE LABELS =============
print(f"Lade Labels aus {SOURCE_JSON}...")
with open(SOURCE_JSON, 'r') as f:
    all_labels = json.load(f)

print(f"✓ Geladen: {len(all_labels)} Bilder")

# ============= GRUPPIERE NACH LABEL & FRAME-SKIP =============
by_label = defaultdict(list)

for img_path, label in all_labels.items():
    # Optional: Frame-Sampling (z.B. nur frame_00000, frame_00002, frame_00004, ...)
    if FRAME_SKIP > 1:
        # Parse frame number aus dem Pfad: "...frame_00123.png" -> 123
        try:
            fname = Path(img_path).stem  # "frame_00123"
            frame_num = int(fname.split('_')[-1])
            if frame_num % FRAME_SKIP != 0:
                continue  # Überspringen
        except:
            pass  # Wenn Parse fehlschlägt, nehm das Bild trotzdem
    
    by_label[label].append(img_path)

print(f"\n✓ Gruppiert nach {len(by_label)} Labels:")
for lbl, paths in sorted(by_label.items()):
    print(f"  Label {lbl}: {len(paths)} Bilder")

# ============= STRATIFIZIERTE AUSWAHL =============
random.seed(SEED)
selected = {}

# Berechne wie viele Bilder pro Label
label_counts = {lbl: len(paths) for lbl, paths in by_label.items()}
total_available = sum(label_counts.values())

print(f"\n✓ Verfügbar nach Frame-Skip: {total_available} Bilder")

# Proportionale Auswahl pro Label
selected_count = {}
for lbl in sorted(by_label.keys()):
    ratio = label_counts[lbl] / total_available
    num_for_label = max(1, int(TARGET_SIZE * ratio))  # Mindestens 1 pro Label
    selected_count[lbl] = num_for_label

# Falls Rounding zu größer/kleiner als Target führt, nachregeln
total_selected = sum(selected_count.values())
if total_selected != TARGET_SIZE:
    # Größte Label klasse anpassen
    largest_label = max(selected_count, key=selected_count.get)
    selected_count[largest_label] += (TARGET_SIZE - total_selected)

print(f"\n✓ Auswahl pro Label (insgesamt {sum(selected_count.values())} Bilder):")
for lbl in sorted(selected_count.keys()):
    actual = len(by_label[lbl])
    target = selected_count[lbl]
    print(f"  Label {lbl}: {target} von {actual} Bildern")

# ============= SAMPLE PRO LABEL =============
for lbl, target_count in selected_count.items():
    available = by_label[lbl]
    sample_size = min(target_count, len(available))
    sampled = random.sample(available, sample_size)
    for img_path in sampled:
        selected[img_path] = lbl

print(f"\n✓ Insgesamt ausgewählt: {len(selected)} Bilder")

# ============= ERSTELLE ORDNERSTRUKTUR & KOPIERE BILDER =============
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
train_dir = OUTPUT_DIR / "train"
train_dir.mkdir(exist_ok=True)

print(f"\nKopiere Bilder nach {train_dir}...")
copied = 0
failed = []

for img_path_rel, label in selected.items():
    src = SOURCE_IMG_DIR / img_path_rel
    # Flache Struktur: nur Dateiname, ODER mit Subfolder erhalten
    dst = train_dir / img_path_rel  # Behält Subfolder wie "170906-150010-Al 2mm/..."
    dst.parent.mkdir(parents=True, exist_ok=True)
    
    if src.exists():
        shutil.copy2(src, dst)
        copied += 1
        if copied % 250 == 0:
            print(f"  ... {copied}/{len(selected)}")
    else:
        failed.append(str(src))

print(f"✓ Kopiert: {copied}/{len(selected)} Bilder")
if failed:
    print(f"⚠ Fehler bei {len(failed)} Bildern:")
    for f in failed[:5]:
        print(f"  - {f}")

# ============= SPEICHERE LABELS =============
output_labels_json = OUTPUT_DIR / "labels.json"
with open(output_labels_json, 'w') as f:
    json.dump(selected, f, indent=2)
print(f"\n✓ Labels gespeichert: {output_labels_json}")

# ============= SPEICHERE CSV (Optional, für Übersicht) =============
output_labels_csv = OUTPUT_DIR / "labels.csv"
with open(output_labels_csv, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['image_path', 'label'])
    for img_path, label in sorted(selected.items()):
        writer.writerow([img_path, label])
print(f"✓ CSV gespeichert: {output_labels_csv}")

# ============= ZUSAMMENFASSUNG =============
print("\n" + "="*60)
print("FERTIG!")
print("="*60)
print(f"Subset-Verzeichnis: {OUTPUT_DIR}")
print(f"Bilder: {train_dir}")
print(f"Labels (JSON): {output_labels_json}")
print(f"Labels (CSV):  {output_labels_csv}")
print(f"\nVerzeichnisstruktur:")
print(f"  subset_2500/")
print(f"    └── train/")
print(f"        └── [2500 Bilder mit Ordnerstruktur]")
print(f"    └── labels.json")
print(f"    └── labels.csv")
