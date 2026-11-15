<div align="center">
  <img src="./icone.ico" alt="Soundboard Discord Icon" width="72" height="72" />
  <h1>Soundboard Discord</h1>
  <p>Painel de áudio minimalista para chamadas do Discord com roteamento de cabo virtual, mistura de microfone, atalhos globais e controle remoto via Wi-Fi.</p>
  <p><sub>Desenvolvido com auxílio de Inteligência Artificial e revisado/testado manualmente.</sub></p>
</div>

---

### Funcionalidades

- **Roteamento de Saída:** Reprodução **Só no Fone** (Preview privado), **Só na Call** ou em **Ambos (Fone + Call)** simultaneamente.
- **Injeção de Microfone + Block Voice:** Mistura a voz com os efeitos sonoros no cabo virtual e muta o microfone físico automaticamente enquanto o áudio toca.
- **Normalização & Overdrive:** Nivelamento automático de picos e ganho amplificado até `800%` com distorção em tempo real.
- **Editor de Corte (Trim):** Definição de início/fim em segundos para saltar trechos ou exportar novos arquivos `.wav`.
- **Atalhos Globais:** Disparo de áudios dentro de jogos em tela cheia (`F1`–`F12`, `NUM0`–`NUM9`, `ALT+1`–`ALT+9`) e parada imediata com <kbd>END</kbd>.
- **Controle pelo Celular:** Servidor HTTP local embutido para acionar áudios pelo navegador na rede Wi-Fi.
- **Bilíngue (`PT` / `EN`):** Troca instantânea de idioma com configurações persistidas em `%APPDATA%\SoundboardDiscord\settings.config`.

---

### Pré-requisitos

1. **Windows 10 / 11**
2. **Python 3.10+** *(para rodar pelo código-fonte)*
3. **VB-CABLE Virtual Audio Device** — baixe em [vb-audio.com/Cable](https://vb-audio.com/Cable/), execute `VBCABLE_Setup_x64.exe` como Administrador e reinicie o PC.

---

### Instalação e Uso

```bash
git clone https://github.com/SEU-USUARIO/soundboard-discord.git
cd soundboard-discord
pip install -r requirements.txt
python painel_soundboard_discord.py
```

#### Configuração rápida no Discord
1. **No Soundboard:** Selecione `CABLE Input (VB-Audio Virtual Cable)` como saída da call e marque **"Juntar minha voz no Cabo Virtual"** *(ou ative "Escutar o dispositivo" nas propriedades de som do Windows para zero latência)*.
2. **No Discord:** Em **Configurações de Usuário → Voz e Vídeo**, defina o **Dispositivo de Entrada** como `CABLE Output (VB-Audio Virtual Cable)`.

---

### Controle Remoto (Celular)

1. Clique em **USAR CELULAR** no topo do programa.
2. Abra o endereço local exibido (ex: `http://192.168.x.x:8765`) no navegador do smartphone conectado ao mesmo Wi-Fi.
3. Caso o Firewall do Windows bloqueie o acesso, clique em **LIBERAR PORTA NO FIREWALL (ADMIN)** dentro do modal.

---

### Gerar Executável (`.exe`)

```bash
pip install pyinstaller pillow
pyinstaller --noconsole --onefile --clean --collect-all sounddevice --icon="icone.ico" --add-data="icone.ico;." --name="SoundboardDiscord" painel_soundboard_discord.py
```
