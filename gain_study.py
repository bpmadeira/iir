import numpy as np
import scipy.signal as signal
import matplotlib.pyplot as plt

# Given filter parameters
C = 45.873e-15
L = 0.022102
fs = 62.5e6
R_values = [1, 10, 100, 1000, 10000, 1000000]

# Quantization parameters
FRAC = 20  # Fractional bits
scale = 2 ** FRAC

# Function to calculate filter coefficients and gain
def calculate_coefficients_and_gain(R):
    f0 = 1 / (2 * np.pi * np.sqrt(L * C))
    p = 2 * np.pi * f0 / np.tan(np.pi * f0 / fs)
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
    return a0, a1, a2, b0, b1, b2

# Function to quantize coefficients
def quantize_coefficients(a0, a1, a2, b0, b1, b2, scale):
    a0_quant = round(a0 * scale)
    a1_quant = round(a1 * scale)
    a2_quant = round(a2 * scale)
    b0_quant = round(b0 * scale)
    b1_quant = round(b1 * scale)
    b2_quant = round(b2 * scale)
    return a0_quant, a1_quant, a2_quant, b0_quant, b1_quant, b2_quant

# Function to proportionally scale the poles to ensure stability
def stabilize_poles_proportionally(poles):
    max_magnitude = max(np.abs(poles))
    if max_magnitude >= 1:
        scaling_factor = 0.9999 / max_magnitude
        stabilized_poles = poles * scaling_factor
    else:
        stabilized_poles = poles
    return stabilized_poles

# Store results for plotting
results = []

# Iterate over R values and calculate coefficients and gain
for R in R_values:
    a0, a1, a2, b0, b1, b2 = calculate_coefficients_and_gain(R)
    a0_quant, a1_quant, a2_quant, b0_quant, b1_quant, b2_quant = quantize_coefficients(a0, a1, a2, b0, b1, b2, scale)
    a0_quant_float = a0_quant / scale
    a1_quant_float = a1_quant / scale
    a2_quant_float = a2_quant / scale
    b0_quant_float = b0_quant / scale
    b1_quant_float = b1_quant / scale
    b2_quant_float = b2_quant / scale
    
    b = [b0_quant_float, b1_quant_float, b2_quant_float]
    a = [a0_quant_float, a1_quant_float, a2_quant_float]
    w, h = signal.freqz(b, a, fs=fs, worN=4096*64) #h : amplitude, w : frequency
    peak_amplitude = np.max(20 * np.log10(np.abs(h)))
    results.append({
        'R': R,
        'a0': a0_quant_float,
        'a1': a1_quant_float,
        'a2': a2_quant_float,
        'b0': b0_quant_float,
        'b1': b1_quant_float,
        'b2': b2_quant_float,
        'gain': peak_amplitude
    })
    
    for result in results:
        print(f"\nR = {result['R']}")
        print(f"a0: {result['a0']}")
        print(f"a1: {result['a1']}")
        print(f"a2: {result['a2']}")
        print(f"b0: {result['b0']}")
        print(f"b1: {result['b1']}")
        print(f"b2: {result['b2']}")
        print(f"Gain: {result['gain']}")
    #Plot for different R values
    plt.plot(w, 20 * np.log10(np.abs(h)), label=f'R={R}') 

# Plot frequency responses
plt.title('Digital filter frequency response for different R values')
plt.xlabel('Frequency [Hz]')
plt.ylabel('Amplitude [dB]')
plt.legend()
plt.grid()
plt.show()

# Calculate differences in coefficients and gains
R_values_diff = R_values[1:]
a1_diff = [results[1]['a1'] - results[i]['a1'] for i in range(1, len(results))]
a2_diff = [results[1]['a2'] - results[i]['a2'] for i in range(1, len(results))]
b0_diff = [results[1]['b0'] - results[i]['b0'] for i in range(1, len(results))]
b1_diff = [results[1]['b1'] - results[i]['b1'] for i in range(1, len(results))]
b2_diff = [results[1]['b2'] - results[i]['b2'] for i in range(1, len(results))]

gains = [result['gain'] for result in results]

# Plot peak amplitude vs R
plt.figure()
plt.plot(R_values, gains, marker='o')
plt.title('Peak Amplitude vs R')
plt.xlabel('R')
plt.ylabel('Peak Amplitude [dB]')
plt.grid()
plt.xscale('log')
plt.show()

# Plot coefficient differences vs R
plt.figure()
plt.plot(R_values_diff, a1_diff, marker='o', label='a1 difference')
plt.plot(R_values_diff, a2_diff, marker='o', label='a2 difference')
plt.plot(R_values_diff, b0_diff, marker='*', label='b0 difference')
plt.plot(R_values_diff, b1_diff, marker='*', label='b1 difference')
plt.plot(R_values_diff, b2_diff, marker='*', label='b2 difference')
plt.title('Coefficient Differences vs R')
plt.xlabel('R')
plt.ylabel('Coefficient Difference')
plt.grid()
plt.xscale('log')
plt.legend()
plt.show()

# Use the quantized float coefficients to calculate zeros, poles, and gain
b = [0.06180858612060547, 0.12361717224121094, 0.06180858612060547]
a = [1.0, -1.7528352737426758 , 1.0000696182250977]

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
        scaling_factor = 0.9999/ max_magnitude
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


