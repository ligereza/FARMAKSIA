(() => {
  "use strict";

  const CALIBRATION_POINTS = 9;
  const MINIMUM_VALID_PREDICTIONS = 10;
  const consentCheckbox = document.querySelector("#consent-checkbox");
  const startButton = document.querySelector("#start-button");
  const recalibrateButton = document.querySelector("#recalibrate-button");
  const stopButton = document.querySelector("#stop-button");
  const status = document.querySelector("#status");
  const sampleCount = document.querySelector("#sample-count");
  const calibrationCount = document.querySelector("#calibration-count");
  const lastPosition = document.querySelector("#last-position");
  const adaptationState = document.querySelector("#adaptation-state");
  const marker = document.querySelector("#gaze-marker");
  const calibrationDots = [...document.querySelectorAll(".calibration-dot")];

  const state = {
    started: false,
    calibrated: false,
    validPredictions: 0,
    calibrationClicks: new Set(),
    lastUiUpdate: 0,
    lastPrediction: null
  };

  function setStatus(message, tone = "warn") {
    status.textContent = message;
    status.dataset.tone = tone;
  }

  function resetVolatileState() {
    state.started = false;
    state.calibrated = false;
    state.validPredictions = 0;
    state.calibrationClicks.clear();
    state.lastUiUpdate = 0;
    state.lastPrediction = null;
    sampleCount.textContent = "0";
    calibrationCount.textContent = "0 / 9";
    lastPosition.textContent = "—";
    adaptationState.textContent = "bloqueada";
    marker.style.display = "none";
    calibrationDots.forEach((dot) => dot.classList.remove("visited"));
  }

  function updateControls() {
    startButton.disabled = !consentCheckbox.checked || state.started;
    recalibrateButton.disabled = !state.started;
  }

  function onGaze(data, elapsedTime) {
    if (!data || !Number.isFinite(data.x) || !Number.isFinite(data.y)) return;
    state.validPredictions += 1;
    state.lastPrediction = { x: data.x, y: data.y, elapsedTime };
    sampleCount.textContent = String(state.validPredictions);
    const now = performance.now();
    if (now - state.lastUiUpdate < 50) return;
    state.lastUiUpdate = now;
    lastPosition.textContent = `${Math.round(data.x)}, ${Math.round(data.y)}`;
    if (state.calibrated && state.validPredictions >= MINIMUM_VALID_PREDICTIONS) {
      adaptationState.textContent = "marcador activo";
      marker.style.left = `${data.x}px`;
      marker.style.top = `${data.y}px`;
      marker.style.display = "block";
    }
  }

  function configureWebGazer() {
    if (!window.webgazer) throw new Error("WebGazer.js local no está disponible");
    window.saveDataAcrossSessions = false;
    return window.webgazer
      .saveDataAcrossSessions(false)
      .setRegression("ridge")
      .showVideoPreview(false)
      .showFaceOverlay(false)
      .showFaceFeedbackBox(false)
      .showPredictionPoints(false)
      .applyKalmanFilter(true)
      .setGazeListener(onGaze);
  }

  async function startTracking() {
    if (!consentCheckbox.checked) {
      setStatus("El consentimiento explícito es obligatorio antes de solicitar la cámara.", "error");
      return;
    }
    if (window.location.protocol === "file:") {
      setStatus("Sirve la carpeta desde localhost o HTTPS; el protocolo file: no es un contexto válido para webcam.", "error");
      return;
    }
    try {
      const webgazer = configureWebGazer();
      setStatus("Solicitando permiso de cámara… no comienza el seguimiento hasta que el navegador lo autorice.", "warn");
      const beginResult = webgazer.begin();
      if (beginResult && typeof beginResult.then === "function") await beginResult;
      if (typeof webgazer.removeMouseEventListeners === "function") webgazer.removeMouseEventListeners();
      state.started = true;
      updateControls();
      setStatus("Seguimiento activo en memoria. Completa los nueve puntos de calibración.", "ok");
    } catch (error) {
      await stopTracking();
      setStatus(`No se pudo iniciar el seguimiento: ${error.message || "permiso o dispositivo no disponible"}`, "error");
    }
  }

  async function clearCalibration() {
    if (!state.started || !window.webgazer) return;
    state.calibrated = false;
    state.calibrationClicks.clear();
    calibrationDots.forEach((dot) => dot.classList.remove("visited"));
    adaptationState.textContent = "bloqueada";
    marker.style.display = "none";
    await window.webgazer.clearData();
    calibrationCount.textContent = "0 / 9";
    setStatus("Modelo borrado. Repite los nueve puntos mirando y pulsando cada objetivo.", "warn");
  }

  async function stopTracking() {
    const webgazer = window.webgazer;
    if (webgazer) {
      try { webgazer.clearGazeListener(); } catch (_) { /* cleanup is best effort */ }
      try { if (typeof webgazer.pause === "function") await webgazer.pause(); } catch (_) { /* cleanup is best effort */ }
      try { if (typeof webgazer.stopVideo === "function") webgazer.stopVideo(); } catch (_) { /* video may already be detached */ }
      try { if (typeof webgazer.end === "function") webgazer.end(); } catch (_) { /* cleanup is best effort */ }
      try { if (typeof webgazer.clearData === "function") await webgazer.clearData(); } catch (_) { /* local model cleanup is best effort */ }
    }
    resetVolatileState();
    updateControls();
    setStatus("Cámara apagada. Estado volátil y calibración limpiados.", "warn");
  }

  calibrationDots.forEach((dot) => {
    dot.addEventListener("click", (event) => {
      event.preventDefault();
      if (!state.started || !window.webgazer) {
        setStatus("Inicia el seguimiento y concede permiso antes de calibrar.", "error");
        return;
      }
      const box = dot.getBoundingClientRect();
      window.webgazer.recordScreenPosition(box.left + box.width / 2, box.top + box.height / 2, "click");
      state.calibrationClicks.add(dot.dataset.point);
      dot.classList.add("visited");
      calibrationCount.textContent = `${state.calibrationClicks.size} / ${CALIBRATION_POINTS}`;
      if (state.calibrationClicks.size === CALIBRATION_POINTS) {
        state.calibrated = true;
        setStatus("Calibración declarada completa. El marcador solo se activa al recibir diez predicciones válidas.", "ok");
      }
    });
  });

  consentCheckbox.addEventListener("change", () => {
    updateControls();
    if (!consentCheckbox.checked && !state.started) setStatus("Cámara apagada. El consentimiento sigue sin concederse.", "warn");
  });
  startButton.addEventListener("click", startTracking);
  recalibrateButton.addEventListener("click", clearCalibration);
  stopButton.addEventListener("click", stopTracking);
  window.addEventListener("pagehide", () => {
    const webgazer = window.webgazer;
    if (!webgazer || !state.started) return;
    try { webgazer.clearGazeListener(); } catch (_) { /* page is closing */ }
    try { if (typeof webgazer.stopVideo === "function") webgazer.stopVideo(); } catch (_) { /* page is closing */ }
    try { if (typeof webgazer.end === "function") webgazer.end(); } catch (_) { /* page is closing */ }
    try { if (typeof webgazer.clearData === "function") void webgazer.clearData(); } catch (_) { /* page is closing */ }
  });

  resetVolatileState();
  updateControls();
})();
