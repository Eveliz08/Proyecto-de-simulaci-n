import numpy as np
import matplotlib.pyplot as plt
from collections import deque
import pandas as pd
from scipy import stats

class InventorySimulation:
    def __init__(self, r, lambda_, G, s, S, c, L, h, T):
        """
        Inicializa la simulación de inventario con política (s, S)
        
        Parámetros:
        r: precio unitario de venta
        lambda_: tasa de llegada de clientes (Poisson)
        G: función que genera demanda aleatoria de clientes
        s: nivel mínimo para reordenar
        S: nivel objetivo de inventario
        c: función de costo de pedido
        L: tiempo de entrega de pedido
        h: costo de mantenimiento por unidad por unidad de tiempo
        T: tiempo total de simulación
        """
        self.r = r
        self.lambda_ = lambda_
        self.G = G
        self.s = s
        self.S = S
        self.c = c
        self.L = L
        self.h = h
        self.T = T
        
        # Variables de estado
        self.reset_simulation()
    
    def reset_simulation(self):
        """Reinicia la simulación al estado inicial"""
        self.t = 0.0  # tiempo actual
        self.x = self.S  # inventario inicial (comenzamos con inventario lleno)
        self.y = 0  # cantidad pedida actualmente
        
        # Variables de conteo
        self.C = 0.0  # costo total de pedidos
        self.H = 0.0  # costo total de mantenimiento
        self.R = 0.0  # ingresos totales
        
        # Próximos eventos
        self.t0 = self.generate_next_customer()  # próximo cliente
        self.t1 = float('inf')  # próximo pedido (infinito si no hay pedido pendiente)
        
        # Historial para análisis
        self.inventory_history = [self.x]
        self.time_history = [self.t]
        self.events_history = []
    
    def generate_next_customer(self):
        """Genera el tiempo de llegada del próximo cliente usando proceso Poisson"""
        U = np.random.uniform()
        return self.t - (1/self.lambda_) * np.log(U)
    
    def run_simulation(self):
        """Ejecuta la simulación hasta el tiempo T"""
        while self.t <= self.T:
            # Determinar el próximo evento
            if self.t0 < self.t1:
                self.process_customer_arrival()
            else:
                self.process_order_arrival()
            
            # Registrar historial
            self.inventory_history.append(self.x)
            self.time_history.append(self.t)
        
        # Calcular ganancia promedio
        avg_profit = (self.R - self.C - self.H) / self.T
        return avg_profit
    
    def process_customer_arrival(self):
        """Procesa la llegada de un cliente"""
        # Actualizar costo de mantenimiento
        delta_t = self.t0 - self.t
        self.H += delta_t * self.x * self.h
        
        # Avanzar tiempo
        self.t = self.t0
        
        # Generar demanda del cliente
        D = self.G()
        w = min(D, self.x)  # cantidad vendida
        
        # Actualizar inventario e ingresos
        self.R += w * self.r
        self.x -= w
        
        # Verificar si necesitamos hacer un pedido
        if self.x < self.s and self.y == 0:
            self.y = self.S - self.x
            self.t1 = self.t + self.L
        
        # Programar próximo cliente
        self.t0 = self.generate_next_customer()
        
        # Registrar evento
        self.events_history.append((self.t, 'Customer', D, w))
    
    def process_order_arrival(self):
        """Procesa la llegada de un pedido"""
        # Actualizar costo de mantenimiento
        delta_t = self.t1 - self.t
        self.H += delta_t * self.x * self.h
        
        # Avanzar tiempo
        self.t = self.t1
        
        # Procesar pedido
        self.C += self.c(self.y)
        self.x += self.y
        self.y = 0
        self.t1 = float('inf')
        
        # Registrar evento
        self.events_history.append((self.t, 'Order', self.y))
    
    def plot_inventory(self, nombre):
        """Grafica el nivel de inventario a lo largo del tiempo"""
        plt.figure(figsize=(12, 6))
        plt.step(self.time_history, self.inventory_history, where='post')
        plt.axhline(y=self.s, color='r', linestyle='--', label=f'Nivel de reorden (s={self.s})')
        plt.axhline(y=self.S, color='g', linestyle='--', label=f'Nivel objetivo (S={self.S})')
        
        # Marcar eventos importantes
        for event in self.events_history:
            time, typ, *details = event
            if typ == 'Customer':
                plt.scatter(time, self.inventory_history[self.time_history.index(time)], color='orange', zorder=5)
            elif typ == 'Order':
                plt.scatter(time, self.inventory_history[self.time_history.index(time)], color='blue', zorder=5)
        
        plt.title('Nivel de Inventario a lo largo del tiempo')
        plt.xlabel('Tiempo')
        plt.ylabel('Unidades en inventario')
        plt.legend()
        plt.grid(True)
        plt.savefig("./img/" + nombre + ".jpg")

# Ejemplo de uso
if __name__ == "__main__":
    # Parámetros de la simulación
    r = 10.0  # precio unitario
    lambda_ = 0.5  # tasa de llegada de clientes (por unidad de tiempo)
    
    # Función de demanda de clientes (distribución Poisson con media 3)
    def demand_generator():
        return np.random.poisson(3)
    
    s = 10  # nivel mínimo para reordenar
    S = 30  # nivel objetivo
    
    # Función de costo de pedido (costo fijo + costo variable)
    def cost_function(y):
        return 50 + 2 * y  # $50 fijos + $2 por unidad
    
    L = 2.0  # tiempo de entrega
    h = 0.5  # costo de mantenimiento por unidad por unidad de tiempo
    T = 100.0  # tiempo total de simulación
    
    
    
    # avg_profit = sim.run_simulation()
    ganancia = []  #Ganancia promedio por unidad de tiempo
    ingresos = []  #Total ingresos
    pedidos = []  #Total costos de pedidos
    mantenimiento = [] #Total costos de mantenimiento
    
    for i in range(30):
        # Crear y ejecutar simulación
        sim = InventorySimulation(r, lambda_, demand_generator, s, S, cost_function, L, h, T)
    
        avg_profit = sim.run_simulation()
        ganancia.append(avg_profit)
        # Graficar el inventario de algunas simulaciones
        if i< 4:
            sim.plot_inventory("sim"+ str(i))
    
    print(ganancia)
    
    
    # Análisis estadístico de los datos en el array ganancia
    ganancia = np.array(ganancia)  # Convertir a un array de NumPy para facilitar cálculos

    # Cálculo de estadísticos
    media = np.mean(ganancia)
    mediana = np.median(ganancia)
    desviacion_estandar = np.std(ganancia)
    varianza = np.var(ganancia)
    minimo = np.min(ganancia)
    maximo = np.max(ganancia)
    
    
    # Crear una tabla con los resultados
    tabla_estadisticos = pd.DataFrame({
        "Estadístico": ["Media", "Mediana", "Desviación Estándar", "Varianza", "Mínimo", "Máximo"],
        "Valor": [media, mediana, desviacion_estandar, varianza, minimo, maximo]
    })

    # Mostrar la tabla
    print(tabla_estadisticos)

    # Generar un histograma
    plt.figure(figsize=(10, 6))
    plt.hist(ganancia, bins=10, color='skyblue', edgecolor='black', alpha=0.7)
    plt.title("Histograma de Ganancia Promedio")
    plt.xlabel("Ganancia Promedio")
    plt.ylabel("Frecuencia")
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig("./img/histograma.jpg")   
    