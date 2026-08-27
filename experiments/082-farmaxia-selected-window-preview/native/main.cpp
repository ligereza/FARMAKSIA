// Passive selected-window preview for FARMAXIA.
// Capture API usage follows Microsoft's MIT Windows.UI.Composition sample.

#include <windows.h>
#include <d3d11_4.h>
#include <dxgi1_6.h>
#include <DispatcherQueue.h>
#include <shobjidl_core.h>

#include <windows.graphics.capture.interop.h>
#include <windows.graphics.capture.h>
#include <winrt/base.h>
#include <winrt/Windows.Foundation.h>
#include <winrt/Windows.Graphics.Capture.h>
#include <winrt/Windows.Graphics.DirectX.h>
#include <winrt/Windows.Graphics.DirectX.Direct3D11.h>
#include <winrt/Windows.System.h>

#include <atomic>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <functional>
#include <memory>
#include <mutex>
#include <vector>

using namespace winrt;
using namespace Windows::Graphics::Capture;
using namespace Windows::Graphics::DirectX;
using namespace Windows::Graphics::DirectX::Direct3D11;

constexpr UINT kPreviewReady = WM_APP + 82;
constexpr int kSelectButton = 1001;

extern "C" HRESULT __stdcall CreateDirect3D11DeviceFromDXGIDevice(
    IDXGIDevice* dxgi_device, ::IInspectable** graphics_device);

struct __declspec(uuid("A9B3D012-3DF2-4EE3-B8D1-8695F457D3C1")) IDirect3DDxgiInterfaceAccess : ::IUnknown
{
    virtual HRESULT __stdcall GetInterface(GUID const& id, void** object) = 0;
};

template <typename T>
winrt::com_ptr<T> GetDXGIInterface(winrt::Windows::Foundation::IInspectable const& object)
{
    auto access = object.as<IDirect3DDxgiInterfaceAccess>();
    winrt::com_ptr<T> result;
    check_hresult(access->GetInterface(winrt::guid_of<T>(), result.put_void()));
    return result;
}

IDirect3DDevice CreateDevice()
{
    winrt::com_ptr<ID3D11Device> device;
    UINT flags = D3D11_CREATE_DEVICE_BGRA_SUPPORT;
    HRESULT hr = D3D11CreateDevice(nullptr, D3D_DRIVER_TYPE_HARDWARE, nullptr, flags,
        nullptr, 0, D3D11_SDK_VERSION, device.put(), nullptr, nullptr);
    if (hr == DXGI_ERROR_UNSUPPORTED) {
        hr = D3D11CreateDevice(nullptr, D3D_DRIVER_TYPE_WARP, nullptr, flags,
            nullptr, 0, D3D11_SDK_VERSION, device.put(), nullptr, nullptr);
    }
    check_hresult(hr);
    winrt::com_ptr<::IInspectable> wrapped;
    check_hresult(CreateDirect3D11DeviceFromDXGIDevice(device.as<IDXGIDevice>().get(), wrapped.put()));
    return wrapped.as<IDirect3DDevice>();
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

class PreviewCapture
{
public:
    using FrameCallback = std::function<void(int, int, std::vector<uint8_t> const&)>;

    PreviewCapture(IDirect3DDevice const& device, GraphicsCaptureItem const& item,
        HWND notify, FrameCallback callback)
        : m_device(device), m_item(item), m_notify(notify), m_callback(std::move(callback))
    {
        auto d3d_device = GetDXGIInterface<ID3D11Device>(m_device);
        d3d_device->GetImmediateContext(m_context.put());
        auto size = item.Size();
        m_frame_pool = Direct3D11CaptureFramePool::Create(m_device,
            DirectXPixelFormat::B8G8R8A8UIntNormalized, 2, size);
        m_session = m_frame_pool.CreateCaptureSession(m_item);
        m_frame_arrived = m_frame_pool.FrameArrived(auto_revoke,
            {this, &PreviewCapture::OnFrameArrived});
    }

    void Start() { m_session.StartCapture(); }

    void Close()
    {
        if (m_closed.exchange(true)) return;
        m_frame_arrived.revoke();
        if (m_session) m_session.Close();
        if (m_frame_pool) m_frame_pool.Close();
        m_staging = nullptr;
        m_context = nullptr;
    }

    ~PreviewCapture() { Close(); }

private:
    void OnFrameArrived(Direct3D11CaptureFramePool const& sender,
        winrt::Windows::Foundation::IInspectable const&)
    {
        if (m_closed) return;
        auto frame = sender.TryGetNextFrame();
        const auto size = frame.ContentSize();
        if (size.Width <= 0 || size.Height <= 0) return;
        auto source = GetDXGIInterface<ID3D11Texture2D>(frame.Surface());
        D3D11_TEXTURE2D_DESC desc{};
        source->GetDesc(&desc);
        if (!m_staging || m_width != size.Width || m_height != size.Height) {
            desc.BindFlags = 0;
            desc.MiscFlags = 0;
            desc.Usage = D3D11_USAGE_STAGING;
            desc.CPUAccessFlags = D3D11_CPU_ACCESS_READ;
            m_staging = nullptr;
            check_hresult(GetDXGIInterface<ID3D11Device>(m_device)->CreateTexture2D(
                &desc, nullptr, m_staging.put()));
            m_width = size.Width;
            m_height = size.Height;
        }
        m_context->CopyResource(m_staging.get(), source.get());
        D3D11_MAPPED_SUBRESOURCE mapped{};
        check_hresult(m_context->Map(m_staging.get(), 0, D3D11_MAP_READ, 0, &mapped));
        std::vector<uint8_t> pixels(static_cast<size_t>(m_width) * m_height * 4);
        for (int y = 0; y < m_height; ++y) {
            std::memcpy(pixels.data() + static_cast<size_t>(y) * m_width * 4,
                static_cast<uint8_t const*>(mapped.pData) + static_cast<size_t>(y) * mapped.RowPitch,
                static_cast<size_t>(m_width) * 4);
        }
        m_context->Unmap(m_staging.get(), 0);
        m_callback(m_width, m_height, pixels);
        PostMessage(m_notify, kPreviewReady, 0, 0);
    }

    IDirect3DDevice m_device{nullptr};
    GraphicsCaptureItem m_item{nullptr};
    Direct3D11CaptureFramePool m_frame_pool{nullptr};
    GraphicsCaptureSession m_session{nullptr};
    Direct3D11CaptureFramePool::FrameArrived_revoker m_frame_arrived{};
    winrt::com_ptr<ID3D11DeviceContext> m_context;
    winrt::com_ptr<ID3D11Texture2D> m_staging;
    HWND m_notify{};
    FrameCallback m_callback;
    std::atomic_bool m_closed{false};
    int m_width{};
    int m_height{};
};

class PreviewApp;
PreviewApp* g_app = nullptr;
LRESULT CALLBACK PreviewProc(HWND, UINT, WPARAM, LPARAM);

class PreviewApp
{
public:
    int Run(HINSTANCE instance)
    {
        if (!GraphicsCaptureSession::IsSupported()) {
            std::printf("FARMAXIA_082_PREVIEW={\"status\":\"WINDOW_PREVIEW_BLOCKED\",\"reason\":\"graphics_capture_unsupported\"}\n");
            return 2;
        }
        WNDCLASS window_class{};
        window_class.hInstance = instance;
        window_class.lpfnWndProc = PreviewProc;
        window_class.lpszClassName = L"Farmaxia082SelectedWindowPreview";
        window_class.hCursor = LoadCursor(nullptr, IDC_ARROW);
        if (!RegisterClass(&window_class) && GetLastError() != ERROR_CLASS_ALREADY_EXISTS) {
            throw hresult_error(HRESULT_FROM_WIN32(GetLastError()));
        }
        m_owner = CreateWindowEx(WS_EX_TOOLWINDOW, window_class.lpszClassName,
            L"FARMAKSIA preview", WS_OVERLAPPEDWINDOW,
            CW_USEDEFAULT, CW_USEDEFAULT, 900, 650, nullptr, nullptr, instance, nullptr);
        if (!m_owner) throw hresult_error(HRESULT_FROM_WIN32(GetLastError()));
        CreateWindow(L"BUTTON", L"Seleccionar ventana", WS_CHILD | WS_VISIBLE | BS_PUSHBUTTON,
            12, 12, 180, 34, m_owner, reinterpret_cast<HMENU>(static_cast<INT_PTR>(kSelectButton)), instance, nullptr);
        ShowWindow(m_owner, SW_SHOWNORMAL);
        UpdateWindow(m_owner);
        m_dispatcher = CreateDispatcherQueueController();
        MSG message{};
        while (GetMessage(&message, nullptr, 0, 0) > 0) {
            TranslateMessage(&message);
            DispatchMessage(&message);
        }
        std::printf("FARMAXIA_082_PREVIEW={\"status\":\"%s\",\"frames\":%d,\"window_capture\":%s,\"input_intercepted\":false,\"raw_content_persisted\":false}\n",
            m_selected ? "WINDOW_PREVIEW_SELECTED" : "WINDOW_PREVIEW_NOT_SELECTED",
            m_frames, m_selected ? "true" : "false");
        return 0;
    }

    void SelectWindow()
    {
        GraphicsCapturePicker picker;
        picker.as<IInitializeWithWindow>()->Initialize(m_owner);
        auto item = picker.PickSingleItemAsync().get();
        if (!item) return;
        m_capture = std::make_unique<PreviewCapture>(m_device ? m_device : (m_device = CreateDevice()),
            item, m_owner, [this](int width, int height, std::vector<uint8_t> const& pixels) {
                OnFrame(width, height, pixels);
            });
        m_capture->Start();
        m_selected = true;
        m_frames = 0;
        m_pixels.clear();
        InvalidateRect(m_owner, nullptr, FALSE);
    }

    void OnFrame(int width, int height, std::vector<uint8_t> const& pixels)
    {
        std::lock_guard lock(m_pixels_mutex);
        m_width = width;
        m_height = height;
        m_pixels = pixels;
        ++m_frames;
    }

    void Paint(HDC dc)
    {
        RECT client{};
        GetClientRect(m_owner, &client);
        RECT target{12, 62, client.right - 12, client.bottom - 12};
        FillRect(dc, &target, static_cast<HBRUSH>(GetStockObject(BLACK_BRUSH)));
        std::vector<uint8_t> pixels;
        int width{};
        int height{};
        {
            std::lock_guard lock(m_pixels_mutex);
            pixels = m_pixels;
            width = m_width;
            height = m_height;
        }
        if (pixels.empty() || width <= 0 || height <= 0) return;
        const double scale = min((target.right - target.left) / static_cast<double>(width),
            (target.bottom - target.top) / static_cast<double>(height));
        const int draw_width = static_cast<int>(width * scale);
        const int draw_height = static_cast<int>(height * scale);
        const int left = target.left + ((target.right - target.left) - draw_width) / 2;
        const int top = target.top + ((target.bottom - target.top) - draw_height) / 2;
        BITMAPINFO info{};
        info.bmiHeader.biSize = sizeof(BITMAPINFOHEADER);
        info.bmiHeader.biWidth = width;
        info.bmiHeader.biHeight = -height;
        info.bmiHeader.biPlanes = 1;
        info.bmiHeader.biBitCount = 32;
        info.bmiHeader.biCompression = BI_RGB;
        StretchDIBits(dc, left, top, draw_width, draw_height, 0, 0, width, height,
            pixels.data(), &info, DIB_RGB_COLORS, SRCCOPY);
    }

    void Close()
    {
        if (m_capture) m_capture->Close();
        m_capture.reset();
    }

private:
    HWND m_owner{};
    Windows::System::DispatcherQueueController m_dispatcher{nullptr};
    IDirect3DDevice m_device{nullptr};
    std::unique_ptr<PreviewCapture> m_capture;
    std::mutex m_pixels_mutex;
    std::vector<uint8_t> m_pixels;
    int m_width{};
    int m_height{};
    int m_frames{};
    bool m_selected{};
};

LRESULT CALLBACK PreviewProc(HWND window, UINT message, WPARAM w_param, LPARAM l_param)
{
    switch (message) {
    case WM_COMMAND:
        if (LOWORD(w_param) == kSelectButton) {
            g_app->SelectWindow();
            return 0;
        }
        break;
    case kPreviewReady:
        InvalidateRect(window, nullptr, FALSE);
        return 0;
    case WM_PAINT: {
        PAINTSTRUCT paint{};
        HDC dc = BeginPaint(window, &paint);
        g_app->Paint(dc);
        EndPaint(window, &paint);
        return 0;
    }
    case WM_KEYDOWN:
        if (w_param == VK_ESCAPE) DestroyWindow(window);
        return 0;
    case WM_DESTROY:
        g_app->Close();
        PostQuitMessage(0);
        return 0;
    }
    return DefWindowProc(window, message, w_param, l_param);
}

int main()
{
    try {
        SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2);
        init_apartment(apartment_type::single_threaded);
        PreviewApp app;
        g_app = &app;
        const int result = app.Run(GetModuleHandle(nullptr));
        g_app = nullptr;
        return result;
    } catch (hresult_error const& error) {
        std::printf("FARMAXIA_082_PREVIEW={\"status\":\"WINDOW_PREVIEW_BLOCKED\",\"reason\":\"hresult_0x%08X\"}\n", static_cast<unsigned int>(error.code()));
        return 2;
    } catch (...) {
        std::printf("FARMAXIA_082_PREVIEW={\"status\":\"WINDOW_PREVIEW_BLOCKED\",\"reason\":\"unknown_native_error\"}\n");
        return 2;
    }
}
