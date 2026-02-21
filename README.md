# USSP – Unofficial Secure Starting Protocol v3.1

**USSP** is a **Windows system audit and forensic inspection tool** with a user interface inspired by a **BIOS / pre‑boot environment**.

The BIOS-like appearance (fullscreen mode, keyboard navigation, hidden cursor, color palette) is **purely a visual and UX choice** and does **not** interact with the real BIOS, firmware, or bootloader in any way.

> ⚠️ **LEGAL DISCLAIMER**  
> This software is intended for **LEGAL and EDUCATIONAL use only**.  
> You must own the system or have explicit authorization to audit it.  
> Any unauthorized or illegal use is strictly prohibited.

---

## 🖥️ Features

### Hardware Inventory
- CPU architecture and cores
- Physical memory modules
- GPU and display adapters
- Disk and S.M.A.R.T. status
- Motherboard and BIOS details
- Logical drives and file systems

### Network Architecture
- TCP/UDP listening ports
- Active network adapters
- DNS cache
- Routing table
- ARP table
- Wi‑Fi profiles and visible networks
- Established connections

### OS & Security Kernel
- TPM status
- Windows Defender state
- Firewall profiles
- Secure Boot status
- BitLocker volumes
- UAC configuration
- Installed antivirus products
- Recent Windows hotfixes

### Persistence Audit
- Registry Run keys
- Scheduled tasks
- Startup folders
- Active services
- Winlogon and shell configuration
- Explorer startup approvals

### System Events (Live)
- Critical kernel events
- Application crash history
- Security critical events
- Power management events

### Forensic Tools
- Full system forensic report export
- Installed drivers
- Open network ports
- Installed software listing
- Process tree overview

### Boot Management
- Exit to Windows
- Optional auto‑start persistence (Windows Run key)

---

## 🎨 Interface & Theme

- **Fullscreen BIOS-style interface**
- **Keyboard-only navigation**
- **Hidden mouse cursor**
- **BIOS-inspired color scheme**:
  - Black background
  - Blue panels
  - Red headers
  - Yellow highlights
- Simulated boot sequence and status messages

> ℹ️ The BIOS look is **visual only** and meant to provide a retro, diagnostic-style experience.

---

## ⌨️ Keyboard Controls

| Key | Action |
|----|-------|
| ↑ / ↓ | Navigate menus |
| Enter | Execute selected action |
| ESC | Go back |
| F5 | Refresh current menu |
| F10 | Exit application |

---

## ⚙️ Installation

### Requirements
- Windows 10 / 11
- Python **3.9+**
- PowerShell enabled

### Setup

```bash
git clone https://github.com/<your-repo>/USSP.git
cd USSP
pip install -r requirements.txt
python USSP.py
````

---

## 💾 Forensic Report Export

* Reports are generated on the **Desktop**
* File format: `USSP_Report_YYYYMMDD_HHMMSS.txt`
* Includes:

  * System metadata
  * OS and hardware summary
  * Process snapshot
  * Key audit information

---

## ⚠️ Persistence Notice

USSP includes an **optional persistence mechanism** using the Windows registry:

```
HKCU\Software\Microsoft\Windows\CurrentVersion\Run
```

This is intended for **authorized audit or lab environments only**.
For public or enterprise use, persistence should be **disabled or made opt‑in**.

---

## 🔐 Security Notes

* No remote communication or data exfiltration
* No network exploitation features
* All actions are local and read‑only (except optional persistence)
* Designed as a **local audit & forensic inspection tool**

---

## 📌 Intended Use Cases

* System diagnostics
* Security auditing (authorized)
* Forensic analysis
* Training and lab environments
* Demonstration and educational purposes

---

## 🧾 License

This project is provided **as‑is**, without warranty.
Use responsibly and legally.

````

---

## 📦 `requirements.txt`

```text
pywin32
colorama
````

### Notes

* `tkinter` is included by default with standard Python installations on Windows
* `pywin32` is required for Windows registry access and system interaction
* `colorama` is optional but recommended for console color output (logs, debug, CLI tools)

  Made with ❤️

