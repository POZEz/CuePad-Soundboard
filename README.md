<div align="center">
  <img src="./icone.ico" alt="CuePad Icon" width="76" height="76" />
  <h1>CuePad</h1>
  <p><strong>Soundboard & Audio Router for Discord</strong></p>
  <p>Painel de áudio minimalista com roteamento duplo (Fone + Call), injeção de microfone com mute automático, corte de faixas, atalhos globais em jogos e controle remoto via Wi-Fi.</p>
  <p><sub>Desenvolvido com auxílio de Inteligência Artificial e revisado/testado manualmente.</sub></p>
</div>

---

### Recursos Principais

- **Roteamento Flexível:** Toque áudios **Só no Fone** (Preview privado), **Só na Call** ou em **Fone + Call** simultaneamente.
- **Injeção de Microfone + Auto-Mute:** Mistura sua voz diretamente no Cabo Virtual e silencia seu microfone físico automaticamente enquanto um áudio toca.
- **Normalização & Overdrive:** Nivelamento automático de volume e ganho de até `800%` (modo estourado em tempo real).
- **Corte Rápido (Trim):** Defina início e fim em segundos para pular trechos ou exportar novos clipes `.wav`.
- **Atalhos em Jogos:** Dispare sons em tela cheia (`F1`–`F12`, `NUM0`–`NUM9`, `ALT+1`–`ALT+0`, `CTRL+1`–`CTRL+0`) e pare tudo imediatamente com <kbd>END</kbd>.
- **Controle pelo Celular:** Web App responsivo integrado na rede local Wi-Fi com busca, controle de volume e modo Preview.
- **Interface Bilíngue (`🇧🇷 PT` / `🇺🇸 EN`):** Tradução instantânea e configurações salvas automaticamente em `%APPDATA%\CuePad\settings.config`.

---

### Pré-requisitos

1. **Windows 10 / 11**
2. **VB-CABLE Virtual Audio Device** — baixe em [vb-audio.com/Cable](https://vb-audio.com/Cable/), execute `VBCABLE_Setup_x64.exe` como Administrador e reinicie o PC.
3. **Python 3.10+** *(apenas se for executar pelo código-fonte)*

---

### Instalação e Execução

```bash
git clone https://github.com/POZEz/CuePad-Soundboard.git
cd CuePad-Soundboard
pip install -r requirements.txt
python CuePad.py
```

#### Configurando no Discord
1. **No CuePad:** Em **Saídas de Áudio**, selecione `CABLE Input (VB-Audio Virtual Cable)` como saída do Discord, escolha seu Headset abaixo e marque **"Juntar minha voz no Cabo Virtual"**.
2. **No Discord:** Em **Configurações de Usuário → Voz e Vídeo**, defina o **Dispositivo de Entrada** como `CABLE Output (VB-Audio Virtual Cable)`.

---

### Controle Remoto pelo Celular

1. Clique em **USAR CELULAR** na barra superior do CuePad.
2. Acesse o endereço exibido (ex: `http://192.168.x.x:8765`) pelo navegador do celular conectado ao mesmo Wi-Fi.
3. Caso o Firewall do Windows bloqueie a conexão externa, clique em **LIBERAR PORTA NO FIREWALL (ADMIN)** na própria janela.

---

### Compilar Executável Portátil (`CuePad.exe`)

```bash
pip install pyinstaller pillow
pyinstaller --noconsole --onefile --clean --collect-all sounddevice --icon="icone.ico" --add-data="icone.ico;." --name="CuePad" CuePad.py
```
