import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt

# Given filter parameters
C = 100e-15
L = 0.0101
R = 1000
fs = 62.5e6

# Calculate resonant frequency
f0 = 1 / (2 * np.pi * np.sqrt(L * C))
print(f"Resonant frequency f0: {f0} Hz")

# Calculate intermediate value p
p = 2 * np.pi * f0 / np.tan(np.pi * f0 / fs)
print(f"Intermediate value p: {p}")

# Calculate the filter coefficients
b2 = 1
b1 = 2
b0 = 1
a2 = L * C * p**2 + R * C * p + 1
a1 = 2 * (1 - L * C * p**2)
a0 = L * C * p**2 - R * C * p + 1

b2 = b2 / a0
b1 = b1 / a0
b0 = b0 / a0
a2 = a2 / a0
a1 = a1 / a0
a0 = a0 / a0

print(f"Calculated coefficients:")
print(f"a0: {a0}")
print(f"a1: {a1}")
print(f"a2: {a2}")
print(f"b0: {b0}")
print(f"b1: {b1}")
print(f"b2: {b2}")

# Quantization parameters
FRAC = 20  # Fractional bits
scale = 2 ** FRAC

# Quantize the coefficients by scaling and rounding
def quantize_coefficients(a0, a1, a2, b0, b1, b2, scale):
    a0_quant = round(a0 * scale)
    a1_quant = round(a1 * scale)
    a2_quant = round(a2 * scale)
    b0_quant = round(b0 * scale)
    b1_quant = round(b1 * scale)
    b2_quant = round(b2 * scale)
    return a0_quant, a1_quant, a2_quant, b0_quant, b1_quant, b2_quant

a0_quant, a1_quant, a2_quant, b0_quant, b1_quant, b2_quant = quantize_coefficients(a0, a1, a2, b0, b1, b2, scale)

print(f"Quantized coefficients (integer values):")
print(f"a0_quant: {a0_quant}")
print(f"a1_quant: {a1_quant}")
print(f"a2_quant: {a2_quant}")
print(f"b0_quant: {b0_quant}")
print(f"b1_quant: {b1_quant}")
print(f"b2_quant: {b2_quant}")

# Convert quantized coefficients back to float for further calculations
a0_quant_float = a0_quant / scale
a1_quant_float = a1_quant / scale
a2_quant_float = a2_quant / scale
b0_quant_float = b0_quant / scale
b1_quant_float = b1_quant / scale
b2_quant_float = b2_quant / scale

print(f"Quantized coefficients (float values):")
print(f"a0_quant_float: {a0_quant_float}")
print(f"a1_quant_float: {a1_quant_float}")
print(f"a2_quant_float: {a2_quant_float}")
print(f"b0_quant_float: {b0_quant_float}")
print(f"b1_quant_float: {b1_quant_float}")
print(f"b2_quant_float: {b2_quant_float}")

# Use the quantized float coefficients to calculate zeros, poles, and gain
b = [b0_quant_float, b1_quant_float, b2_quant_float]
a = [a0_quant_float, a1_quant_float, a2_quant_float]

# Calculate zeros, poles, and gain
zeros, poles, gain = signal.tf2zpk(b, a)

# Print the results
print("\nZeros:")
for zero in zeros:
    print(f"Real: {zero.real}, Imaginary: {zero.imag}")

print("\nPoles:")
for pole in poles:
    print(f"Real: {pole.real}, Imaginary: {pole.imag}")

print(f"\nGain: {gain}")

# Calculate magnitudes of the poles
magnitudes = np.abs(poles)
print("\nPole Magnitudes:")
for i, mag in enumerate(magnitudes):
    print(f"Pole {i + 1} Magnitude: {mag}")

# Function to proportionally scale the poles to ensure stability
def stabilize_poles_proportionally(poles):
    max_magnitude = max(np.abs(poles))
    if max_magnitude >= 1:
        scaling_factor = 0.9999 / max_magnitude
        stabilized_poles = poles * scaling_factor
    else:
        stabilized_poles = poles
    return stabilized_poles

# Stabilize the poles proportionally
stabilized_poles = stabilize_poles_proportionally(poles)

# Convert stabilized poles back to filter coefficients
a_stabilized = signal.zpk2tf(zeros, stabilized_poles, gain)[1]

print("\nStabilized poles (proportional):")
for pole in stabilized_poles:
    print(f"Real: {pole.real}, Imaginary: {pole.imag}")

# Print the new coefficients
print("\nNew denominator coefficients (a) after proportional stabilization:")
for i, coeff in enumerate(a_stabilized):
    print(f"a{i}: {coeff}")

# Plot the transfer function with higher resolution
w_original, h_original = signal.freqz(b, a, fs=fs, worN=4096*64)
w_stabilized, h_stabilized = signal.freqz(b, a_stabilized, fs=fs, worN=4096*64)
plt.figure()
plt.plot(w_original, 20 * np.log10(abs(h_original)), 'b', label='Original')
plt.plot(w_stabilized, 20 * np.log10(abs(h_stabilized)), 'r', label='Stabilized')
plt.title('Digital filter frequency response')
plt.xlabel('Frequency [Hz]')
plt.ylabel('Amplitude [dB]')
plt.legend()
plt.grid()
plt.show()

# Calculate the resonant frequency of the stabilized poles
def calculate_resonant_frequency(poles, fs):
    resonant_frequencies = []
    for pole in poles:
        angle = np.angle(pole)
        frequency = angle * fs / (2 * np.pi)
        resonant_frequencies.append(frequency)
    return resonant_frequencies

resonant_frequencies = calculate_resonant_frequency(stabilized_poles, fs)
print("\nResonant Frequencies of Stabilized Poles:")
for i, freq in enumerate(resonant_frequencies):
    print(f"Pole {i + 1} Resonant Frequency: {freq} Hz")

# Calculate the new magnitudes of the stabilized poles
new_magnitudes = np.abs(stabilized_poles)
print("\nNew Pole Magnitudes after Stabilization:")
for i, mag in enumerate(new_magnitudes):
    print(f"Pole {i + 1} Magnitude: {mag}")

# Scale the new a0, a1, a2 coefficients to the integer (2**FRAC)
a0_stabilized_quant, a1_stabilized_quant, a2_stabilized_quant, _, _, _ = quantize_coefficients(
    a_stabilized[0], a_stabilized[1], a_stabilized[2], b0, b1, b2, scale)

print("\nNew Quantized Denominator Coefficients after Stabilization:")
print(f"a0_stabilized_quant: {a0_stabilized_quant}")
print(f"a1_stabilized_quant: {a1_stabilized_quant}")
print(f"a2_stabilized_quant: {a2_stabilized_quant}")
print(f"b0_quant: {b0_quant}")
print(f"b1_quant: {b1_quant}")
print(f"b2_quant: {b2_quant}")
