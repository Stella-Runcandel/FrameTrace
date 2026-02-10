// FrameTrace utility: Enumerate Windows video capture devices via Media Foundation.
//
// Build (MSVC Developer Command Prompt):
//   cl /EHsc /W4 /nologo tools\windows\mf_device_enum.cpp /link mfplat.lib mf.lib mfuuid.lib ole32.lib
//
// This program only enumerates devices and prints JSON to stdout.
// It does NOT open camera streams or process frames.

#include <mfapi.h>
#include <mfidl.h>
#include <mfobjects.h>
#include <windows.h>

#include <iostream>
#include <sstream>
#include <string>
#include <vector>

#pragma comment(lib, "mfplat.lib")
#pragma comment(lib, "mf.lib")
#pragma comment(lib, "mfuuid.lib")
#pragma comment(lib, "ole32.lib")

namespace {

std::string HResultToHex(HRESULT hr) {
    std::ostringstream os;
    os << "0x" << std::hex << std::uppercase << static_cast<unsigned long>(hr);
    return os.str();
}

std::string WideToUtf8(const wchar_t* input) {
    if (input == nullptr) {
        return "";
    }
    const int size = WideCharToMultiByte(
        CP_UTF8,
        0,
        input,
        -1,
        nullptr,
        0,
        nullptr,
        nullptr);
    if (size <= 0) {
        return "";
    }

    std::string output(static_cast<size_t>(size - 1), '\0');
    const int written = WideCharToMultiByte(
        CP_UTF8,
        0,
        input,
        -1,
        output.data(),
        size,
        nullptr,
        nullptr);

    if (written <= 0) {
        return "";
    }
    return output;
}

std::string JsonEscape(const std::string& text) {
    std::ostringstream os;
    for (unsigned char c : text) {
        switch (c) {
            case '"': os << "\\\""; break;
            case '\\': os << "\\\\"; break;
            case '\b': os << "\\b"; break;
            case '\f': os << "\\f"; break;
            case '\n': os << "\\n"; break;
            case '\r': os << "\\r"; break;
            case '\t': os << "\\t"; break;
            default:
                if (c < 0x20) {
                    os << "\\u00";
                    const char hex[] = "0123456789ABCDEF";
                    os << hex[(c >> 4) & 0x0F] << hex[c & 0x0F];
                } else {
                    os << c;
                }
                break;
        }
    }
    return os.str();
}

struct DeviceEntry {
    unsigned int index = 0;
    std::string friendly_name;
    std::string symbolic_link;
};

}  // namespace

int main() {
    HRESULT hr = CoInitializeEx(nullptr, COINIT_MULTITHREADED);
    const bool com_ready = SUCCEEDED(hr) || hr == RPC_E_CHANGED_MODE;
    const bool coinit_succeeded = SUCCEEDED(hr);
    if (!com_ready) {
        std::cerr << "Failed to initialize COM: " << HResultToHex(hr) << "\n";
        std::cout << "[]\n";
        return 1;
    }

    hr = MFStartup(MF_VERSION, MFSTARTUP_LITE);
    if (FAILED(hr)) {
        std::cerr << "MFStartup failed: " << HResultToHex(hr) << "\n";
        if (coinit_succeeded) {
            CoUninitialize();
        }
        std::cout << "[]\n";
        return 1;
    }

    IMFAttributes* attributes = nullptr;
    IMFActivate** devices = nullptr;
    UINT32 device_count = 0;
    std::vector<DeviceEntry> results;

    do {
        hr = MFCreateAttributes(&attributes, 1);
        if (FAILED(hr)) {
            std::cerr << "MFCreateAttributes failed: " << HResultToHex(hr) << "\n";
            break;
        }

        hr = attributes->SetGUID(
            MF_DEVSOURCE_ATTRIBUTE_SOURCE_TYPE,
            MF_DEVSOURCE_ATTRIBUTE_SOURCE_TYPE_VIDCAP_GUID);
        if (FAILED(hr)) {
            std::cerr << "SetGUID(MF_DEVSOURCE_ATTRIBUTE_SOURCE_TYPE) failed: " << HResultToHex(hr) << "\n";
            break;
        }

        hr = MFEnumDeviceSources(attributes, &devices, &device_count);
        if (FAILED(hr)) {
            std::cerr << "MFEnumDeviceSources failed: " << HResultToHex(hr) << "\n";
            break;
        }

        results.reserve(device_count);

        for (UINT32 i = 0; i < device_count; ++i) {
            wchar_t* friendly = nullptr;
            UINT32 friendly_len = 0;
            wchar_t* symbolic = nullptr;
            UINT32 symbolic_len = 0;

            DeviceEntry entry;
            entry.index = i;

            hr = devices[i]->GetAllocatedString(
                MF_DEVSOURCE_ATTRIBUTE_FRIENDLY_NAME,
                &friendly,
                &friendly_len);
            if (SUCCEEDED(hr) && friendly != nullptr) {
                entry.friendly_name = WideToUtf8(friendly);
            } else {
                entry.friendly_name = "";
            }

            hr = devices[i]->GetAllocatedString(
                MF_DEVSOURCE_ATTRIBUTE_SOURCE_TYPE_VIDCAP_SYMBOLIC_LINK,
                &symbolic,
                &symbolic_len);
            if (SUCCEEDED(hr) && symbolic != nullptr) {
                entry.symbolic_link = WideToUtf8(symbolic);
            } else {
                entry.symbolic_link = "";
            }

            if (friendly != nullptr) {
                CoTaskMemFree(friendly);
            }
            if (symbolic != nullptr) {
                CoTaskMemFree(symbolic);
            }

            results.push_back(std::move(entry));
        }
    } while (false);

    std::cout << "[\n";
    for (size_t i = 0; i < results.size(); ++i) {
        const DeviceEntry& d = results[i];
        std::cout << "  {\n"
                  << "    \"index\": " << d.index << ",\n"
                  << "    \"friendly_name\": \"" << JsonEscape(d.friendly_name) << "\",\n"
                  << "    \"symbolic_link\": \"" << JsonEscape(d.symbolic_link) << "\"\n"
                  << "  }";
        if (i + 1 < results.size()) {
            std::cout << ",";
        }
        std::cout << "\n";
    }
    std::cout << "]\n";

    if (devices != nullptr) {
        for (UINT32 i = 0; i < device_count; ++i) {
            if (devices[i] != nullptr) {
                devices[i]->Release();
            }
        }
        CoTaskMemFree(devices);
    }

    if (attributes != nullptr) {
        attributes->Release();
    }

    MFShutdown();
    if (coinit_succeeded) {
        CoUninitialize();
    }

    return 0;
}
