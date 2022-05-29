@echo off
conda activate app & pyinstaller --noconfirm --onefile --windowed --icon "F:/ThesisDraft/NSApp/ico/icon.ico" --name "ns_svc"  "F:/ThesisDraft/NSApp/main_svc.py"