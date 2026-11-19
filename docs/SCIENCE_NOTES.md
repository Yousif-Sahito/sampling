# Scientific conventions

A signal x(t) maps time in seconds to an amplitude. A sinusoid of frequency f
hertz completes f cycles each second; its period is 1/f seconds for f > 0.
We evaluate A sin(2πft + φ), A cos(2πft + φ), or the sum of two independent
sines. UI phase is in degrees, converted by φ = degrees × π/180. Components
with exactly zero amplitude are excluded from fmax and alias predictions.
Coincident tones are still listed individually; cancellation can make fmax a
conservative bound rather than the minimal occupied bandwidth.

The analytic function is a CT model. Its displayed curve uses 1,600 equally
spaced timestamps in [0,2), endpoint excluded. These are numerical plotting
points, not analog capture. Actual ideal samples are separately evaluated at
t_n = n/fs, for every nonnegative integer n satisfying n/fs < 2. Sample rate
fs is in samples/second; sampling period Ts = 1/fs. Integer fs gives exactly
2fs samples, including time zero but excluding time two.

## Nyquist and aliases

The signal's required Nyquist sampling rate is 2fmax. The sampling system's
Nyquist frequency is fs/2. They are different quantities. Below 2fmax unique
recovery cannot generally be guaranteed. Above it, the ideal theorem assumes
a perfectly bandlimited signal, infinite noiseless samples and ideal infinite
reconstruction. Equality is a critical boundary, never labeled safe here.
UI half-hertz frequencies and integer rates are exactly representable in binary;
strict comparison deliberately keeps nearby but unequal floating-point values
distinct in the reusable numerical API.

For a tone, f_alias = |((f + fs/2) mod fs) − fs/2|. At f=8 and fs=12,
this is |(14 mod 12) − 6| = |2 − 6| = 4 Hz. In fact the phase-zero 8 Hz
sine produces the negative of the phase-zero 4 Hz sine on these sample times;
frequency magnitude does not specify sign/phase. Many analog frequencies share
the same discrete-time equivalence class. At 18 Hz sampled at 12 Hz the folded
magnitude is 6 Hz. Multiple tones can collide and cancel or reinforce.

At f=8, fs=16, φ=0, samples are sin(πn)=0 up to floating-point roundoff.
The analytic waveform is not zero. A nonzero phase gives different boundary
samples, illustrating the degeneracy and the reason equality is unsafe.

## Reconstruction

All methods receive only sampled times/values, target times and declared
settings. They cannot read the analytic reference.

- ZOH chooses the latest sample at or before each time, holding the first or
  last sample outside the observed span.
- Linear joins neighboring samples and holds the endpoints outside the span.
- Nearest neighbor chooses the closest sample; exact midpoint ties select the
  earlier sample. Outside the sample span it holds the nearest endpoint.
- Finite sinc sums x[n] sinc(fs(t−t_n)); for t_n=n/fs this is exactly
  Σ x[n] sinc(fs t−n). NumPy sinc(u)=sin(πu)/(πu), with sinc(0)=1.
  Uniform spacing is checked; summation is chunked to bound memory.
  No nonexistent samples are inferred from the known analytic model.
- PCHIP is piecewise cubic, shape-preserving interpolation from SciPy, with
  endpoint hold outside the span. It is not ideal Shannon reconstruction.

The sinc implementation omits all contributions outside the finite record.
This causes errors, especially near the edges, even when fs > 2fmax. It can
overshoot. Perfect finite-record recovery is not promised. A single sample is
held by the interpolators, or contributes one sinc basis for sinc. Empty,
nonfinite, mismatched and non-increasing sample records are rejected clearly.
The UI's minimum fs=2 always provides four samples, so interpolation is defined.

## Errors and spectra

For errors e_i=x(t_i)−xhat(t_i) at the same dense target times:
RMSE=√mean(e_i²), MAE=mean(|e_i|), MaxAE=max(|e_i|). Interior RMSE selects
0.4 ≤ t_i ≤ 1.6 seconds, inclusively. All results have amplitude units; no
normalization divides by reference energy. Zero signals remain well-defined.
The comparison uses a fixed unit-amplitude phase-zero 8 Hz sine and the current
method, with common axes and separately measured errors; there is no universal
method/phase error-ranking claim.

The spectrum overlays known original frequencies and folded magnitudes on
sample FFT bins. Theoretical markers use nominal per-tone input amplitudes,
not predicted summed amplitudes. FFT bins use rfftfreq(N, 1/fs), |rfft(x)|/N,
doubling interior positive-frequency bins but not DC or the even-N Nyquist
bin. Odd-N final bins are doubled. The rectangular observation window causes
leakage for non-bin-centered components. Δf=fs/N=0.5 Hz here; zero padding is
not used and would not improve true resolution.

Real acquisition needs analog anti-alias filtering before the ADC if input
energy extends above fs/2. Filtering, noise, quantization, jitter and ADC
hardware are future work, not simulated in v1.
