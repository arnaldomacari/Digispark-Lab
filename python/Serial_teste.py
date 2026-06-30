import serial
import time
import csv
from datetime import datetime
from collections import deque
import os

# Configurações
PORTA = '/dev/ttyACM0'
BAUD_RATE = 9600  # Mudamos para 9600 (padrão mais seguro para CDC virtual)
INTERVALO_SALVAMENTO = 15 * 60  # 15 minutos
TAMANHO_MEDIA_MOVIL = 10

ARQUIVO_DADOS = 'dados_aht10.csv'

class ColetorDados:
    def __init__(self):
        self.temperaturas = deque(maxlen=TAMANHO_MEDIA_MOVIL)
        self.umidades = deque(maxlen=TAMANHO_MEDIA_MOVIL)
        self.todas_temperaturas = []
        self.todas_umidades = []
        self.ultima_leitura = None
        
    def adicionar_leitura(self, temp, hum):
        self.temperaturas.append(temp)
        self.umidades.append(hum)
        self.todas_temperaturas.append(temp)
        self.todas_umidades.append(hum)
        self.ultima_leitura = (temp, hum)
        
    def get_media_movil(self):
        if not self.temperaturas: return None, None
        return sum(self.temperaturas) / len(self.temperaturas), sum(self.umidades) / len(self.umidades)
    
    def get_media_total(self):
        if not self.todas_temperaturas: return None, None
        return sum(self.todas_temperaturas) / len(self.todas_temperaturas), sum(self.todas_umidades) / len(self.todas_umidades)
    
    def limpar_dados_periodo(self):
        self.todas_temperaturas.clear()
        self.todas_umidades.clear()

def criar_arquivo_csv():
    if not os.path.exists(ARQUIVO_DADOS):
        with open(ARQUIVO_DADOS, 'w', newline='') as arquivo:
            escritor = csv.writer(arquivo)
            escritor.writerow(['Timestamp', 'Media_Movel_Temp_C', 'Media_Movel_Hum_%', 
                             'Media_Periodo_Temp_C', 'Media_Periodo_Hum_%', 
                             'Num_Leituras', 'Ultima_Temp_C', 'Ultima_Hum_%'])

def salvar_dados(coletor):
    media_movil_temp, media_movil_hum = coletor.get_media_movil()
    media_periodo_temp, media_periodo_hum = coletor.get_media_total()
    
    if media_movil_temp is None: return
    
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(ARQUIVO_DADOS, 'a', newline='') as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow([
            timestamp, f"{media_movil_temp:.2f}", f"{media_movil_hum:.2f}",
            f"{media_periodo_temp:.2f}" if media_periodo_temp else "N/A",
            f"{media_periodo_hum:.2f}" if media_periodo_hum else "N/A",
            len(coletor.todas_temperaturas),
            f"{coletor.ultima_leitura[0]:.2f}", f"{coletor.ultima_leitura[1]:.2f}"
        ])
    
    print(f"\n[{timestamp}] Dados salvos! (Média Móvel: {media_movil_temp:.1f}°C / {media_movil_hum:.1f}%)")
    coletor.limpar_dados_periodo()

def main():
    coletor = ColetorDados()
    criar_arquivo_csv()
    
    tempo_ultimo_salvamento = time.time()
    
    try:
        print(f"Aguardando porta {PORTA}...")
        # timeout=2 é crucial: faz o readline() destravar se não chegar nada
        ser = serial.Serial(PORTA, BAUD_RATE, timeout=2) 
        time.sleep(2) 
        
        print("Conectado! Coletando dados...\n")
        
        while True:
            tempo_atual = time.time()
            
            if (tempo_atual - tempo_ultimo_salvamento) >= INTERVALO_SALVAMENTO:
                salvar_dados(coletor)
                tempo_ultimo_salvamento = tempo_atual
            
            # Lê a linha diretamente. O timeout=2 vai fazer ele esperar ou pular se não vier nada
            try:
                linha = ser.readline().decode('utf-8').strip()
                
                if ';' in linha:
                    temp, hum = map(float, linha.split(';'))
                    coletor.adicionar_leitura(temp, hum)
                    
                    media_t, media_h = coletor.get_media_movil()
                    print(f"Temp: {temp:.1f}°C | Hum: {hum:.1f}% | Média Móvel: {media_t:.1f}°C / {media_h:.1f}%", end='\r')
                    
            except ValueError:
                pass # Ignora linhas vazias ou lixo do buffer
            except UnicodeDecodeError:
                pass
                
    except serial.SerialException as e:
        print(f"\nErro na porta serial: {e}")
        print("Dica: Verifique se o Digispark está conectado e se você está no grupo 'dialout'.")
    except KeyboardInterrupt:
        print("\n\nEncerrando...")
        if coletor.todas_temperaturas:
            salvar_dados(coletor)
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()