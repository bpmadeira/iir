import numpy as np
import matplotlib.pyplot as plt
import time
from scipy import signal

### This script makes the following assumptions:
### a0, a1, a2 are the IIR part of the filter
### b0, b1, b2 are the FIR part of the filter

# Given filter coefficients
C = 0.5e-13
L = 20e-3
R = 500
fs = 62.5e6
f0 = 1 / (2 * np.pi * np.sqrt(L * C))
p = 2 * np.pi * f0 / np.tan(np.pi * f0 / fs)
b2 = 1
b1 = 2
b0 = 1
a2 = L * C * p**2 + R * C * p + 1
a1 = 2 * (1 - L * C * p**2)
a0 = L * C * p**2 - R * C * p + 1

# b2 = 0.262
# b1 = -0.476
# b0 = 0.262
# a2 = 0
# a1 = 0
# a0 = 1

# Normalized

N = 30
F = 30

b2n = b2/a0
b1n = b1/a0
b0n = b0/a0
a1n = a1/a0
a2n = a2/a0
a0n = a0/a0

# Scaled coefficients
a0_16b = round(a0n * 2**N)
a1_16b = round(a1n * 2**N)
a2_16b = round(a2n * 2**N)
b0_16b = round(b0n * 2**F)
b1_16b = round(b1n * 2**F)
b2_16b = round(b2n * 2**F)

# Scaled coefficients
q_a0_16b = round(a0_16b/2**F,7)
q_a1_16b = round(a1_16b/2**F,7)
q_a2_16b = round(a2_16b/2**F,7)
q_b0_16b = round(b0_16b/2**F,7)
q_b1_16b = round(b1_16b/2**F,7)
q_b2_16b = round(b2_16b/2**F,7)

e_a0_16b = a0n - round(a0_16b/2**F,7)
e_a1_16b = a1n - round(a1_16b/2**F,7)
e_a2_16b = a2n - round(a2_16b/2**F,7)
e_b0_16b = b0n - round(b0_16b/2**F,7)
e_b1_16b = b1n - round(b1_16b/2**F,7)
e_b2_16b = b2n - round(b2_16b/2**F,7)

# Calculating zeros and poles
zeros = np.roots([b2_16b, b1_16b, b0_16b])
poles = np.roots([a2_16b, a1_16b, a0_16b])

qzeros = np.roots([q_b2_16b, q_b1_16b, q_b0_16b])
qpoles = np.roots([q_a2_16b, q_a1_16b, q_a0_16b])

# Plotting the poles, zeros, and unit circle
plt.figure(1)
plt.figure(figsize=(8, 8))
plt.plot(np.real(zeros), np.imag(zeros), 'o', label='Zeros')
plt.plot(np.real(poles), np.imag(poles), 'x', label='Poles')
plt.plot(np.real(qzeros), np.imag(qzeros), '8', label='Quantized Zeros')
plt.plot(np.real(qpoles), np.imag(qpoles), 'P', label='Quantized Poles')

# Creating a unit circle for reference
theta = np.linspace(0, 2 * np.pi, 1000)
plt.plot(np.cos(theta), np.sin(theta), label='Unit Circle')

plt.xlabel('Real Part')
plt.ylabel('Imaginary Part')
plt.title('Poles, Zeros, and Unit Circle of the IIR Filter')
plt.axhline(0, color='black', lw=1)
plt.axvline(0, color='black', lw=1)
plt.grid(True)
plt.legend()


print( "Normalized: \n"
      "a0: ",a0n, "\n"
      "a1: ",a1n, "\n"
      "a2: ",a2n, "\n"
      "b0: ",b0n, "\n"
      "b1: ",b1n, "\n"
      "b2: ",b2n, "\n")

print( "Fixed-Point: \n"
      "a0: ",a0_16b, "\n"
      "a1: ",a1_16b, "\n"
      "a2: ",a2_16b, "\n"
      "b0: ",b0_16b, "\n"
      "b1: ",b1_16b, "\n"
      "b2: ",b2_16b, "\n")

print( "Quantized: \n"
      "a0: ",q_a0_16b, "\n"
      "a1: ",q_a1_16b, "\n"
      "a2: ",q_a2_16b, "\n"
      "b0: ",q_b0_16b, "\n"
      "b1: ",q_b1_16b, "\n"
      "b2: ",q_b2_16b, "\n")

print( "Quantization Error: \n"
      "a0: ",e_a0_16b, "\n"
      "a1: ",e_a1_16b, "\n"
      "a2: ",e_a2_16b, "\n"
      "b0: ",e_b0_16b, "\n"
      "b1: ",e_b1_16b, "\n"
      "b2: ",e_b2_16b, "\n")


# Calculate frequency response
w, h = signal.freqz([b2_16b, b1_16b, b0_16b], [a2_16b, a1_16b, a0_16b])
w2, h2 = signal.freqz([q_b2_16b, q_b1_16b, q_b0_16b], [q_a2_16b, q_a1_16b, q_a0_16b])
frequencies = w * fs/ (2 * np.pi)

bin1 = "01110000000000000111000000000000011100000000000001110000000000000111000000000000011100000000000001110000000000000111000000000000"
dec = int(bin1,2)
print(dec)

# Plot
plt.figure(2)
plt.figure(figsize=(8, 8))
plt.plot(frequencies, 20 * np.log10(abs(h)))
plt.plot(frequencies, 20 * np.log10(abs(h2)))
plt.title('Frequency Response')
plt.xlabel('Normalized Frequency (x π rad/sample)')
plt.ylabel('Amplitude (dB)')
plt.grid()
plt.show()

