import { FaceLandmarker, FilesetResolver } from "./vendor/tasks-vision/vision_bundle.js";

const $ = (id) => document.getElementById(id);
const ui = {
  status: $("status"),
  consent: $("consent-checkbox"),
  start: $("start-button"),
  reset: $("reset-button"),
  stop: $("stop-button"),
  stage: $("calibration-stage"),
  dot: $("calibration-dot"),
  marker: $("signal-marker"),
  title: $("stage-title"),
  message: $("stage-message"),
  backend: $("backend-value"),
  frames: $("frames-value"),
  inference: $("inference-value"),
  face: $("face-value"),
  samples: $("samples-value"),
  output: $("output-value"),
  camera: $("camera"),
};

const CALIBRATION_POINTS = [
  [0.08, 0.10], [0.50, 0.10], [0.92, 0.10],
  [0.08, 0.32], [0.50, 0.32], [0.92, 0.32],
  [0.08, 0.68], [0.50, 0.68], [0.92, 0.68],
  [0.08, 0.90], [0.50, 0.90], [0.92, 0.90],
];
const FEATURE_COUNT = 16;
const MIN_FRAME_INTERVAL_MS = 1000 / 18;

const state = {
  adapter: null,
  session: null,
  landmarker: null,
  stream: null,
  running: false,
  processing: false,
  videoFrameHandle: null,
  animationHandle: null,
  lastFrameAt: 0,
  lastTimestamp: 0,
  lastFeatures: null,
  lastEmbedding: null,
  calibrationIndex: -1,
  samples: [],
  frameCount: 0,
  inferenceCount: 0,
};

class VizzRuntimeError extends Error {
  constructor(code, message, cause = undefined) {
    super(message, { cause });
    this.code = code;
  }
}

function setStatus(message, kind = "neutral") {
  ui.status.textContent = message;
  ui.status.dataset.kind = kind;
}

function fail(error) {
  console.error(error);
  const code = error?.code || "runtime_error";
  setStatus(`${code}: ${error?.message || "fallo del runtime"}`, "error");
  ui.title.textContent = "Pipeline detenido por seguridad";
  ui.message.textContent = "No se usa fallback CPU/WASM ni se solicita cámara después de un fallo GPU.";
  ui.backend.textContent = "bloqueado";
  ui.backend.dataset.kind = "error";
  ui.dot.style.display = "none";
  ui.marker.style.display = "none";
}

function requireGpuApi() {
  if (!navigator.gpu || typeof navigator.gpu.requestAdapter !== "function") {
    throw new VizzRuntimeError("gpu_unavailable", "este navegador no expone WebGPU");
  }
}

async function initializeGpuPipeline() {
  requireGpuApi();
  setStatus("Comprobando adaptador GPU de bajo consumo…");
  const adapter = await navigator.gpu.requestAdapter({ powerPreference: "low-power" });
  if (!adapter) {
    throw new VizzRuntimeError("gpu_unavailable", "no se encontró un adaptador WebGPU");
  }
  state.adapter = adapter;

  const ort = window.ort;
  if (!ort?.InferenceSession || !ort?.Tensor) {
    throw new VizzRuntimeError("gpu_runtime_missing", "no se cargó el runtime ONNX WebGPU local");
  }
  ort.env.webgpu.powerPreference = "low-power";
  ort.env.webgpu.adapter = adapter;

  setStatus("Inicializando modelo ONNX en WebGPU…");
  state.session = await ort.InferenceSession.create("./models/tiny_gaze_encoder.onnx", {
    executionProviders: ["webgpu"],
    graphOptimizationLevel: "all",
  });

  setStatus("Inicializando Face Landmarker con delegate GPU…");
  const fileset = await FilesetResolver.forVisionTasks("./vendor/tasks-vision/wasm");
  state.landmarker = await FaceLandmarker.createFromOptions(fileset, {
    baseOptions: {
      modelAssetPath: "./models/face_landmarker.task",
      delegate: "GPU",
    },
    runningMode: "VIDEO",
    numFaces: 1,
    outputFaceBlendshapes: false,
    outputFacialTransformationMatrixes: true,
  });

  ui.backend.textContent = "WebGPU · low-power";
  ui.backend.dataset.kind = "ok";
  setStatus("GPU lista. Se puede solicitar la cámara con consentimiento.", "ok");
}

async function requestCameraAfterGpuGate() {
  if (!navigator.mediaDevices?.getUserMedia) {
    throw new VizzRuntimeError("camera_unavailable", "este navegador no expone getUserMedia");
  }
  state.stream = await navigator.mediaDevices.getUserMedia({
    audio: false,
    video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 }, frameRate: { ideal: 20, max: 24 } },
  });
  ui.camera.srcObject = state.stream;
  await ui.camera.play();
}

function pointToPixels([x, y]) {
  const rect = ui.stage.getBoundingClientRect();
  return [rect.width * x, rect.height * y];
}

function showCalibrationPoint() {
  if (state.calibrationIndex < 0 || state.calibrationIndex >= CALIBRATION_POINTS.length) {
    ui.dot.style.display = "none";
    return;
  }
  const [x, y] = pointToPixels(CALIBRATION_POINTS[state.calibrationIndex]);
  ui.dot.style.left = `${x}px`;
  ui.dot.style.top = `${y}px`;
  ui.dot.style.display = "block";
  ui.stage.focus?.({ preventScroll: true });
}

function beginCalibration() {
  state.samples = [];
  state.calibrationIndex = 0;
  ui.samples.textContent = "0";
  ui.title.textContent = `Calibración GPU · punto 1/${CALIBRATION_POINTS.length}`;
  ui.message.textContent = "Mira el punto y haz clic cuando el rostro esté visible; la muestra queda solo en memoria.";
  showCalibrationPoint();
}

function finishCalibration() {
  state.calibrationIndex = -1;
  ui.dot.style.display = "none";
  ui.title.textContent = "Pipeline GPU activo · head de gaze pendiente";
  ui.message.textContent = "La captura verificó el encoder GPU. Aún no se presenta precisión de gaze: faltan pesos entrenados y validación humana.";
  setStatus("GPU activo; calibración capturada en memoria, sin claim de precisión.", "ok");
}

function addCalibrationSample() {
  if (!state.lastFeatures || !state.lastEmbedding || state.calibrationIndex < 0) {
    setStatus("Aún no hay una señal facial válida; espera un instante.", "warn");
    return;
  }
  const target = CALIBRATION_POINTS[state.calibrationIndex];
  state.samples.push({ target, features: Array.from(state.lastFeatures), embedding: Array.from(state.lastEmbedding) });
  ui.samples.textContent = String(state.samples.length);
  state.calibrationIndex += 1;
  if (state.calibrationIndex >= CALIBRATION_POINTS.length) {
    finishCalibration();
    return;
  }
  ui.title.textContent = `Calibración GPU · punto ${state.calibrationIndex + 1}/${CALIBRATION_POINTS.length}`;
  showCalibrationPoint();
}

function point(landmarks, index) {
  const item = landmarks[index];
  return item ? [item.x, item.y, item.z || 0] : null;
}

function distance(a, b) {
  return Math.hypot(a[0] - b[0], a[1] - b[1]) || 1e-6;
}

function extractFeatures(landmarks) {
  const li = point(landmarks, 468);
  const ri = point(landmarks, 473);
  const lo = point(landmarks, 33);
  const lc = point(landmarks, 133);
  const ro = point(landmarks, 362);
  const rc = point(landmarks, 263);
  const lt = point(landmarks, 159);
  const lb = point(landmarks, 145);
  const rt = point(landmarks, 386);
  const rb = point(landmarks, 374);
  const nose = point(landmarks, 1);
  const chin = point(landmarks, 152);
  if (![li, ri, lo, lc, ro, rc, lt, lb, rt, rb, nose, chin].every(Boolean)) return null;
  const faceScale = distance(lo, rc);
  const features = new Float32Array([
    li[0], li[1], ri[0], ri[1],
    (li[0] - lo[0]) / distance(lo, lc), (li[1] - lt[1]) / distance(lt, lb),
    (ri[0] - ro[0]) / distance(ro, rc), (ri[1] - rt[1]) / distance(rt, rb),
    nose[0], nose[1], chin[0], chin[1],
    (li[0] + ri[0]) / 2, (li[1] + ri[1]) / 2,
    faceScale, Math.abs(nose[2] - chin[2]),
  ]);
  return features;
}

async function runGpuEncoder(features) {
  const ort = window.ort;
  const input = new ort.Tensor("float32", features, [1, FEATURE_COUNT]);
  const output = await state.session.run({ features: input });
  const tensor = output.embedding;
  if (!tensor?.data) throw new VizzRuntimeError("gpu_output_invalid", "el encoder no devolvió embedding");
  return tensor.data;
}

function updateSignalMarker(features) {
  const x = Math.min(0.96, Math.max(0.04, features[12]));
  const y = Math.min(0.94, Math.max(0.06, features[13]));
  const [px, py] = pointToPixels([x, y]);
  ui.marker.style.left = `${px}px`;
  ui.marker.style.top = `${py}px`;
  ui.marker.style.display = "block";
}

async function processFrame(timestamp) {
  if (state.processing || !state.landmarker || !state.session || ui.camera.readyState < 2) return;
  if (timestamp - state.lastFrameAt < MIN_FRAME_INTERVAL_MS) return;
  state.processing = true;
  state.lastFrameAt = timestamp;
  try {
    const monotonicTimestamp = Math.max(timestamp, state.lastTimestamp + 1);
    state.lastTimestamp = monotonicTimestamp;
    const result = state.landmarker.detectForVideo(ui.camera, monotonicTimestamp);
    state.frameCount += 1;
    ui.frames.textContent = String(state.frameCount);
    const landmarks = result.faceLandmarks?.[0];
    if (!landmarks) {
      ui.face.textContent = "sin señal";
      return;
    }
    ui.face.textContent = "detectado";
    const features = extractFeatures(landmarks);
    if (!features) return;
    const embedding = await runGpuEncoder(features);
    state.lastFeatures = features;
    state.lastEmbedding = embedding;
    state.inferenceCount += 1;
    ui.inference.textContent = String(state.inferenceCount);
    ui.output.textContent = `${Array.from(embedding).slice(0, 3).map((value) => value.toFixed(3)).join(", ")}…`;
    updateSignalMarker(features);
  } catch (error) {
    stopRuntime();
    fail(new VizzRuntimeError("gpu_pipeline_failed", "falló una inferencia; ejecución cerrada", error));
  } finally {
    state.processing = false;
  }
}

function scheduleFrame() {
  if (!state.running) return;
  if (typeof ui.camera.requestVideoFrameCallback === "function") {
    state.videoFrameHandle = ui.camera.requestVideoFrameCallback((now) => {
      void processFrame(now);
      scheduleFrame();
    });
  } else {
    state.animationHandle = requestAnimationFrame((now) => {
      void processFrame(now);
      scheduleFrame();
    });
  }
}

function stopRuntime() {
  state.running = false;
  if (state.videoFrameHandle !== null && typeof ui.camera.cancelVideoFrameCallback === "function") ui.camera.cancelVideoFrameCallback(state.videoFrameHandle);
  if (state.animationHandle !== null) cancelAnimationFrame(state.animationHandle);
  state.videoFrameHandle = null;
  state.animationHandle = null;
  if (state.stream) state.stream.getTracks().forEach((track) => track.stop());
  state.stream = null;
  ui.camera.pause();
  ui.camera.srcObject = null;
  state.lastFeatures = null;
  state.lastEmbedding = null;
  state.samples = [];
  ui.samples.textContent = "0";
  ui.dot.style.display = "none";
  ui.marker.style.display = "none";
  ui.stop.disabled = true;
  ui.reset.disabled = true;
  ui.start.disabled = !ui.consent.checked;
}

async function startRuntime() {
  if (!ui.consent.checked) return;
  ui.start.disabled = true;
  ui.stop.disabled = false;
  setStatus("Preparando pipeline; la cámara permanece cerrada…");
  try {
    if (!state.session || !state.landmarker) await initializeGpuPipeline();
    await requestCameraAfterGpuGate();
    state.running = true;
    ui.reset.disabled = false;
    beginCalibration();
    scheduleFrame();
  } catch (error) {
    stopRuntime();
    fail(error);
  }
}

ui.consent.addEventListener("change", () => {
  ui.start.disabled = !ui.consent.checked || state.running;
  if (!ui.consent.checked) stopRuntime();
});
ui.start.addEventListener("click", () => void startRuntime());
ui.stop.addEventListener("click", () => {
  stopRuntime();
  setStatus("Detenido. La cámara fue cerrada y las muestras se descartaron.");
  ui.title.textContent = "Pipeline GPU preparado para prueba";
  ui.message.textContent = "El modelo de gaze todavía no tiene pesos entrenados.";
});
ui.reset.addEventListener("click", () => {
  if (state.running) beginCalibration();
});
ui.dot.addEventListener("click", addCalibrationSample);
window.addEventListener("resize", showCalibrationPoint);
window.addEventListener("beforeunload", stopRuntime);
