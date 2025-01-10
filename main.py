import numpy as np
from scipy.integrate import odeint
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import os

class TunedMassDamperAnalysis:
    def __init__(self, m1=1.0, m2=0.05, k1=1.0, b=0.1):
        #initialize with default parameters matching the case 
        self.m1 = m1  # Building mass
        self.m2 = m2  # Damper mass
        self.k1 = k1  # Building spring constant
        self.b = b    # Damping coefficient

    def system_equations(self, state, t, k2):
        #system of first-order differential eq.
        x1, x2, p1, p2 = state

        dx1dt = p1 / self.m1
        dx2dt = p2 / self.m2
        dp1dt = -self.k1 * x1 + k2 * (x2 - x1) + self.b * (p2 / self.m2 - p1 / self.m1)
        dp2dt = -k2 * (x2 - x1) - self.b * (p2 / self.m2 - p1 / self.m1)

        return [dx1dt, dx2dt, dp1dt, dp2dt]

    def calculate_energy(self, state, k2):
        x1, x2, p1, p2 = state

        T1 = p1 ** 2 / (2 * self.m1)
        T2 = p2 ** 2 / (2 * self.m2)
        V1 = 0.5 * self.k1 * x1 ** 2
        V2 = 0.5 * k2 * (x2 - x1) ** 2

        return T1 + T2, V1 + V2, T1 + T2 + V1 + V2

    def simulate(self, k2, t_span, initial_conditions):
        #simulate system dynamics
        solution = odeint(self.system_equations, initial_conditions, t_span, args=(k2,))
        energies = np.array([self.calculate_energy(state, k2) for state in solution])
        return solution, energies

    def save_plot(self, save_path, filename):
        if save_path:
            os.makedirs(save_path, exist_ok=True)
            plt.savefig(os.path.join(save_path, filename))

    def generate_all_plots(self, save_path=None):
        print("Generating analysis plots...")
        
        # Simulation parameters
        t = np.linspace(0, 200, 2000)
        initial_conditions = [10, 0, 0, 0]
        k2_optimal = 0.05

        # Run simulation
        print("Running simulation...")
        solution, energies = self.simulate(k2_optimal, t, initial_conditions)

        # 1. Motion Plot
        print("Generating motion plot...")
        plt.figure(figsize=(12, 6))
        plt.plot(t, solution[:, 0], 'b-', label='Building Position (x₁)')
        plt.plot(t, solution[:, 1], 'r--', label='Damper Position (x₂)')
        plt.xlabel('Time (s)')
        plt.ylabel('Position')
        plt.title('Building and Damper Motion')
        plt.grid(True)
        plt.legend()
        self.save_plot(save_path, 'motion_plot.png')
        plt.show()

        # 2. Energy Plot
        print("Generating energy plot...")
        plt.figure(figsize=(12, 6))
        plt.plot(t, energies[:, 0], 'b-', label='Kinetic Energy')
        plt.plot(t, energies[:, 1], 'r--', label='Potential Energy')
        plt.plot(t, energies[:, 2], 'g-', label='Total Energy')
        plt.xlabel('Time (s)')
        plt.ylabel('Energy')
        plt.title('System Energy Components')
        plt.grid(True)
        plt.legend()
        self.save_plot(save_path, 'energy_plot.png')
        plt.show()

        # 3. Phase Space Plot
        print("Generating phase space plot...")
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        ax.plot(solution[:, 0], solution[:, 1], solution[:, 2], 'b-')
        ax.set_xlabel('Building Position (x₁)')
        ax.set_ylabel('Damper Position (x₂)')
        ax.set_zlabel('Building Momentum (p₁)')
        ax.set_title('System Phase Space Trajectory')
        self.save_plot(save_path, 'phase_space.png')
        plt.show()

        # 4. Parameter Optimization Plot
        print("Generating optimization plot...")
        k2_range = np.linspace(0.01, 0.1, 20)
        settling_times = []
        
        for k2 in k2_range:
            sol, _ = self.simulate(k2, t, initial_conditions)
            mask = np.abs(sol[:, 0]) > 2.5
            settling_times.append(t[mask][-1] if np.any(mask) else 0)

        plt.figure(figsize=(10, 6))
        plt.plot(k2_range, settling_times, 'b-', linewidth=2)
        plt.xlabel('Spring Constant (k₂)')
        plt.ylabel('Settling Time (s)')
        plt.title('Optimization of Spring Constant k₂')
        plt.grid(True)
        self.save_plot(save_path, 'optimization_plot.png')
        plt.show()

        print("Analysis complete! All plots have been generated and saved.")

if __name__ == "__main__":
    # Create analysis instance
    analysis = TunedMassDamperAnalysis()
    
    # Generate all plots with progress messages
    analysis.generate_all_plots(save_path="./figures")
