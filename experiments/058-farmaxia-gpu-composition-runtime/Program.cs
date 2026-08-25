using System.Collections.Concurrent;
using System.Diagnostics;
using System.Numerics;
using System.Runtime.InteropServices;
using System.Text.Json;
using System.Threading;
using Vortice.D3DCompiler;
using Vortice.Direct3D;
using Vortice.Direct3D11;
using Vortice.DirectComposition;
using Vortice.DXGI;

return GpuCompositionOverlay.Run(Arguments.Parse(args));

internal sealed record Arguments(double DurationSeconds, double UpdateHz, bool Marker, bool NoPointer, bool Stdin)
{
    public static Arguments Parse(string[] args)
    {
        double duration = 5.0;
        double hz = 30.0;
        bool marker = false;
        bool noPointer = false;
        bool stdin = false;

        for (int i = 0; i < args.Length; i++)
        {
            switch (args[i].ToLowerInvariant())
            {
                case "--duration" when i + 1 < args.Length && double.TryParse(args[++i], out var parsedDuration):
                    duration = Math.Clamp(parsedDuration, 0.1, 3600.0);
                    break;
                case "--hz" when i + 1 < args.Length && double.TryParse(args[++i], out var parsedHz):
                    hz = Math.Clamp(parsedHz, 1.0, 120.0);
                    break;
                case "--marker":
                    marker = true;
                    break;
                case "--no-pointer":
                    noPointer = true;
                    break;
                case "--stdin":
                    stdin = true;
                    break;
            }
        }

        return new Arguments(duration, hz, marker, noPointer, stdin);
    }
}

internal static class GpuCompositionOverlay
{
    public static int Run(Arguments arguments)
    {
        using var process = Process.GetCurrentProcess();
        var wall = Stopwatch.StartNew();
        TimeSpan cpuStart = process.TotalProcessorTime;
        OverlayMetrics metrics = new();

        try
        {
            using var window = new OverlayWindow();
            using var renderer = new CompositionRenderer(window.Handle, window.Width, window.Height);
            PointerPlan initialPlan = new(window.Width, window.Height, arguments.Marker, arguments.NoPointer || arguments.Stdin ? null : Native.GetCursor(window.OriginX, window.OriginY));
            renderer.RenderPlan(initialPlan);
            window.Show();

            Console.WriteLine($"058 overlay active: backend=d3d11-directcomposition origin=({window.OriginX},{window.OriginY}) size={window.Width}x{window.Height} pointer={!arguments.NoPointer && !arguments.Stdin} stdin={arguments.Stdin}");

            var commands = new ConcurrentQueue<RenderCommand>();
            if (arguments.Stdin)
            {
                var reader = new Thread(() => ReadCommands(commands, window.OriginX, window.OriginY, window.Width, window.Height))
                {
                    IsBackground = true,
                    Name = "farmaxia-058-stdin",
                };
                reader.Start();
            }

            long lastPlanTick = Stopwatch.GetTimestamp();
            long deadline = lastPlanTick + (long)(arguments.DurationSeconds * Stopwatch.Frequency);
            long updateTicks = Math.Max(1, (long)(Stopwatch.Frequency / arguments.UpdateHz));
            PointerPlan currentPlan = initialPlan;
            Point lastPoint = initialPlan.Point ?? new Point(int.MinValue, int.MinValue);
            metrics.PlanUpdates++;
            metrics.PresentedFrames++;

            while (Stopwatch.GetTimestamp() < deadline)
            {
                Native.PumpMessages(ref metrics);
                if (metrics.QuitRequested)
                    break;

                long now = Stopwatch.GetTimestamp();
                if (now - lastPlanTick >= updateTicks)
                {
                    lastPlanTick = now;
                    bool dirty = false;
                    bool stopAfterRender = false;
                    while (commands.TryDequeue(out RenderCommand command))
                    {
                        if (command.Stop)
                        {
                            stopAfterRender = true;
                            continue;
                        }
                        if (command.Plan is not null)
                        {
                            currentPlan = command.Plan.Value;
                            dirty = true;
                        }
                    }

                    if (!arguments.NoPointer && !arguments.Stdin)
                    {
                        Point? point = Native.GetCursor(window.OriginX, window.OriginY);
                        if (point is not null && point.Value != lastPoint)
                        {
                            currentPlan = new PointerPlan(window.Width, window.Height, arguments.Marker, point);
                            lastPoint = point.Value;
                            dirty = true;
                        }
                    }

                    if (dirty)
                    {
                        renderer.RenderPlan(currentPlan);
                        metrics.PlanUpdates++;
                        metrics.PresentedFrames++;
                    }

                    if (stopAfterRender)
                    {
                        metrics.QuitRequested = true;
                        break;
                    }
                }

                Thread.Sleep(1);
            }

            Console.WriteLine($"058 overlay stopped: plans={metrics.PlanUpdates} presents={metrics.PresentedFrames} messages={metrics.Messages} quit={metrics.QuitRequested}");
            return 0;
        }
        catch (Exception error)
        {
            Console.Error.WriteLine($"058 overlay failed: {error.GetType().Name}: {error.Message}");
            Console.Error.WriteLine(error.StackTrace);
            return 1;
        }
        finally
        {
            wall.Stop();
            process.Refresh();
            double cpuMs = (process.TotalProcessorTime - cpuStart).TotalMilliseconds;
            Console.WriteLine($"058 metrics: wall_ms={wall.Elapsed.TotalMilliseconds:F1} cpu_ms={cpuMs:F1} cpu_pct={(cpuMs / Math.Max(1.0, wall.Elapsed.TotalMilliseconds) * 100.0):F1}");
        }
    }

    private static void ReadCommands(ConcurrentQueue<RenderCommand> commands, int originX, int originY, int width, int height)
    {
        try
        {
            string? line;
            while ((line = Console.ReadLine()) is not null)
            {
                try
                {
                    using JsonDocument document = JsonDocument.Parse(line);
                    JsonElement root = document.RootElement;
                    string type = root.TryGetProperty("type", out JsonElement typeElement) ? typeElement.GetString() ?? "" : "";
                    if (string.Equals(type, "stop", StringComparison.OrdinalIgnoreCase))
                    {
                        commands.Enqueue(new RenderCommand(null, true));
                        continue;
                    }

                    if (!string.Equals(type, "focus", StringComparison.OrdinalIgnoreCase))
                        continue;

                    float x = root.GetProperty("x").GetSingle();
                    float y = root.GetProperty("y").GetSingle();
                    float radius = root.TryGetProperty("radius_px", out JsonElement radiusElement) ? Math.Clamp(radiusElement.GetSingle(), 32.0f, Math.Max(width, height)) : 280.0f;
                    float dimAlpha = root.TryGetProperty("dim_alpha", out JsonElement dimElement) ? Math.Clamp(dimElement.GetSingle(), 0.0f, 0.8f) : 0.15f;
                    float ringAlpha = root.TryGetProperty("ring_alpha", out JsonElement ringElement) ? Math.Clamp(ringElement.GetSingle(), 0.0f, 0.4f) : 0.07f;
                    bool marker = root.TryGetProperty("marker", out JsonElement markerElement) && markerElement.GetBoolean();
                    Point point = new((int)Math.Round(x - originX), (int)Math.Round(y - originY));
                    commands.Enqueue(new RenderCommand(new PointerPlan(width, height, marker, point, radius, dimAlpha, ringAlpha), false));
                }
                catch (Exception error)
                {
                    Console.Error.WriteLine($"058 stdin ignored: {error.Message}");
                }
            }
        }
        catch (Exception error)
        {
            Console.Error.WriteLine($"058 stdin stopped: {error.Message}");
        }
    }
}

internal sealed class OverlayMetrics
{
    public int PlanUpdates;
    public int PresentedFrames;
    public int Messages;
    public bool QuitRequested;
}

internal readonly record struct Point(int X, int Y);

internal readonly record struct PointerPlan(
    int Width,
    int Height,
    bool Marker,
    Point? Point,
    float RadiusPx = 280.0f,
    float DimAlpha = 0.15f,
    float RingAlpha = 0.07f)
{
    public PlanConstants ToConstants()
    {
        float x = Point is null ? 0.5f : Math.Clamp((Point.Value.X + 0.5f) / Width, 0.0f, 1.0f);
        float y = Point is null ? 0.5f : Math.Clamp((Point.Value.Y + 0.5f) / Height, 0.0f, 1.0f);
        return new PlanConstants(new Vector4(x, y, RadiusPx / Height, DimAlpha), new Vector4(Width, Height, Marker ? 1.0f : 0.0f, RingAlpha));
    }
}

internal readonly record struct RenderCommand(PointerPlan? Plan, bool Stop);

[StructLayout(LayoutKind.Sequential)]
internal struct PlanConstants
{
    public Vector4 Focus;
    public Vector4 Screen;

    public PlanConstants(Vector4 focus, Vector4 screen)
    {
        Focus = focus;
        Screen = screen;
    }
}

internal sealed class CompositionRenderer : IDisposable
{
    private const string ShaderSource = """
cbuffer Plan : register(b0)
{
    float4 Focus;
    float4 Screen;
};

struct VertexOut
{
    float4 Position : SV_Position;
};

VertexOut VS(uint id : SV_VertexID)
{
    float2 positions[3] = {
        float2(-1.0, -1.0),
        float2(-1.0,  3.0),
        float2( 3.0, -1.0)
    };

    VertexOut output;
    output.Position = float4(positions[id], 0.0, 1.0);
    return output;
}

float4 PS(VertexOut input) : SV_Target
{
    float2 uv = input.Position.xy / Screen.xy;
    float2 delta = (uv - Focus.xy) * float2(Screen.x / Screen.y, 1.0);
    float distanceFromFocus = length(delta);
    float radius = Focus.z;
    float dim = smoothstep(radius * 0.72, radius * 1.08, distanceFromFocus);
    float ringOuter = 1.0 - smoothstep(radius, radius + 0.008, distanceFromFocus);
    float ringInner = 1.0 - smoothstep(radius - 0.008, radius, distanceFromFocus);
    float ring = saturate(ringOuter - ringInner);
    float marker = Screen.z * ring;

    float alpha = saturate(Focus.w * dim + Screen.w * marker);
    float3 color = float3(0.035, 0.050, 0.080) * alpha;
    color += float3(0.08, 0.15, 0.24) * (0.07 * marker);
    return float4(color, alpha);
}
""";

    private readonly IntPtr _windowHandle;
    private readonly int _width;
    private readonly int _height;
    private readonly ID3D11Device _device;
    private readonly ID3D11DeviceContext _context;
    private readonly IDXGISwapChain1 _swapChain;
    private readonly ID3D11RenderTargetView _renderTarget;
    private readonly ID3D11VertexShader _vertexShader;
    private readonly ID3D11PixelShader _pixelShader;
    private readonly ID3D11Buffer _planBuffer;
    private readonly IDCompositionDevice _compositionDevice;
    private readonly IDCompositionTarget _compositionTarget;
    private readonly IDCompositionVisual _compositionVisual;

    public CompositionRenderer(IntPtr windowHandle, int width, int height)
    {
        _windowHandle = windowHandle;
        _width = width;
        _height = height;

        FeatureLevel[] levels = { FeatureLevel.Level_11_1, FeatureLevel.Level_11_0 };
        D3D11.D3D11CreateDevice(
            IntPtr.Zero,
            DriverType.Hardware,
            DeviceCreationFlags.BgraSupport,
            levels,
            out _device,
            out _,
            out _context).CheckError();

        using IDXGIDevice dxgiDevice = _device.QueryInterface<IDXGIDevice>();
        using IDXGIFactory2 factory = DXGI.CreateDXGIFactory2<IDXGIFactory2>(false);

        var description = new SwapChainDescription1(
            (uint)width,
            (uint)height,
            Format.B8G8R8A8_UNorm,
            false,
            Usage.RenderTargetOutput,
            2,
            Scaling.Stretch,
            SwapEffect.FlipSequential,
            AlphaMode.Premultiplied,
            SwapChainFlags.None);

        _swapChain = factory.CreateSwapChainForComposition(_device, description, null);
        using ID3D11Texture2D backBuffer = _swapChain.GetBuffer<ID3D11Texture2D>(0);
        _renderTarget = _device.CreateRenderTargetView(backBuffer, null);

        ReadOnlyMemory<byte> vertexBytecode = Compiler.Compile(ShaderSource, "VS", "farmaxia_focus.hlsl", "vs_5_0");
        ReadOnlyMemory<byte> pixelBytecode = Compiler.Compile(ShaderSource, "PS", "farmaxia_focus.hlsl", "ps_5_0");
        _vertexShader = _device.CreateVertexShader(vertexBytecode.Span);
        _pixelShader = _device.CreatePixelShader(pixelBytecode.Span);
        _planBuffer = _device.CreateBuffer(new[] { new PlanConstants(Vector4.Zero, Vector4.Zero) }, BindFlags.ConstantBuffer, ResourceUsage.Default, CpuAccessFlags.None, ResourceOptionFlags.None, 0, 0);

        DComp.DCompositionCreateDevice(dxgiDevice, out IDCompositionDevice? compositionDevice).CheckError();
        _compositionDevice = compositionDevice ?? throw new InvalidOperationException("DirectComposition device was not returned.");
        _compositionDevice.CreateTargetForHwnd(_windowHandle, true, out IDCompositionTarget? compositionTarget).CheckError();
        _compositionTarget = compositionTarget ?? throw new InvalidOperationException("DirectComposition target was not returned.");
        _compositionDevice.CreateVisual(out IDCompositionVisual? compositionVisual).CheckError();
        _compositionVisual = compositionVisual ?? throw new InvalidOperationException("DirectComposition visual was not returned.");
        _compositionVisual.SetContent(_swapChain).CheckError();
        _compositionTarget.SetRoot(_compositionVisual).CheckError();
        _compositionDevice.Commit().CheckError();
    }

    public void RenderPlan(PointerPlan plan)
    {
        PlanConstants constants = plan.ToConstants();
        _context.UpdateSubresource(in constants, _planBuffer, 0, 0, 0, null);
        _context.IASetPrimitiveTopology(PrimitiveTopology.TriangleList);
        _context.VSSetShader(_vertexShader, null, 0);
        _context.PSSetShader(_pixelShader, null, 0);
        _context.PSSetConstantBuffer(0, _planBuffer);
        _context.RSSetViewport(new Vortice.Mathematics.Viewport(0, 0, _width, _height, 0, 1));
        _context.OMSetRenderTargets(_renderTarget);
        _context.Draw(3, 0);
        _swapChain.Present(1, PresentFlags.None).CheckError();
    }

    public void Dispose()
    {
        _compositionDevice.Commit();
        _compositionVisual.Dispose();
        _compositionTarget.Dispose();
        _compositionDevice.Dispose();
        _planBuffer.Dispose();
        _pixelShader.Dispose();
        _vertexShader.Dispose();
        _renderTarget.Dispose();
        _swapChain.Dispose();
        _context.Dispose();
        _device.Dispose();
    }

}

internal sealed class OverlayWindow : IDisposable
{
    private const int CS_HREDRAW = 0x0002;
    private const int CS_VREDRAW = 0x0001;
    private const int WS_POPUP = unchecked((int)0x80000000);
    private const int WS_EX_LAYERED = 0x00080000;
    private const int WS_EX_NOACTIVATE = 0x08000000;
    private const int WS_EX_TOOLWINDOW = 0x00000080;
    private const int WS_EX_TRANSPARENT = 0x00000020;
    private const int WS_EX_NOREDIRECTIONBITMAP = 0x00200000;
    private const uint SWP_SHOWWINDOW = 0x0040;
    private const int SW_SHOWNOACTIVATE = 4;
    private static readonly IntPtr HWND_TOPMOST = new(-1);
    private static readonly IntPtr IDC_ARROW = new(32512);
    private static readonly Native.WndProc WindowProcedure = WindowProc;
    private static ushort _classAtom;

    public IntPtr Handle { get; }
    public int OriginX { get; }
    public int OriginY { get; }
    public int Width { get; }
    public int Height { get; }

    public OverlayWindow()
    {
        Native.SetProcessDpiAwarenessContext(new IntPtr(-4));
        OriginX = Native.GetSystemMetrics(76);
        OriginY = Native.GetSystemMetrics(77);
        Width = Native.GetSystemMetrics(78);
        Height = Native.GetSystemMetrics(79);
        if (Width <= 0 || Height <= 0)
            throw new InvalidOperationException("Virtual desktop metrics are invalid.");

        string className = "FARMAXIA_058_GPU_COMPOSITION";
        if (_classAtom == 0)
        {
            var windowClass = new Native.WndClassEx
            {
                Size = (uint)Marshal.SizeOf<Native.WndClassEx>(),
                Style = CS_HREDRAW | CS_VREDRAW,
                WindowProcedure = WindowProcedure,
                Instance = Native.GetModuleHandle(null),
                Cursor = Native.LoadCursor(IntPtr.Zero, IDC_ARROW),
                ClassName = className,
            };
            _classAtom = Native.RegisterClassEx(ref windowClass);
            if (_classAtom == 0)
                throw new InvalidOperationException($"RegisterClassEx failed: {Marshal.GetLastWin32Error()}");
        }

        Handle = Native.CreateWindowEx(
            // WS_EX_LAYERED is intentional here: with WS_EX_TRANSPARENT it makes
            // the hit-test pass through to windows in other processes. The pixels
            // still come from the DComp premultiplied flip chain, not from a
            // legacy CPU-side layered presentation path.
            WS_EX_LAYERED | WS_EX_NOACTIVATE | WS_EX_TOOLWINDOW | WS_EX_TRANSPARENT | WS_EX_NOREDIRECTIONBITMAP,
            className,
            "FARMAXIA VIZZ composition overlay",
            WS_POPUP,
            OriginX,
            OriginY,
            Width,
            Height,
            IntPtr.Zero,
            IntPtr.Zero,
            Native.GetModuleHandle(null),
            IntPtr.Zero);

        if (Handle == IntPtr.Zero)
            throw new InvalidOperationException($"CreateWindowEx failed: {Marshal.GetLastWin32Error()}");
    }

    public void Show()
    {
        if (!Native.SetWindowPos(Handle, HWND_TOPMOST, OriginX, OriginY, Width, Height, SWP_SHOWWINDOW))
            throw new InvalidOperationException($"SetWindowPos failed: {Marshal.GetLastWin32Error()}");
        Native.ShowWindow(Handle, SW_SHOWNOACTIVATE);
        Native.UpdateWindow(Handle);
    }

    public void Dispose()
    {
        if (Handle != IntPtr.Zero)
            Native.DestroyWindow(Handle);
    }

    private static IntPtr WindowProc(IntPtr window, uint message, IntPtr wParam, IntPtr lParam)
    {
        return message switch
        {
            0x0084 => new IntPtr(-1), // WM_NCHITTEST -> HTTRANSPARENT
            0x0021 => new IntPtr(3),  // WM_MOUSEACTIVATE -> MA_NOACTIVATE
            0x0010 => IntPtr.Zero,
            _ => Native.DefWindowProc(window, message, wParam, lParam),
        };
    }
}

internal static class Native
{
    private const uint PM_REMOVE = 0x0001;
    private const uint WM_QUIT = 0x0012;
    private const uint QS_ALLINPUT = 0x04FF;

    public static Point? GetCursor(int originX, int originY)
    {
        if (!GetCursorPos(out NativePoint point))
            return null;
        return new Point(point.X - originX, point.Y - originY);
    }

    public static void PumpMessages(ref OverlayMetrics metrics)
    {
        while (PeekMessage(out Message message, IntPtr.Zero, 0, 0, PM_REMOVE))
        {
            metrics.Messages++;
            if (message.MessageId == WM_QUIT)
            {
                metrics.QuitRequested = true;
                return;
            }
            TranslateMessage(ref message);
            DispatchMessage(ref message);
        }
    }

    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool SetProcessDpiAwarenessContext(IntPtr dpiContext);

    [DllImport("user32.dll", SetLastError = true)]
    public static extern int GetSystemMetrics(int index);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool GetCursorPos(out NativePoint point);

    [DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    public static extern ushort RegisterClassEx(ref WndClassEx windowClass);

    [DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    public static extern IntPtr CreateWindowEx(int extendedStyle, string className, string windowName, int style, int x, int y, int width, int height, IntPtr parent, IntPtr menu, IntPtr instance, IntPtr parameter);

    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool SetWindowPos(IntPtr window, IntPtr insertAfter, int x, int y, int width, int height, uint flags);

    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool ShowWindow(IntPtr window, int command);

    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool UpdateWindow(IntPtr window);

    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool DestroyWindow(IntPtr window);

    [DllImport("user32.dll")]
    public static extern IntPtr DefWindowProc(IntPtr window, uint message, IntPtr wParam, IntPtr lParam);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool PeekMessage(out Message message, IntPtr window, uint minimum, uint maximum, uint remove);

    [DllImport("user32.dll")]
    private static extern bool TranslateMessage(ref Message message);

    [DllImport("user32.dll")]
    private static extern IntPtr DispatchMessage(ref Message message);

    [DllImport("kernel32.dll", CharSet = CharSet.Unicode)]
    public static extern IntPtr GetModuleHandle(string? moduleName);

    [DllImport("user32.dll", SetLastError = true)]
    public static extern IntPtr LoadCursor(IntPtr instance, IntPtr cursor);

    [StructLayout(LayoutKind.Sequential)]
    public struct NativePoint
    {
        public int X;
        public int Y;
    }

    [StructLayout(LayoutKind.Sequential, CharSet = CharSet.Unicode)]
    public struct WndClassEx
    {
        public uint Size;
        public int Style;
        public WndProc WindowProcedure;
        public int ClassExtra;
        public int WindowExtra;
        public IntPtr Instance;
        public IntPtr Icon;
        public IntPtr Cursor;
        public IntPtr Background;
        public string? MenuName;
        public string ClassName;
        public IntPtr SmallIcon;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct Message
    {
        public IntPtr Window;
        public uint MessageId;
        public IntPtr WParam;
        public IntPtr LParam;
        public uint Time;
        public NativePoint Point;
        public uint Private;
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct WndProcMessage
    {
        public IntPtr Window;
        public uint Message;
        public IntPtr WParam;
        public IntPtr LParam;
    }

    [UnmanagedFunctionPointer(CallingConvention.Winapi)]
    public delegate IntPtr WndProc(IntPtr window, uint message, IntPtr wParam, IntPtr lParam);
}
