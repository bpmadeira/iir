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

# Function to proportionally scale the poles to ensure stability
def stabilize_poles_proportionally(poles, pulling_factor=0.9999):
    max_magnitude = max(np.abs(poles))
    if max_magnitude >= 1:
        scaling_factor = pulling_factor / max_magnitude
        stabilized_poles = poles * scaling_factor
    else:
        stabilized_poles = poles
    return stabilized_poles

# Function to calculate Q factor based on bandwidth
def calculate_q_factor_bandwidth(b, a, fs):
    w, h = signal.freqz(b, a, worN=6250000, fs=fs)
    h_db = 20 * np.log10(abs(h))

    # Find the peak of the frequency response
    peak_index = np.argmax(h_db)
    peak_freq = w[peak_index]
    peak_value = h_db[peak_index]

    # Find -3dB points
    left_3db_index = np.where(h_db[:peak_index] <= peak_value - 3)[0][-1]
    right_3db_index = np.where(h_db[peak_index:] <= peak_value - 3)[0][0] + peak_index

    left_3db_freq = w[left_3db_index]
    right_3db_freq = w[right_3db_index]

    bandwidth = right_3db_freq - left_3db_freq
    q_factor = peak_freq / bandwidth

    return q_factor

# Vary pulling factor and calculate Q factor
pulling_factors = np.linspace(0.99999 , 0.99999999, 100)
q_factors_list = []

for pf in pulling_factors:
    stabilized_poles = stabilize_poles_proportionally(poles, pf)
    a_stabilized = signal.zpk2tf(zeros, stabilized_poles, gain)[1]
    q_factor = calculate_q_factor_bandwidth(b, a_stabilized, fs)
    q_factors_list.append(q_factor)

# Plot Q factors versus pulling factors
plt.figure()
plt.plot(pulling_factors, q_factors_list, label='Q Factor')

plt.xlabel('Pulling Factor')
plt.ylabel('Q Factor')
plt.title('Q Factor vs Pulling Factor')
plt.legend()
plt.grid()
plt.show()
