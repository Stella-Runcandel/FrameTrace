# Media Foundation Video Device Enumerator (Windows)

This command-line tool lists **video capture devices** using the official Windows Media Foundation API and prints a JSON array to stdout.

## Source file

- `tools/windows/mf_device_enum.cpp`

## Build (MSVC)

Use a **Developer Command Prompt for Visual Studio**:

```bat
cl /EHsc /W4 /nologo tools\windows\mf_device_enum.cpp /link mfplat.lib mf.lib mfuuid.lib ole32.lib
```

Required libraries:

- `mfplat.lib`
- `mf.lib`
- `mfuuid.lib`
- `ole32.lib`

## Run

```bat
mf_device_enum.exe
```

## Example output

```json
[
  {
    "index": 0,
    "friendly_name": "HD USB Camera",
    "symbolic_link": "\\?\\usb#vid_046d&pid_0825&mi_00#7&..."
  },
  {
    "index": 1,
    "friendly_name": "Virtual Camera",
    "symbolic_link": "\\?\\root#media#0000#{...}"
  }
]
```

## Notes

- The tool only enumerates devices; it does **not** open capture streams.
- On failure, it prints `[]` and writes a diagnostic to stderr.
