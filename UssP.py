import tkinter as tk
from tkinter import messagebox, filedialog
import os
import sys
import subprocess
import threading
import time
import platform
import json
import winreg
import ctypes
from datetime import datetime

BIOS_BLUE = "#0000AA"
BIOS_GREY = "#AAAAAA"
BIOS_WHITE = "#FFFFFF"
BIOS_RED = "#AA0000"
BIOS_YELLOW = "#FFFF55"
BIOS_BLACK = "#000000"

FONT_MAIN = ("Consolas", 11)
FONT_BOLD = ("Consolas", 11, "bold")


class USSPCore:
    @staticmethod
    def run_ps(cmd):
        try:
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            full_cmd = f'powershell -NoProfile -Command "{cmd}"'
            res = subprocess.check_output(full_cmd, shell=True, stderr=subprocess.STDOUT, stdin=subprocess.PIPE, startupinfo=si)
            return res.decode('utf-8', errors='replace').strip()
        except Exception as e:
            return f"KERNEL_ERROR: {str(e)}"


class USSP:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("UssP")
        self.root.configure(bg=BIOS_BLACK)

        self.root.attributes("-fullscreen", True)
        self.root.config(cursor="none")

        self.selected_index = 0
        self.current_menu_level = "BOOT"
        self.breadcrumb = []
        self.menu_structure = self.get_structure()
        self.current_dict_ref = self.menu_structure

        self.setup_ui()

        self.auto_register_persistence()

        self.root.bind("<Up>", self.move_up)
        self.root.bind("<Down>", self.move_down)
        self.root.bind("<Return>", self.select)
        self.root.bind("<Escape>", self.back)
        self.root.bind("<F10>", lambda e: self.root.quit())
        self.root.bind("<F5>", lambda e: self.load_menu(self.current_dict_ref))
        self.root.after(100, self.boot_sequence)

    def get_structure(self):
        return {
            "HARDWARE INVENTORY": {
                "desc": "Real-time physical component interrogation via WMI.",
                "actions": {
                    "CPU Architecture": lambda: USSPCore.run_ps("Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, ThreadCount, MaxClockSpeed, L3CacheSize | Format-List"),
                    "Memory Modules": lambda: USSPCore.run_ps("Get-CimInstance Win32_PhysicalMemory | Select-Object Manufacturer, PartNumber, Capacity, Speed, ConfiguredClockSpeed | Format-Table"),
                    "GPU & Display": lambda: USSPCore.run_ps("Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion, AdapterRAM | Format-List"),
                    "Disk S.M.A.R.T Status": lambda: USSPCore.run_ps("Get-CimInstance Win32_DiskDrive | Select-Object Model, Size, Status, InterfaceType"),
                    "Motherboard / BIOS": lambda: USSPCore.run_ps("Get-CimInstance Win32_BaseBoard | Select-Object Manufacturer, Product, Version"),
                    "BIOS Details": lambda: USSPCore.run_ps("Get-CimInstance Win32_BIOS | Select-Object Manufacturer, SMBIOSBIOSVersion, ReleaseDate, Version, SerialNumber | Format-List"),
                    "Logical Drives": lambda: USSPCore.run_ps("Get-CimInstance Win32_LogicalDisk | Select-Object DeviceID, VolumeName, Size, FreeSpace, FileSystem | Format-Table"),
                    "PCI & USB Controllers": lambda: USSPCore.run_ps("Get-CimInstance Win32_PnPEntity | Where-Object { $_.PNPClass -in @('PCI', 'USB') } | Select-Object Name, Manufacturer, Status | Format-Table -AutoSize"),
                    "Full Hardware Summary": lambda: USSPCore.run_ps("Get-CimInstance Win32_ComputerSystem | Select-Object Manufacturer, Model, TotalPhysicalMemory | Format-List"),
                }
            },
            "NETWORK ARCHITECTURE": {
                "desc": "Live socket monitoring and adapter analysis.",
                "actions": {
                    "TCP/UDP Listeners": lambda: USSPCore.run_ps("Get-NetTCPConnection -State Listen | Select-Object LocalAddress, LocalPort, OwningProcess | Sort-Object LocalPort"),
                    "Network Adapters": lambda: USSPCore.run_ps("Get-NetAdapter | Select-Object Name, InterfaceDescription, Status, MacAddress, LinkSpeed"),
                    "DNS Client Cache": lambda: USSPCore.run_ps("Get-DnsClientCache | Select-Object Name, Data, Type | Format-Table"),
                    "Active Routing Table": lambda: USSPCore.run_ps("Get-NetRoute -AddressFamily IPv4 | Select-Object DestinationPrefix, NextHop, RouteMetric"),
                    "Full IP Configuration": lambda: USSPCore.run_ps("Get-NetIPAddress -AddressFamily IPv4 | Select-Object IPAddress, InterfaceIndex, PrefixLength, AddressState | Format-Table"),
                    "ARP Table": lambda: USSPCore.run_ps("Get-NetNeighbor -AddressFamily IPv4 | Select-Object IPAddress, LinkLayerAddress, State | Format-Table"),
                    "WiFi Profiles & Networks": lambda: USSPCore.run_ps("netsh wlan show profiles; netsh wlan show networks"),
                    "Active Connections": lambda: USSPCore.run_ps("Get-NetTCPConnection | Where-Object State -eq 'Established' | Select-Object LocalAddress, LocalPort, RemoteAddress, RemotePort | Format-Table"),
                }
            },
            "OS & SECURITY KERNEL": {
                "desc": "Deep audit of the Windows security subsystem.",
                "actions": {
                    "TPM Module Status": lambda: USSPCore.run_ps("Get-Tpm"),
                    "Windows Defender Status": lambda: USSPCore.run_ps("Get-MpComputerStatus | Select-Object AntivirusEnabled, RealTimeProtectionEnabled, LastFullScanAge"),
                    "Hotfixes (Last 10)": lambda: USSPCore.run_ps("Get-HotFix | Sort-Object InstalledOn -Descending | Select-Object -First 10"),
                    "Secure Boot State": lambda: USSPCore.run_ps(r"""$ErrorActionPreference = 'SilentlyContinue'; try { if (Confirm-SecureBootUEFI) { 'ENABLED' } else { 'DISABLED' } } catch { 'NOT AVAILABLE (Legacy BIOS or permission issue)' }"""),
                    "Firewall Profiles": lambda: USSPCore.run_ps("Get-NetFirewallProfile | Select-Object Name, Enabled, DefaultInboundAction, DefaultOutboundAction | Format-Table"),
                    "UAC Configuration": lambda: USSPCore.run_ps("Get-ItemProperty -Path 'HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Policies\\System' | Select-Object EnableLUA, ConsentPromptBehaviorAdmin"),
                    "Installed Antivirus Products": lambda: USSPCore.run_ps("Get-CimInstance -Namespace 'root/SecurityCenter2' -ClassName AntivirusProduct | Select-Object displayName, productState"),
                    "BitLocker Volumes": lambda: USSPCore.run_ps("Get-BitLockerVolume | Select-Object MountPoint, VolumeStatus, ProtectionStatus | Format-Table"),
                }
            },
            "PERSISTENCE AUDIT": {
                "desc": "Analysis of auto-start entries and system hooks.",
                "actions": {
                    "Registry Run Keys": lambda: USSPCore.run_ps("Get-ItemProperty 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run', 'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run' -ErrorAction SilentlyContinue"),
                    "Scheduled Tasks (Active)": lambda: USSPCore.run_ps("Get-ScheduledTask | Where-Object {$_.State -eq 'Ready'} | Select-Object TaskName, TaskPath | Select-Object -First 20"),
                    "Active Services": lambda: USSPCore.run_ps("Get-Service | Where-Object {$_.Status -eq 'Running'} | Select-Object DisplayName, Name"),
                    "Register USSP Persistence": self.enable_persist,
                    "Startup Folders Content": lambda: USSPCore.run_ps(r"""Get-ChildItem "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup", "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup" -ErrorAction SilentlyContinue | Select-Object Name, FullName"""),
                    "Winlogon & Shell Settings": lambda: USSPCore.run_ps("Get-ItemProperty 'HKLM:\\SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon' -ErrorAction SilentlyContinue | Format-List"),
                    "Explorer Startup Apps": lambda: USSPCore.run_ps("Get-ItemProperty 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer\\StartupApproved\\Run' -ErrorAction SilentlyContinue"),
                }
            },
            "SYSTEM EVENTS (LIVE)": {
                "desc": "Direct query of the Windows Event Log (Critical only).",
                "actions": {
                    "Critical Kernel Events": lambda: USSPCore.run_ps("Get-WinEvent -FilterHashtable @{LogName='System'; Level=1,2} -MaxEvents 15 | Select-Object TimeCreated, Message"),
                    "App Crash History": lambda: USSPCore.run_ps("Get-WinEvent -FilterHashtable @{LogName='Application'; Level=2} -MaxEvents 10 | Select-Object TimeCreated, Message"),
                    "Security Critical Events": lambda: USSPCore.run_ps("Get-WinEvent -FilterHashtable @{LogName='Security'; Level=1,2} -MaxEvents 10 | Select-Object TimeCreated, ID, Message"),
                    "Power Management Events": lambda: USSPCore.run_ps("Get-WinEvent -FilterHashtable @{LogName='System'; ProviderName='*Power*'} -MaxEvents 8 | Select-Object TimeCreated, Message"),
                    "System Audit Log": lambda: USSPCore.run_ps("Get-WinEvent -FilterHashtable @{LogName='System'; Level=3} -MaxEvents 5 | Select-Object TimeCreated, Message"),
                }
            },
            "FORENSIC TOOLS": {
                "desc": "Administrative and data export utilities.",
                "actions": {
                    "Export Full System JSON": self.export_forensic,
                    "List All Drivers": lambda: USSPCore.run_ps("Get-CimInstance Win32_PnPSignedDriver | Select-Object DeviceName, Manufacturer, DriverVersion | Select-Object -First 30"),
                    "Open Network Ports": lambda: USSPCore.run_ps("Get-NetTCPConnection | Where-Object State -eq 'Listen' | Select-Object LocalPort, OwningProcess, State | Format-Table"),
                    "Installed Software (All)": lambda: USSPCore.run_ps("Get-ItemProperty HKLM:\\SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*, HKLM:\\SOFTWARE\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\* | Select-Object DisplayName, DisplayVersion, Publisher | Where-Object DisplayName | Sort-Object DisplayName | Select-Object -First 40"),
                    "Process Tree": lambda: USSPCore.run_ps("Get-Process | Select-Object Name, Id, CPU, WorkingSet | Sort-Object CPU -Descending | Select-Object -First 20"),
                }
            },
           
            "BOOT MANAGEMENT": {
                "desc": "System boot and exit controls. USSP auto-starts on every Windows boot.",
                "actions": {
                    "Boot To Windows": self.boot_to_windows,
                    "Re-Register Auto-Start": self.enable_persist,
                }
            },
            "EXIT": {
                "desc": "Terminate USSP Secure Shell.",
                "actions": {"Shutdown Interface": lambda: self.root.quit()}
            }
        }

    def setup_ui(self):
        self.header = tk.Frame(self.root, bg=BIOS_GREY, height=60)
        self.header.pack(fill="x")
        self.header.pack_propagate(False)

        self.logo_label = tk.Label(self.header, bg=BIOS_GREY)
        try:
            path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
            self.img = tk.PhotoImage(file=path)
            if self.img.width() > 100: self.img = self.img.subsample(4)
            self.logo_label.config(image=self.img)
        except:
            self.logo_label.config(text="[USSP-CORE]", fg=BIOS_RED, font=FONT_BOLD)
        self.logo_label.pack(side="left", padx=20)
        tk.Label(self.header, text="Unofficial Secure Starting Protocol v3.1", bg=BIOS_GREY, fg=BIOS_BLUE, font=FONT_BOLD).pack(side="left")

        self.time_lbl = tk.Label(self.header, text="", bg=BIOS_GREY, fg=BIOS_BLUE, font=FONT_BOLD)
        self.time_lbl.pack(side="right", padx=20)

        self.main = tk.Frame(self.root, bg=BIOS_BLUE, bd=4, relief="ridge")
        self.main.pack(fill="both", expand=True, padx=10, pady=10)

        self.footer = tk.Frame(self.root, bg=BIOS_GREY, height=30)
        self.footer.pack(fill="x")
        tk.Label(self.footer, text="↑↓: Navigate | ENTER: Execute | ESC: Back | F5: Refresh | F10: Exit", bg=BIOS_GREY, fg=BIOS_BLACK, font=("Consolas", 10)).pack()
        self.update_time()

    def update_time(self):
        self.time_lbl.config(text=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        self.root.after(1000, self.update_time)

    def boot_sequence(self):
        self.clear_main()
        t = tk.Text(self.main, bg=BIOS_BLACK, fg=BIOS_WHITE, font=("Consolas", 12), bd=0, highlightthickness=0)
        t.pack(fill="both", expand=True, padx=40, pady=40)

        log = [
            ("> INITIALIZING USSP KERNEL INTERFACE...", 0.1),
            ("> DETECTING SYSTEM ARCHITECTURE... " + platform.machine(), 0.1),
            ("> QUERYING CPU DATA...", 0.2),
            ("> MAPPING MEMORY ADRESSES...", 0.2),
            ("> ASSETS LOADED", 0.05),
            ("> MOUSE POINTER: DISABLED BY SECURITY POLICY", 0.1),
            ("> LIVE DATA MODE: ACTIVE", 0.1),
            ("> AUTO-PERSISTENCE ENABLED (boot on startup)", 0.15),
            ("> READY.", 0.3)
        ]

        def stream(i=0):
            if i < len(log):
                t.insert(tk.END, log[i][0] + "\n")
                self.root.update()
                time.sleep(log[i][1])
                stream(i+1)
            else:
                self.load_menu(self.menu_structure)

        threading.Thread(target=stream, daemon=True).start()

    def load_menu(self, menu):
        self.clear_main()
        self.current_menu_level = "MENU"
        self.current_dict_ref = menu
        self.selected_index = 0

        self.container = tk.Frame(self.main, bg=BIOS_BLUE)
        self.container.pack(fill="both", expand=True)

        self.menu_frame = tk.Frame(self.container, bg=BIOS_BLUE, width=420, bd=2, relief="solid")
        self.menu_frame.pack(side="left", fill="y", padx=10, pady=10)
        self.menu_frame.pack_propagate(False)

        self.desc_frame = tk.Frame(self.container, bg=BIOS_BLUE, bd=2, relief="solid")
        self.desc_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        self.draw_list()

    def draw_list(self):
        for w in self.menu_frame.winfo_children(): w.destroy()
        for w in self.desc_frame.winfo_children(): w.destroy()

        items = list(self.current_dict_ref.keys())
        tk.Label(self.menu_frame, text=" MAIN CATEGORY ", bg=BIOS_WHITE, fg=BIOS_BLACK, font=FONT_BOLD).pack(fill="x")

        for i, item in enumerate(items):
            bg_c = BIOS_RED if i == self.selected_index else BIOS_BLUE
            fg_c = BIOS_YELLOW if i == self.selected_index else BIOS_WHITE
            tk.Label(self.menu_frame, text=f" {item} ", bg=bg_c, fg=fg_c, font=FONT_MAIN, anchor="w").pack(fill="x", pady=2)

        tk.Label(self.desc_frame, text=" SUB-SYSTEM DESCRIPTION ", bg=BIOS_WHITE, fg=BIOS_BLACK, font=FONT_BOLD).pack(fill="x")
        sel = items[self.selected_index]
        val = self.current_dict_ref[sel]
        txt = val["desc"] if isinstance(val, dict) else "Direct Kernel Execution Tool."
        tk.Message(self.desc_frame, text=txt, bg=BIOS_BLUE, fg=BIOS_WHITE, font=FONT_MAIN, width=620).pack(pady=20, padx=10)

    def move_up(self, e):
        if self.current_menu_level == "MENU":
            self.selected_index = (self.selected_index - 1) % len(self.current_dict_ref)
            self.draw_list()

    def move_down(self, e):
        if self.current_menu_level == "MENU":
            self.selected_index = (self.selected_index + 1) % len(self.current_dict_ref)
            self.draw_list()

    def select(self, e):
        if self.current_menu_level == "MENU":
            keys = list(self.current_dict_ref.keys())
            sel = keys[self.selected_index]
            val = self.current_dict_ref[sel]

            if isinstance(val, dict) and "actions" in val:
                self.breadcrumb.append((self.current_dict_ref, self.selected_index))
                self.load_menu(val["actions"])
            elif callable(val):
                self.run_action(sel, val)

    def back(self, e):
        if self.current_menu_level == "ACTION":
            self.load_menu(self.current_dict_ref)
        elif self.current_menu_level == "MENU" and self.breadcrumb:
            prev, idx = self.breadcrumb.pop()
            self.load_menu(prev)
            self.selected_index = idx
            self.draw_list()

    def run_action(self, title, func):
        self.clear_main()
        self.current_menu_level = "ACTION"

        tk.Label(self.main, text=f" DATA STREAM: {title} ", bg=BIOS_RED, fg=BIOS_WHITE, font=FONT_BOLD).pack(fill="x")

        out_frame = tk.Frame(self.main, bg=BIOS_BLACK)
        out_frame.pack(fill="both", expand=True, pady=5)

        scroll = tk.Scrollbar(out_frame)
        scroll.pack(side="right", fill="y")

        txt = tk.Text(out_frame, bg=BIOS_BLACK, fg=BIOS_YELLOW, font=("Consolas", 10), bd=0, yscrollcommand=scroll.set)
        txt.pack(fill="both", expand=True, side="left", padx=10)
        scroll.config(command=txt.yview)

        def run():
            res = func()
            txt.insert(tk.END, res)
            txt.config(state="disabled")

        threading.Thread(target=run, daemon=True).start()

    def clear_main(self):
        for w in self.main.winfo_children(): w.destroy()

   
    def enable_persist(self):
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
            path = os.path.abspath(sys.argv[0])
            val = f'"{sys.executable}" "{path}"'
            winreg.SetValueEx(key, "USSP_System_Engine", 0, winreg.REG_SZ, val)
            return "SUCCESS: USSP Persistence key written to Registry.\n→ Application will now launch automatically on Windows startup."
        except Exception as e:
            return f"ERROR: Access Denied. {e}"

    def export_forensic(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"USSP_Report_{timestamp}.txt"

            desktop = os.path.join(os.environ['USERPROFILE'], 'Desktop')
            report_path = os.path.join(desktop, filename)

            with open(report_path, "w", encoding="utf-8") as f:
                f.write(f"--- USSP FORENSIC REPORT ---\nDate: {timestamp}\n")
                f.write(f"CPU: {platform.processor()}\n")
                f.write(f"OS: {platform.platform()}\n")
                f.write(f"Machine: {platform.node()}\n")
                f.write("-" * 50 + "\n\n")
                f.write(USSPCore.run_ps("Get-Process | Select-Object Name, Id, CPU, WorkingSet | Sort-Object CPU -Descending | Select-Object -First 30"))

            return f"FORENSIC REPORT GENERATED\nPath: {report_path}\n\nPlease check your Desktop."

        except Exception as e:
            return f"EXPORT ERROR: {e}"

    def boot_to_windows(self):
        self.root.quit()

    def auto_register_persistence(self):
        try:
            self.enable_persist()  
        except:
            pass


if __name__ == "__main__":
    app = USSP()
    app.root.mainloop()