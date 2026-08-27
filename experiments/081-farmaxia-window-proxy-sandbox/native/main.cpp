// Derived from Microsoft's MIT Windows.UI.Composition-Win32-Samples capture
// path. This executable captures only the source HWND that it creates itself.

#include <windows.h>
#include <windowsx.h>
#include <d3d11_4.h>
#include <dxgi1_6.h>
#include <DispatcherQueue.h>
#include <windows.graphics.capture.interop.h>
#include <windows.graphics.capture.h>

#include <winrt/base.h>
#include <winrt/Windows.Foundation.h>
#include <winrt/Windows.Graphics.Capture.h>
#include <winrt/Windows.Graphics.DirectX.h>
#include <winrt/Windows.Graphics.DirectX.Direct3D11.h>
#include <winrt/Windows.System.h>

#include <array>
#include <atomic>
#include <cstdint>
#include <cstdio>
#include <functional>
#include <memory>
#include <mutex>
#include <string>
#include <vector>

using namespace winrt;
using namespace Windows::Graphics::Capture;
using namespace Windows::Graphics::DirectX;
using namespace Windows::Graphics::DirectX::Direct3D11;

constexpr int kSize = 320;
constexpr int kHalf = kSize / 2;
constexpr UINT kFrameReady = WM_APP + 81;
constexpr std::array<int, 4> destination_to_source{3, 2, 1, 0};

extern "C" HRESULT __stdcall CreateDirect3D11DeviceFromDXGIDevice(
    IDXGIDevice* dxgi_device, ::IInspectable** graphics_device);

struct __declspec(uuid("A9B3D012-3DF2-4EE3-B8D1-8695F457D3C1")) IDirect3DDxgiInterfaceAccess : ::IUnknown
{
    virtual HRESULT __stdcall GetInterface(GUID const& id, void** object) = 0;
};

template <typename T>
winrt::com_ptr<T> GetDXGIInterfaceFromObject(winrt::Windows::Foundation::IInspectable const& object)
{
    auto access = object.as<IDirect3DDxgiInterfaceAccess>();
    winrt::com_ptr<T> result;
    check_hresult(access->GetInterface(winrt::guid_of<T>(), result.put_void()));
    return result;
}

IDirect3DDevice CreateDirect3DDevice(IDXGIDevice* dxgi_device)
{
    winrt::com_ptr<::IInspectable> device;
    check_hresult(CreateDirect3D11DeviceFromDXGIDevice(dxgi_device, device.put()));
    return device.as<IDirect3DDevice>();
}

IDirect3DDevice CreateDevice()
{
    winrt::com_ptr<ID3D11Device> device;
    UINT flags = D3D11_CREATE_DEVICE_BGRA_SUPPORT;
    HRESULT hr = D3D11CreateDevice(nullptr, D3D_DRIVER_TYPE_HARDWARE, nullptr, flags, nullptr, 0,
        D3D11_SDK_VERSION, device.put(), nullptr, nullptr);
    if (hr == DXGI_ERROR_UNSUPPORTED) {
        hr = D3D11CreateDevice(nullptr, D3D_DRIVER_TYPE_WARP, nullptr, flags, nullptr, 0,
            D3D11_SDK_VERSION, device.put(), nullptr, nullptr);
    }
    check_hresult(hr);
    return CreateDirect3DDevice(device.as<IDXGIDevice>().get());
}

GraphicsCaptureItem CreateCaptureItemForWindow(HWND source_window)
{
    auto factory = get_activation_factory<GraphicsCaptureItem>();
    auto interop = factory.as<IGraphicsCaptureItemInterop>();
    GraphicsCaptureItem item{nullptr};
    check_hresult(interop->CreateForWindow(source_window,
        guid_of<ABI::Windows::Graphics::Capture::IGraphicsCaptureItem>(),
        reinterpret_cast<void**>(put_abi(item))));
    return item;
}

Windows::System::DispatcherQueueController CreateDispatcherQueueController()
{
    namespace abi = ABI::Windows::System;
    DispatcherQueueOptions options{sizeof(DispatcherQueueOptions), DQTYPE_THREAD_CURRENT, DQTAT_COM_STA};
    Windows::System::DispatcherQueueController controller{nullptr};
    check_hresult(::CreateDispatcherQueueController(options,
        reinterpret_cast<abi::IDispatcherQueueController**>(put_abi(controller))));
    return controller;
}

struct Pixel
{
    uint8_t b{};
    uint8_t g{};
    uint8_t r{};
    uint8_t a{};
    bool operator==(Pixel const& other) const
    {
        return b == other.b && g == other.g && r == other.r && a == other.a;
    }
    bool operator!=(Pixel const& other) const { return !(*this == other); }
};

LRESULT CALLBACK SourceProc(HWND window, UINT message, WPARAM w_param, LPARAM l_param);
LRESULT CALLBACK ProxyProc(HWND window, UINT message, WPARAM w_param, LPARAM l_param);

class ProbeCapture
{
public:
    ProbeCapture(IDirect3DDevice const& device, HWND source_window, HWND notify_window,
        std::function<void(std::vector<uint8_t> const&)> on_frame)
        : m_device(device), m_item(CreateCaptureItemForWindow(source_window)),
          m_notify(notify_window), m_on_frame(std::move(on_frame))
    {
        auto d3d_device = GetDXGIInterfaceFromObject<ID3D11Device>(m_device);
        d3d_device->GetImmediateContext(m_context.put());
        m_frame_pool = Direct3D11CaptureFramePool::Create(m_device,
            DirectXPixelFormat::B8G8R8A8UIntNormalized, 2, m_item.Size());
        m_session = m_frame_pool.CreateCaptureSession(m_item);
        m_frame_arrived = m_frame_pool.FrameArrived(auto_revoke, {this, &ProbeCapture::OnFrameArrived});
    }

    void Start() { m_session.StartCapture(); }

    void Close()
    {
        if (m_closed.exchange(true)) return;
        m_frame_arrived.revoke();
        m_session.Close();
        m_frame_pool.Close();
        m_staging = nullptr;
        m_context = nullptr;
    }

    ~ProbeCapture() { Close(); }

private:
    void OnFrameArrived(Direct3D11CaptureFramePool const& sender, winrt::Windows::Foundation::IInspectable const&)
    {
        if (m_closed) return;
        auto frame = sender.TryGetNextFrame();
        const auto size = frame.ContentSize();
        if (size.Width != kSize || size.Height != kSize) return;
        auto source = GetDXGIInterfaceFromObject<ID3D11Texture2D>(frame.Surface());
        D3D11_TEXTURE2D_DESC desc{};
        source->GetDesc(&desc);
        if (!m_staging) {
            desc.BindFlags = 0;
            desc.MiscFlags = 0;
            desc.Usage = D3D11_USAGE_STAGING;
            desc.CPUAccessFlags = D3D11_CPU_ACCESS_READ;
            check_hresult(GetDXGIInterfaceFromObject<ID3D11Device>(m_device)->CreateTexture2D(&desc, nullptr, m_staging.put()));
        }
        m_context->CopyResource(m_staging.get(), source.get());
        D3D11_MAPPED_SUBRESOURCE mapped{};
        check_hresult(m_context->Map(m_staging.get(), 0, D3D11_MAP_READ, 0, &mapped));
        std::vector<uint8_t> pixels(kSize * kSize * sizeof(Pixel));
        for (int y = 0; y < kSize; ++y) {
            std::memcpy(pixels.data() + y * kSize * sizeof(Pixel),
                static_cast<uint8_t const*>(mapped.pData) + y * mapped.RowPitch,
                kSize * sizeof(Pixel));
        }
        m_context->Unmap(m_staging.get(), 0);
        m_on_frame(pixels);
        PostMessage(m_notify, kFrameReady, 0, 0);
    }

    IDirect3DDevice m_device{nullptr};
    GraphicsCaptureItem m_item{nullptr};
    Direct3D11CaptureFramePool m_frame_pool{nullptr};
    GraphicsCaptureSession m_session{nullptr};
    Direct3D11CaptureFramePool::FrameArrived_revoker m_frame_arrived{};
    winrt::com_ptr<ID3D11DeviceContext> m_context;
    winrt::com_ptr<ID3D11Texture2D> m_staging;
    HWND m_notify{};
    std::function<void(std::vector<uint8_t> const&)> m_on_frame;
    std::atomic_bool m_closed{false};
};

class Sandbox;
Sandbox* g_sandbox = nullptr;

class Sandbox
{
public:
    int Run(HINSTANCE instance)
    {
        if (!GraphicsCaptureSession::IsSupported()) {
            EmitAndQuit("WINDOW_PROXY_SANDBOX_BLOCKED", "graphics_capture_unsupported");
            return 2;
        }
        m_started_at = GetTickCount64();
        Register(instance, L"Farmaxia081Source", SourceProc);
        Register(instance, L"Farmaxia081Proxy", ProxyProc);
        const int x = GetSystemMetrics(SM_XVIRTUALSCREEN) + 24;
        const int y = GetSystemMetrics(SM_YVIRTUALSCREEN) + 24;
        m_source = CreateWindowEx(WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE, L"Farmaxia081Source", L"",
            WS_POPUP, x, y, kSize, kSize, nullptr, nullptr, instance, nullptr);
        m_proxy = CreateWindowEx(WS_EX_TOOLWINDOW | WS_EX_NOACTIVATE, L"Farmaxia081Proxy", L"",
            WS_POPUP, x + kSize + 18, y, kSize, kSize, nullptr, nullptr, instance, nullptr);
        if (!m_source || !m_proxy) throw hresult_error(HRESULT_FROM_WIN32(GetLastError()));
        ShowWindow(m_source, SW_SHOWNOACTIVATE);
        ShowWindow(m_proxy, SW_SHOWNOACTIVATE);
        UpdateWindow(m_source);
        UpdateWindow(m_proxy);
        m_dispatcher = CreateDispatcherQueueController();
        m_capture = std::make_unique<ProbeCapture>(CreateDevice(), m_source, m_proxy,
            [this](std::vector<uint8_t> const& pixels) { OnFrame(pixels); });
        m_capture->Start();
        SetTimer(m_source, 81, 40, nullptr);
        MSG message{};
        while (GetMessage(&message, nullptr, 0, 0) > 0) {
            TranslateMessage(&message);
            DispatchMessage(&message);
        }
        return m_exit_code;
    }

    void PaintSource(HDC dc)
    {
        for (int tile = 0; tile < 4; ++tile) {
            RECT rect{(tile % 2) * kHalf, (tile / 2) * kHalf, (tile % 2 + 1) * kHalf, (tile / 2 + 1) * kHalf};
            COLORREF color = tile == m_selected ? RGB(255, 0, 255) : BaseColor(tile);
            HBRUSH brush = CreateSolidBrush(color);
            FillRect(dc, &rect, brush);
            DeleteObject(brush);
        }
    }

    void PaintProxy(HDC dc)
    {
        std::vector<uint8_t> pixels;
        {
            std::lock_guard lock(m_pixels_mutex);
            pixels = m_proxy_pixels;
        }
        if (pixels.size() != kSize * kSize * sizeof(Pixel)) return;
        BITMAPINFO info{};
        info.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
        info.bmiHeader.biWidth = kSize;
        info.bmiHeader.biHeight = -kSize;
        info.bmiHeader.biPlanes = 1;
        info.bmiHeader.biBitCount = 32;
        info.bmiHeader.biCompression = BI_RGB;
        StretchDIBits(dc, 0, 0, kSize, kSize, 0, 0, kSize, kSize, pixels.data(), &info, DIB_RGB_COLORS, SRCCOPY);
    }

    void SelectSourceAt(int x, int y)
    {
        if (x < 0 || y < 0 || x >= kSize || y >= kSize) return;
        m_selected = (x >= kHalf ? 1 : 0) + (y >= kHalf ? 2 : 0);
        InvalidateRect(m_source, nullptr, FALSE);
    }

    void Tick()
    {
        if (!m_routed && m_source_frames >= 1) {
            RouteProxyClick(3 * kHalf / 2, 3 * kHalf / 2);
            m_routed = true;
        }
        if (m_routed && m_post_route_frames >= 1) Validate();
        if (GetTickCount64() - m_started_at > 8000) EmitAndQuit("WINDOW_PROXY_SANDBOX_BLOCKED", "capture_timeout");
    }

    void InvalidateProxy() { InvalidateRect(m_proxy, nullptr, FALSE); }

private:
    static COLORREF BaseColor(int tile)
    {
        constexpr std::array<COLORREF, 4> colors{RGB(255, 0, 0), RGB(0, 255, 0), RGB(0, 0, 255), RGB(255, 255, 0)};
        return colors.at(tile);
    }

    void OnFrame(std::vector<uint8_t> const& source)
    {
        std::lock_guard lock(m_pixels_mutex);
        ++m_source_frames;
        if (!m_routed) m_before = Samples(source);
        else ++m_post_route_frames;
        m_after = Samples(source);
        m_proxy_pixels.assign(source.size(), 0);
        for (int destination = 0; destination < 4; ++destination) {
            const int source_tile = destination_to_source.at(destination);
            for (int row = 0; row < kHalf; ++row) {
                const size_t from = ((source_tile / 2) * kHalf + row) * kSize + (source_tile % 2) * kHalf;
                const size_t to = ((destination / 2) * kHalf + row) * kSize + (destination % 2) * kHalf;
                std::memcpy(m_proxy_pixels.data() + to * sizeof(Pixel), source.data() + from * sizeof(Pixel), kHalf * sizeof(Pixel));
            }
        }
        m_proxy_samples = Samples(m_proxy_pixels);
    }

    static std::array<Pixel, 4> Samples(std::vector<uint8_t> const& pixels)
    {
        std::array<Pixel, 4> result{};
        for (int tile = 0; tile < 4; ++tile) {
            const int x = (tile % 2) * kHalf + kHalf / 2;
            const int y = (tile / 2) * kHalf + kHalf / 2;
            std::memcpy(&result.at(tile), pixels.data() + (y * kSize + x) * sizeof(Pixel), sizeof(Pixel));
        }
        return result;
    }

    void RouteProxyClick(int proxy_x, int proxy_y)
    {
        const int destination = (proxy_x >= kHalf ? 1 : 0) + (proxy_y >= kHalf ? 2 : 0);
        const int source_tile = destination_to_source.at(destination);
        const int source_x = (source_tile % 2) * kHalf + proxy_x % kHalf;
        const int source_y = (source_tile / 2) * kHalf + proxy_y % kHalf;
        SendMessage(m_source, WM_LBUTTONDOWN, MK_LBUTTON, MAKELPARAM(source_x, source_y));
        SendMessage(m_source, WM_LBUTTONUP, 0, MAKELPARAM(source_x, source_y));
    }

    void Validate()
    {
        bool pixels_match = true;
        for (int destination = 0; destination < 4; ++destination) {
            pixels_match = pixels_match && m_proxy_samples.at(destination) == m_after.at(destination_to_source.at(destination));
        }
        const bool source_changed = m_before.at(0) != m_after.at(0);
        const bool routed_expected_source = m_selected == 0;
        const bool inverse_round_trip = destination_to_source.at(3) == 0;
        if (pixels_match && source_changed && routed_expected_source && inverse_round_trip) {
            EmitAndQuit("WINDOW_PROXY_SANDBOX_VERIFIED", "capture_transform_inverse_mapping");
        } else {
            EmitAndQuit("WINDOW_PROXY_SANDBOX_BLOCKED", "pixel_or_inverse_contract_failed");
        }
    }

    void EmitAndQuit(char const* status, char const* reason)
    {
        if (m_finished.exchange(true)) return;
        if (m_capture) m_capture->Close();
        KillTimer(m_source, 81);
        std::printf("FARMAXIA_081_NATIVE={\"status\":\"%s\",\"reason\":\"%s\",\"source_frames\":%d,\"post_route_frames\":%d,\"external_window_capture\":false,\"system_input_injected\":false,\"screen_capture\":false}\n",
            status, reason, m_source_frames, m_post_route_frames);
        std::fflush(stdout);
        m_exit_code = std::string(status) == "WINDOW_PROXY_SANDBOX_VERIFIED" ? 0 : 2;
        if (m_proxy) DestroyWindow(m_proxy);
        if (m_source) DestroyWindow(m_source);
        PostQuitMessage(m_exit_code);
    }

    static void Register(HINSTANCE instance, wchar_t const* name, WNDPROC procedure)
    {
        WNDCLASS window_class{};
        window_class.hInstance = instance;
        window_class.lpfnWndProc = procedure;
        window_class.lpszClassName = name;
        window_class.hCursor = LoadCursor(nullptr, IDC_ARROW);
        if (!RegisterClass(&window_class) && GetLastError() != ERROR_CLASS_ALREADY_EXISTS) {
            throw hresult_error(HRESULT_FROM_WIN32(GetLastError()));
        }
    }

    HWND m_source{};
    HWND m_proxy{};
    Windows::System::DispatcherQueueController m_dispatcher{nullptr};
    std::unique_ptr<ProbeCapture> m_capture;
    std::mutex m_pixels_mutex;
    std::vector<uint8_t> m_proxy_pixels;
    std::array<Pixel, 4> m_before{};
    std::array<Pixel, 4> m_after{};
    std::array<Pixel, 4> m_proxy_samples{};
    ULONGLONG m_started_at{};
    int m_source_frames{};
    int m_post_route_frames{};
    int m_selected{-1};
    int m_exit_code{};
    bool m_routed{};
    std::atomic_bool m_finished{false};
};

LRESULT CALLBACK SourceProc(HWND window, UINT message, WPARAM w_param, LPARAM l_param)
{
    switch (message) {
    case WM_PAINT: {
        PAINTSTRUCT paint{};
        HDC dc = BeginPaint(window, &paint);
        g_sandbox->PaintSource(dc);
        EndPaint(window, &paint);
        return 0;
    }
    case WM_LBUTTONDOWN:
        g_sandbox->SelectSourceAt(GET_X_LPARAM(l_param), GET_Y_LPARAM(l_param));
        return 0;
    case WM_TIMER:
        g_sandbox->Tick();
        return 0;
    }
    return DefWindowProc(window, message, w_param, l_param);
}

LRESULT CALLBACK ProxyProc(HWND window, UINT message, WPARAM w_param, LPARAM l_param)
{
    switch (message) {
    case kFrameReady:
        g_sandbox->InvalidateProxy();
        return 0;
    case WM_PAINT: {
        PAINTSTRUCT paint{};
        HDC dc = BeginPaint(window, &paint);
        g_sandbox->PaintProxy(dc);
        EndPaint(window, &paint);
        return 0;
    }
    }
    return DefWindowProc(window, message, w_param, l_param);
}

int main()
{
    try {
        SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2);
        init_apartment(apartment_type::single_threaded);
        Sandbox sandbox;
        g_sandbox = &sandbox;
        const int result = sandbox.Run(GetModuleHandle(nullptr));
        g_sandbox = nullptr;
        return result;
    } catch (hresult_error const& error) {
        std::printf("FARMAXIA_081_NATIVE={\"status\":\"WINDOW_PROXY_SANDBOX_BLOCKED\",\"reason\":\"hresult_0x%08X\"}\n", static_cast<unsigned int>(error.code()));
        return 2;
    } catch (...) {
        std::printf("FARMAXIA_081_NATIVE={\"status\":\"WINDOW_PROXY_SANDBOX_BLOCKED\",\"reason\":\"unknown_native_error\"}\n");
        return 2;
    }
}
