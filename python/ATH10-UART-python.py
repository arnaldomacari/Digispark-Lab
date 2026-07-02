import serial
import time
import csv
from datetime import datetime
from collections import deque
import os

# Configurações
PORTA = '/dev/ttyACM0'
BAUD_RATE = 115200
INTERVALO_LEITURA = 1  # segundos entre leituras
INTERVALO_SALVAMENTO = 15 * 60  # 15 minutos em segundos
TAMANHO_MEDIA_MOVIL = 10  # número de leituras para média móvel

# Nome do arquivo CSV
ARQUIVO_DADOS = 'dados_aht10.csv'

class ColetorDados:
    def __init__(self):
        self.temperaturas = deque(maxlen=TAMANHO_MEDIA_MOVIL)
        self.umidades = deque(maxlen=TAMANHO_MEDIA_MOVIL)
        self.todas_temperaturas = []
        self.todas_umidades = []
        self.ultima_leitura = None
        
    def adicionar_leitura(self, temp, hum):
        """Adiciona uma leitura às filas de média móvel"""
        self.temperaturas.append(temp)
        self.umidades.append(hum)
        self.todas_temperaturas.append(temp)
        self.todas_umidades.append(hum)
        self.ultima_leitura = (temp, hum)
        
    def get_media_movil(self):
        """Retorna a média móvel atual"""
        if not self.temperaturas:
            return None, None
        
        media_temp = sum(self.temperaturas) / len(self.temperaturas)
        media_hum = sum(self.umidades) / len(self.umidades)
        return media_temp, media_hum
    
    def get_media_total(self):
        """Retorna a média de todas as leituras do período"""
        if not self.todas_temperaturas:
            return None, None
        
        media_temp = sum(self.todas_temperaturas) / len(self.todas_temperaturas)
        media_hum = sum(self.todas_umidades) / len(self.todas_umidades)
        return media_temp, media_hum
    
    def limpar_dados_periodo(self):
        """Limpa os dados do período após salvar"""
        self.todas_temperaturas.clear()
        self.todas_umidades.clear()

def criar_arquivo_csv():
    """Cria o arquivo CSV com cabeçalho se não existir"""
    if not os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, 'w', newline='') as arquivo:
            escritor = csv.writer(arquivo)
            escritor.writerow(['Timestamp', 'Media_Movel_Temp_C', 'Media_Movel_Hum_%', 
                             'Media_Periodo_Temp_C', 'Media_Periodo_Hum_%', 
                             'Num_Leituras', 'Ultima_Temp_C', 'Ultima_Hum_%'])

def salvar_dados(coletor):
    """Salva as médias no arquivo CSV"""
    media_movil_temp, media_movil_hum = coletor.get_media_movil()
    media_periodo_temp, media_periodo_hum = coletor.get_media_total()
    
    if media_movil_temp is None:
        print("Sem dados para salvar")
        return
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    num_leituras = len(coletor.todas_temperaturas)
    
    with open(ARQUIVO_DADOS, 'a', newline='') as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow([
            timestamp,
            f"{media_movil_temp:.2f}",
            f"{media_movil_hum:.2f}",
            f"{media_periodo_temp:.2f}" if media_periodo_temp else "N/A",
            f"{media_periodo_hum:.2f}" if media_periodo_hum else "N/A",
            num_leituras,
            f"{coletor.ultima_leitura[0]:.2f}" if coletor.ultima_leitura else "N/A",
            f"{coletor.ultima_leitura[1]:.2f}" if coletor.ultima_leitura else "N/A"
        ])
    
    print(f"\n[{timestamp}] Dados salvos:")
    print(f"  Média Móvel: {media_movil_temp:.2f}°C, {media_movil_hum:.2f}%")
    print(f"  Média Período: {media_periodo_temp:.2f}°C, {media_periodo_hum:.2f}%")
    print(f"  Leituras: {num_leituras}")
    print("-" * 50)
    
    coletor.limpar_dados_periodo()

def main():
    coletor = ColetorDados()
    criar_arquivo_csv()
    
    tempo_inicio = time.time()
    tempo_ultimo_salvamento = tempo_inicio
    leituras_recebidas = 0
    
    try:
        print(f"Abrindo porta {PORTA}...")
        ser = serial.Serial(PORTA, BAUD_RATE, timeout=2)
        time.sleep(2)  # Aguarda conexão estabilizar
        
        print(f"Coletando dados do AHT10...")
        print(f"Salvamento a cada {INTERVALO_SALVAMENTO//60} minutos")
        print(f"Média móvel de {TAMANHO_MEDIA_MOVIL} leituras")
        print("Pressione Ctrl+C para parar\n")
        print("Tempo | Média Móvel Temp | Média Móvel Hum | Última Temp | Última Hum")
        print("-" * 70)

        while True:
            linha = ser.read(1);                   #readline().decode("utf-8", errors="ignore").strip()
            print(linha)
            time.sleep(0.5)
        
        while True:
            tempo_atual = time.time()
            
            # Verifica se é hora de salvar (a cada 15 minutos)
            if (tempo_atual - tempo_ultimo_salvamento) >= INTERVALO_SALVAMENTO:
                salvar_dados(coletor)
                tempo_ultimo_salvamento = tempo_atual
            
            # Lê dados da serial
            if ser.in_waiting > 0:
                try:
                    linha = ser.readline().decode('utf-8').strip()
                    
                    if ',' in linha:
                        temp, hum = map(float, linha.split(','))
                        coletor.adicionar_leitura(temp, hum)
                        leituras_recebidas += 1
                        
                        # Mostra em tempo real
                        media_movil_temp, media_movil_hum = coletor.get_media_movil()
                        minutos_decorridos = int((tempo_atual - tempo_inicio) // 60)
                        
                        print(f"{minutos_decorridos:2d}min  | "
                              f"{media_movil_temp:16.2f}°C | "
                              f"{media_movil_hum:15.2f}% | "
                              f"{temp:11.2f}°C | "
                              f"{hum:10.2f}%", 
                              end='\r')
                        
                except ValueError as e:
                    print(f"\nDado inválido: {linha}")
                except Exception as e:
                    print(f"\nErro ao processar: {e}")
            
            time.sleep(INTERVALO_LEITURA)
            
    except serial.SerialException as e:
        print(f"\nErro ao abrir porta serial: {e}")
        print("Verifique se:")
        print("  1. O Digispark está conectado")
        print("  2. Você tem permissão para acessar /dev/ttyACM0")
        print("  3. A porta está correta (use 'ls /dev/ttyACM*' para verificar)")
    except KeyboardInterrupt:
        print("\n\nEncerrando coleta...")
        # Salva dados restantes antes de fechar
        if coletor.todas_temperaturas:
            salvar_dados(coletor)
        print(f"Total de leituras: {leituras_recebidas}")
        print(f"Dados salvos em: {os.path.abspath(ARQUIVO_DADOS)}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()