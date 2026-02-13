<div align="center">

# ✨ FrameTrace ✨  
### Visual State Monitoring & Detection Tool  
**by Stella Group**

> *“Stop staring at the screen. Let FrameTrace do it.”*

</div>

---

## 👀 What is FrameTrace?

FrameTrace is a **profile-based visual monitoring desktop application**.

It watches a live video input (typically via OBS Virtual Camera), compares what it sees against user-defined visual references, and alerts you when a specific visual state appears on screen.

Everything runs **locally**:

- 🚫 No cloud services  
- 🚫 No accounts  
- 🚫 No background uploads  
- 🚫 No hidden automation  

FrameTrace is a deterministic, local-first monitoring tool built for control.

---

## 🎯 Detection & Monitoring

Monitoring runs directly against in-memory camera frames using:

```
frame_comp_from_array()
```

This avoids per-cycle disk writes and keeps detection fast.

When monitoring is active:

- Only the selected reference is evaluated  
- Detection uses edge-based matching (Canny + matchTemplate)  
- Bounding boxes are computed deterministically  

File-based detection (`frame_comp`) remains available for manual/debug workflows using `captures/latest.png`.

---

## 💾 Capture & Debug Retention

Artifact persistence is:

- Optional  
- Throttled  
- Bounded  

Configured in `core/detector.py`:

| Setting | Description |
|----------|------------|
| `DEBUG_STORAGE_LIMIT_BYTES` | Maximum debug storage (default 1GB) |
| `EXIT_TIMEOUT` | Time before event resets (default 0.6s) |

This guarantees:

- 📦 No unbounded disk growth  
- 🧮 Predictable storage usage  
- 🕒 Safe long-running sessions  

---

## 🧠 Design Philosophy

FrameTrace is intentionally:

- 🧠 **Deterministic** — no black-box AI  
- 🧱 **Modular** — clean separation between UI, detection, and data  
- 🧹 **Safe with files** — user data survives updates  
- 😴 **Predictable to extend** — boring, explicit code paths  

FrameTrace is not AI hype.  
It’s a local, power-user visual monitoring tool.

---

## 🏗 Architecture Overview

```
core/detector.py
    Edge-based template matching engine

core/profiles.py
    Profile + asset management

core/notifier.py
    Windows notification and alert system

app/services/monitor_service.py
    Camera capture and detection loop (QThread)
```

---

## 📦 Installation

Download the latest installer from:

👉 **GitHub → Releases → FrameTrace_Setup.exe**

- Installs per-user  
- No admin required  
- Data stored locally  

---

## 💽 Data & Updates

All user data is stored in:

```
Data/
```

Located next to the executable.

Includes:

- Profiles  
- Frames  
- References  
- Debug artifacts  
- Logs  

Updates do **not** overwrite user data.

---

## 🛠 Development

Clone repository:

```bash
git clone https://github.com/yourusername/FrameTrace.git
cd FrameTrace
```

Create virtual environment:

```bash
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run:

```bash
python run.py
```

---

## 📄 License

MIT License
