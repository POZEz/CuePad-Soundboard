import os
import sys
import json
import math
import wave
import array
import socket
import ctypes
import tempfile
import threading
import subprocess
import urllib.parse
import html
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

# Módulo nativo para amplificar e distorcer o áudio (Boost/Estourado)
try:
    import audioop
except ImportError:
    audioop = None

# Módulos opcionais para Saída Dupla Simultânea (Fone + Call) e Injeção de Mic
try:
    import numpy as np
    import sounddevice as sd
    SOUNDDEVICE_DISPONIVEL = True
except ImportError:
    np = None
    sd = None
    SOUNDDEVICE_DISPONIVEL = False

# Importação do pygame e do módulo SDL2 para listar placas de som
try:
    import pygame
    import pygame._sdl2.audio as sdl2_audio
except ImportError:
    print("ERRO: A biblioteca 'pygame' não está instalada.")
    print("No terminal do VS Code, digite: pip install pygame")
    sys.exit(1)


# ==============================================================================
# CONFIGURAÇÃO DO DIRETÓRIO DE ÁUDIOS E CONSTANTES DO SISTEMA (CUEPAD)
# ==============================================================================
APP_NAME = "CuePad"
APP_VERSION = "1.0.0"
APP_ID_WINDOWS = "CuePad.Soundboard.Desktop.1"

APPDATA_ROOT = os.getenv("APPDATA") or os.path.expanduser("~")
PASTA_APP_DATA = os.path.join(APPDATA_ROOT, "CuePad")
PASTA_APP_DATA_LEGADO = os.path.join(APPDATA_ROOT, "SoundboardDiscord")
ARQUIVO_PREFERENCIAS_GLOBAIS = os.path.join(PASTA_APP_DATA, "settings.config")
ARQUIVO_PREFERENCIAS_LEGADO = os.path.join(PASTA_APP_DATA_LEGADO, "settings.config")

PASTA_PADRAO_AUDIOS = os.path.join(os.path.expanduser("~"), "Documents", "AudiosDiscord")
FORMATOS_SUPORTADOS = (".mp3", ".wav", ".ogg")
PORTA_API_REMOTA = 8765

PLAYLIST_TODOS = "TODOS"
PLAYLIST_FAVORITOS = "FAVORITOS"

MAPA_VK_WINDOWS = {
    "F1": 0x70, "F2": 0x71, "F3": 0x72, "F4": 0x73,
    "F5": 0x74, "F6": 0x75, "F7": 0x76, "F8": 0x77,
    "F9": 0x78, "F10": 0x79, "F11": 0x7A, "F12": 0x7B,
    "NUM0": 0x60, "NUM1": 0x61, "NUM2": 0x62, "NUM3": 0x63, "NUM4": 0x64,
    "NUM5": 0x65, "NUM6": 0x66, "NUM7": 0x67, "NUM8": 0x68, "NUM9": 0x69,
    "NUM+": 0x6B, "NUM-": 0x6D, "NUM*": 0x6A, "NUM/": 0x6F,
    "ALT+1": (0x12, 0x31), "ALT+2": (0x12, 0x32), "ALT+3": (0x12, 0x33),
    "ALT+4": (0x12, 0x34), "ALT+5": (0x12, 0x35), "ALT+6": (0x12, 0x36),
    "ALT+7": (0x12, 0x37), "ALT+8": (0x12, 0x38), "ALT+9": (0x12, 0x39),
    "ALT+0": (0x12, 0x30),
    "CTRL+1": (0x11, 0x31), "CTRL+2": (0x11, 0x32), "CTRL+3": (0x11, 0x33),
    "CTRL+4": (0x11, 0x34), "CTRL+5": (0x11, 0x35), "CTRL+6": (0x11, 0x36),
    "CTRL+7": (0x11, 0x37), "CTRL+8": (0x11, 0x38), "CTRL+9": (0x11, 0x39),
    "CTRL+0": (0x11, 0x30),
    "END": 0x23, "HOME": 0x24, "INSERT": 0x2D, "PAGEUP": 0x21, "PAGEDOWN": 0x22,
}

TRADUCOES = {
    "pt": {
        "app_title": "CUEPAD",
        "app_subtitle": "SOUNDBOARD & ROTEADOR DE ÁUDIO",
        "status_ready": "PRONTO — TECLA [END] PARA O ÁUDIO EM QUALQUER JOGO",
        "btn_guide": "? GUIA",
        "btn_remote": "USAR CELULAR",
        "btn_win_mic": "SOM DO WINDOWS",
        "sec_outputs": "SAÍDAS DE ÁUDIO",
        "lbl_output_mode": "ONDE O ÁUDIO VAI TOCAR",
        "mode_fone": "SÓ FONE",
        "mode_call": "SÓ CALL",
        "mode_ambos": "FONE + CALL",
        "lbl_call_out": "SAÍDA PARA O DISCORD (CABO VIRTUAL)",
        "lbl_fone_out": "SEU FONE OU CAIXA DE SOM",
        "sec_mic": "SEU MICROFONE",
        "lbl_mic_in": "MICROFONE FÍSICO",
        "chk_inject_mic": "Juntar minha voz no Cabo Virtual",
        "chk_block_voice": "Mutar minha voz enquanto o áudio toca",
        "sec_hotkeys": "ATALHOS EM JOGOS",
        "chk_hotkeys": "Ativar atalhos durante jogos",
        "btn_bind_key": "DEFINIR TECLA",
        "sec_folder": "PASTA DE ÁUDIOS",
        "btn_browse": "ESCOLHER PASTA",
        "btn_rescan": "ATUALIZAR",
        "lbl_search": "BUSCAR",
        "lbl_enter_hint": "[ENTER TOCA]",
        "lbl_collection": "LISTA",
        "btn_add_list": "+ LISTA",
        "btn_add_track": "+ SALVAR",
        "btn_rem_track": "- REMOVER",
        "col_key": "ATALHO",
        "col_name": "NOME DO ÁUDIO",
        "col_fmt": "TIPO",
        "col_dur": "DURAÇÃO",
        "lbl_selected": "SELECIONADO:",
        "lbl_no_track": "NENHUM ÁUDIO SELECIONADO",
        "chk_normalize": "Igualar volume automático",
        "btn_play": "TOCAR",
        "btn_preview": "OUVIR SÓ NO FONE",
        "btn_pause": "PAUSAR",
        "btn_resume": "RETOMAR",
        "btn_stop": "PARAR [END]",
        "lbl_in": "INÍCIO(S)",
        "lbl_out": "FIM(S)",
        "btn_locate": "IR P/ SEG",
        "btn_trim": "CORTAR ÁUDIO",
        "btn_overdrive": "ESTOURAR",
        "btn_clip_on": "ESTOURADO",
        "tracks_count": "{n} ÁUDIOS",
        "status_index": "LISTA PRONTA — {n} ÁUDIO(S) VISÍVEIS",
        "status_select_first": "SELECIONE UM ÁUDIO NA TABELA PRIMEIRO",
        "status_playing": "TOCANDO [{modo}] — {arq} ({tempo})",
        "status_preview": "OUVINDO SÓ NO FONE — {arq} ({tempo})",
        "status_paused": "PAUSADO — {arq}",
        "status_stopped": "ÁUDIO PARADO",
        "status_finished": "REPRODUÇÃO CONCLUÍDA",
        "status_out_changed": "SAÍDA ATIVA -> {disp}",
        "status_added_list": "ADICIONADO '{arq}' EM [{lista}]",
        "status_trim_saved": "CORTE SALVO -> {arq}",
        "dlg_folder_title": "Selecione a pasta de áudios",
        "dlg_new_list_title": "Nova Lista",
        "dlg_new_list_prompt": "Nome da nova lista/coleção:",
        "dlg_warn_title": "Aviso",
        "dlg_remove_list_info": "Selecione uma lista personalizada (ex: FAVORITOS) para remover áudios dela.",
        "dlg_trim_err_num": "Informe valores numéricos válidos para INÍCIO(S) e FIM(S).",
        "dlg_trim_err_range": "O segundo de INÍCIO(S) deve ser menor que o FIM(S).",
        "dlg_trim_prompt": "Trecho: {ini:.1f}s até {fim:.1f}s.\nNome do novo arquivo:",
        "dlg_hk_title": "Definir Atalho",
        "dlg_hk_target": "ÁUDIO: {arq}",
        "dlg_hk_prompt": "Escolha a tecla ou pressione no teclado:",
        "dlg_hk_confirm": "SALVAR ATALHO",
        "dlg_hk_none": "NENHUM",
        "ctx_play": "Tocar na Saída Principal",
        "ctx_preview": "Ouvir Só no Fone (Preview)",
        "ctx_hotkey": "Definir Tecla de Atalho...",
        "ctx_add_fav": "Salvar na Lista / Favoritos",
        "ctx_trim": "Cortar e Salvar Trecho...",
        "tut_title": "GUIA RÁPIDO DO CUEPAD",
        "tut_skip": "FECHAR",
        "tut_prev": "ANTERIOR",
        "tut_next": "PRÓXIMO",
        "tut_finish": "CONCLUIR",
        "tut_steps": [
            (
                "1/4 — COMO ENVIAR ÁUDIO PARA O DISCORD",
                "• Em 'SAÍDAS DE ÁUDIO' (à esquerda), deixe selecionado o 'CABLE Input' como saída para o Discord e escolha o seu Headset logo abaixo.\n\n"
                "• No aplicativo do Discord (Voz e Vídeo), mude o Dispositivo de Entrada (Microfone) para 'CABLE Output'.\n\n"
                "• Você pode escolher tocar o som em 'FONE + CALL' (você e a call ouvem), 'SÓ CALL' ou 'SÓ FONE'."
            ),
            (
                "2/4 — USANDO SEU MICROFONE JUNTO",
                "• Para falar normalmente no Discord sem trocar de microfone, marque 'Juntar minha voz no Cabo Virtual' em 'SEU MICROFONE'.\n\n"
                "• Ou clique em 'SOM DO WINDOWS' no topo para ativar a opção 'Escutar o dispositivo' nativa do Windows (zero atraso).\n\n"
                "• A opção 'Mutar minha voz enquanto o áudio toca' corta o ruído do seu quarto automaticamente durante os memes."
            ),
            (
                "3/4 — TESTAR NO FONE, LISTAS E CORTE",
                "• Quer ouvir um áudio antes sem mandar na call? Clique no botão 'OUVIR SÓ NO FONE' no rodapé (ou com o botão direito na tabela).\n\n"
                "• Na barra superior, você pode filtrar pelo nome, criar listas personalizadas (+ LISTA) e salvar os melhores áudios (+ SALVAR).\n\n"
                "• No rodapé, ajuste INÍCIO(S) e FIM(S) para tocar de um segundo exato ou clicar em 'CORTAR ÁUDIO' para salvar um trecho."
            ),
            (
                "4/4 — ATALHOS EM JOGOS E ÁUDIO ESTOURADO",
                "• Clique em um áudio e depois em 'DEFINIR TECLA' para criar um atalho (ex: F1, NUM1, ALT+1, CTRL+1) que funciona mesmo dentro de jogos em tela cheia.\n\n"
                "• A tecla [END] do teclado para qualquer áudio imediatamente.\n\n"
                "• Arraste a barra de volume para a direita (acima de 100%) ou clique em 'ESTOURAR' para distorcer o áudio em tempo real."
            ),
        ],
    },
    "en": {
        "app_title": "CUEPAD",
        "app_subtitle": "SOUNDBOARD & AUDIO ROUTER",
        "status_ready": "READY — PRESS [END] TO STOP AUDIO IN ANY GAME",
        "btn_guide": "? GUIDE",
        "btn_remote": "PHONE REMOTE",
        "btn_win_mic": "WINDOWS SOUND",
        "sec_outputs": "AUDIO OUTPUTS",
        "lbl_output_mode": "WHERE TO PLAY AUDIO",
        "mode_fone": "HEADPHONES",
        "mode_call": "CALL ONLY",
        "mode_ambos": "BOTH",
        "lbl_call_out": "DISCORD OUTPUT (VIRTUAL CABLE)",
        "lbl_fone_out": "YOUR HEADPHONES / SPEAKERS",
        "sec_mic": "YOUR MICROPHONE",
        "lbl_mic_in": "PHYSICAL MICROPHONE",
        "chk_inject_mic": "Mix my voice into Virtual Cable",
        "chk_block_voice": "Mute my mic while audio plays",
        "sec_hotkeys": "IN-GAME HOTKEYS",
        "chk_hotkeys": "Enable hotkeys while gaming",
        "btn_bind_key": "SET HOTKEY",
        "sec_folder": "AUDIO FOLDER",
        "btn_browse": "BROWSE FOLDER",
        "btn_rescan": "REFRESH",
        "lbl_search": "SEARCH",
        "lbl_enter_hint": "[ENTER PLAYS]",
        "lbl_collection": "LIST",
        "btn_add_list": "+ LIST",
        "btn_add_track": "+ SAVE",
        "btn_rem_track": "- REMOVE",
        "col_key": "HOTKEY",
        "col_name": "AUDIO NAME",
        "col_fmt": "TYPE",
        "col_dur": "LENGTH",
        "lbl_selected": "SELECTED:",
        "lbl_no_track": "NO AUDIO SELECTED",
        "chk_normalize": "Auto-level volume",
        "btn_play": "PLAY",
        "btn_preview": "PREVIEW ON HEADPHONES",
        "btn_pause": "PAUSE",
        "btn_resume": "RESUME",
        "btn_stop": "STOP [END]",
        "lbl_in": "START(S)",
        "lbl_out": "END(S)",
        "btn_locate": "JUMP TO",
        "btn_trim": "TRIM AUDIO",
        "btn_overdrive": "BASS BOOST",
        "btn_clip_on": "BOOST ON",
        "tracks_count": "{n} TRACKS",
        "status_index": "LIST READY — {n} TRACK(S) VISIBLE",
        "status_select_first": "SELECT AN AUDIO FROM THE LIST FIRST",
        "status_playing": "PLAYING [{modo}] — {arq} ({tempo})",
        "status_preview": "PREVIEWING ON HEADPHONES — {arq} ({tempo})",
        "status_paused": "PAUSED — {arq}",
        "status_stopped": "AUDIO STOPPED",
        "status_finished": "PLAYBACK FINISHED",
        "status_out_changed": "ACTIVE OUTPUT -> {disp}",
        "status_added_list": "ADDED '{arq}' TO [{lista}]",
        "status_trim_saved": "TRIM SAVED -> {arq}",
        "dlg_folder_title": "Select audio folder",
        "dlg_new_list_title": "New Collection",
        "dlg_new_list_prompt": "Name for the new list/collection:",
        "dlg_warn_title": "Notice",
        "dlg_remove_list_info": "Select a custom list (e.g. FAVORITOS) to remove tracks from it.",
        "dlg_trim_err_num": "Enter valid numeric values for START(S) and END(S).",
        "dlg_trim_err_range": "START(S) must be less than END(S).",
        "dlg_trim_prompt": "Range: {ini:.1f}s to {fim:.1f}s.\nNew file name:",
        "dlg_hk_title": "Assign Hotkey",
        "dlg_hk_target": "TRACK: {arq}",
        "dlg_hk_prompt": "Select a key or press it on your keyboard:",
        "dlg_hk_confirm": "SAVE HOTKEY",
        "dlg_hk_none": "NONE",
        "ctx_play": "Play on Active Output",
        "ctx_preview": "Preview on Headphones Only",
        "ctx_hotkey": "Assign Hotkey...",
        "ctx_add_fav": "Save to List / Favorites",
        "ctx_trim": "Trim and Export Clip...",
        "tut_title": "CUEPAD QUICK START GUIDE",
        "tut_skip": "CLOSE",
        "tut_prev": "PREVIOUS",
        "tut_next": "NEXT",
        "tut_finish": "DONE",
        "tut_steps": [
            (
                "1/4 — SENDING AUDIO TO DISCORD",
                "• Under 'AUDIO OUTPUTS' (on the left), select 'CABLE Input' as your Discord Output and choose your Headphones below it.\n\n"
                "• Inside Discord (Voice & Video settings), set your Input Device (Microphone) to 'CABLE Output'.\n\n"
                "• You can choose to play sounds on 'BOTH' (you and the call hear it), 'CALL ONLY', or 'HEADPHONES'."
            ),
            (
                "2/4 — USING YOUR MICROPHONE TOGETHER",
                "• To speak normally on Discord without switching microphones, check 'Mix my voice into Virtual Cable' under 'YOUR MICROPHONE'.\n\n"
                "• Or click 'WINDOWS SOUND' at the top to enable native Windows 'Listen to this device' (zero latency).\n\n"
                "• Checking 'Mute my mic while audio plays' automatically silences background room noise while a sound clip is playing."
            ),
            (
                "3/4 — HEADPHONE PREVIEW, LISTS & TRIMMING",
                "• Want to test a sound privately without sending it to the call? Click 'PREVIEW ON HEADPHONES' at the bottom (or right-click any track).\n\n"
                "• Use the top bar to search by name, create custom collections (+ LIST), and save your favorite clips (+ SAVE).\n\n"
                "• Set START(S) and END(S) at the bottom to start from a specific second or click 'TRIM AUDIO' to save a cut clip."
            ),
            (
                "4/4 — IN-GAME HOTKEYS & BASS BOOST",
                "• Select any track and click 'SET HOTKEY' to bind a key (e.g., F1, NUM1, ALT+1, CTRL+1) that works even inside fullscreen games.\n\n"
                "• Pressing the [END] key immediately stops any playing audio.\n\n"
                "• Drag the volume slider past 100% or click 'BASS BOOST' for real-time distorted meme audio."
            ),
        ],
    },
}


# ==============================================================================
# 1. CONFIGURAÇÃO VISUAL CENTRALIZADA (DESIGN SYSTEM)
# ==============================================================================
class ThemeConfig:
    """Centraliza cores, tipografia, dimensões e regras de estilo da interface."""

    BG_MAIN = "#0B0B0B"        # Fundo principal
    BG_SURFACE = "#151515"     # Superfícies secundárias
    BG_HOVER = "#1C1C1C"       # Estado de interação sutil
    DIVIDER = "#262626"        # Divisores e bordas de 1px
    TEXT_PRIMARY = "#EAEAEA"   # Texto principal
    TEXT_SECONDARY = "#858585" # Texto secundário / rótulos técnicos
    ACCENT = "#D95726"         # Cor única de destaque (Âmbar de equipamento de estúdio)

    FONT_UI = ("Segoe UI", 9)
    FONT_UI_BOLD = ("Segoe UI", 9, "bold")
    FONT_LABEL = ("Segoe UI", 8, "bold")
    FONT_TITLE = ("Segoe UI", 10, "bold")
    FONT_MONO = ("Consolas", 9)
    FONT_MONO_BOLD = ("Consolas", 9, "bold")
    FONT_TIME = ("Consolas", 11, "bold")

    SIDEBAR_WIDTH = 310
    ROW_HEIGHT = 28

    @classmethod
    def aplicar_estilos_ttk(cls, root: tk.Tk) -> ttk.Style:
        """Configura o tema base do ttk para seguir a geometria reta e paleta escura."""
        style = ttk.Style(root)
        style.theme_use("clam")

        style.configure("TFrame", background=cls.BG_MAIN)
        style.configure("Surface.TFrame", background=cls.BG_SURFACE)

        style.configure(
            "TLabel",
            background=cls.BG_MAIN,
            foreground=cls.TEXT_PRIMARY,
            font=cls.FONT_UI
        )
        style.configure(
            "Surface.TLabel",
            background=cls.BG_SURFACE,
            foreground=cls.TEXT_PRIMARY,
            font=cls.FONT_UI
        )
        style.configure(
            "Muted.TLabel",
            background=cls.BG_MAIN,
            foreground=cls.TEXT_SECONDARY,
            font=cls.FONT_LABEL
        )
        style.configure(
            "SurfaceMuted.TLabel",
            background=cls.BG_SURFACE,
            foreground=cls.TEXT_SECONDARY,
            font=cls.FONT_LABEL
        )

        style.configure(
            "TCombobox",
            fieldbackground=cls.BG_MAIN,
            background=cls.BG_SURFACE,
            foreground=cls.TEXT_PRIMARY,
            arrowcolor=cls.TEXT_SECONDARY,
            bordercolor=cls.DIVIDER,
            lightcolor=cls.DIVIDER,
            darkcolor=cls.DIVIDER,
            borderwidth=1,
            padding=4
        )
        style.map(
            "TCombobox",
            fieldbackground=[("readonly", cls.BG_MAIN)],
            selectbackground=[("readonly", cls.BG_MAIN)],
            selectforeground=[("readonly", cls.TEXT_PRIMARY)],
            background=[("active", cls.BG_HOVER)],
            arrowcolor=[("active", cls.TEXT_PRIMARY)]
        )

        root.option_add("*TCombobox*Listbox.background", cls.BG_SURFACE)
        root.option_add("*TCombobox*Listbox.foreground", cls.TEXT_PRIMARY)
        root.option_add("*TCombobox*Listbox.selectBackground", cls.DIVIDER)
        root.option_add("*TCombobox*Listbox.selectForeground", cls.TEXT_PRIMARY)
        root.option_add("*TCombobox*Listbox.font", cls.FONT_UI)
        root.option_add("*TCombobox*Listbox.Relief", "flat")

        style.configure(
            "Treeview",
            background=cls.BG_MAIN,
            foreground=cls.TEXT_PRIMARY,
            fieldbackground=cls.BG_MAIN,
            borderwidth=0,
            relief="flat",
            rowheight=cls.ROW_HEIGHT,
            font=cls.FONT_UI
        )
        style.configure(
            "Treeview.Heading",
            background=cls.BG_SURFACE,
            foreground=cls.TEXT_SECONDARY,
            bordercolor=cls.DIVIDER,
            lightcolor=cls.BG_SURFACE,
            darkcolor=cls.DIVIDER,
            borderwidth=1,
            relief="flat",
            padding=(8, 6),
            font=cls.FONT_LABEL
        )
        style.map(
            "Treeview.Heading",
            background=[("active", cls.BG_HOVER)],
            foreground=[("active", cls.TEXT_PRIMARY)]
        )
        style.map(
            "Treeview",
            background=[("selected", cls.BG_SURFACE)],
            foreground=[("selected", cls.ACCENT)]
        )

        style.configure(
            "Vertical.TScrollbar",
            background=cls.BG_SURFACE,
            troughcolor=cls.BG_MAIN,
            bordercolor=cls.BG_MAIN,
            lightcolor=cls.BG_SURFACE,
            darkcolor=cls.BG_SURFACE,
            arrowsize=0,
            relief="flat"
        )
        style.map(
            "Vertical.TScrollbar",
            background=[("active", cls.DIVIDER)]
        )

        return style


# ==============================================================================
# 2. COMPONENTES GRÁFICOS REUTILIZÁVEIS (BASEADOS EM TK.CANVAS)
# ==============================================================================
class HairlineDivider(tk.Frame):
    """Linha divisória precisa de 1px para estruturação geométrica."""

    def __init__(self, parent, orient="horizontal", **kwargs):
        height = 1 if orient == "horizontal" else kwargs.pop("height", 1)
        width = 1 if orient == "vertical" else kwargs.pop("width", 1)
        super().__init__(
            parent,
            bg=ThemeConfig.DIVIDER,
            height=height,
            width=width,
            bd=0,
            highlightthickness=0,
            **kwargs
        )


class SectionHeader(tk.Frame):
    """Cabeçalho de seção limpo com título direto e linha divisória de 1px."""

    def __init__(self, parent, title: str, bg=ThemeConfig.BG_SURFACE):
        super().__init__(parent, bg=bg)
        top = tk.Frame(self, bg=bg)
        top.pack(fill=tk.X, pady=(0, 4))

        self.lbl_title = tk.Label(
            top,
            text=title.upper(),
            bg=bg,
            fg=ThemeConfig.ACCENT,
            font=ThemeConfig.FONT_LABEL
        )
        self.lbl_title.pack(side=tk.LEFT)

        HairlineDivider(self, orient="horizontal").pack(fill=tk.X)

    def set_title(self, new_title: str):
        self.lbl_title.config(text=new_title.upper())


class StatusIndicatorLED(tk.Canvas):
    """Indicador luminoso quadrado minimalista para telemetria de estado."""

    def __init__(self, parent, size=8, bg=ThemeConfig.BG_SURFACE):
        super().__init__(
            parent,
            width=size,
            height=size,
            bg=bg,
            bd=0,
            highlightthickness=0
        )
        self.size = size
        self.rect = self.create_rectangle(
            0, 0, size, size,
            fill=ThemeConfig.DIVIDER,
            outline=""
        )

    def set_active(self, active: bool):
        color = ThemeConfig.ACCENT if active else ThemeConfig.DIVIDER
        self.itemconfig(self.rect, fill=color)


class StudioButton(tk.Canvas):
    """Botão retangular de geometria reta com borda de 1px e indicador de estado."""

    def __init__(
        self,
        parent,
        text: str,
        command=None,
        width=90,
        height=28,
        accent=False,
        bg_surface=ThemeConfig.BG_SURFACE
    ):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=bg_surface,
            bd=0,
            highlightthickness=1,
            highlightbackground=ThemeConfig.ACCENT if accent else ThemeConfig.DIVIDER,
            cursor="hand2"
        )
        self.command = command
        self.text = text
        self.accent_active = accent
        self.bg_default = bg_surface
        self._width = width
        self._height = height

        self.bind("<Configure>", self._redraw)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def set_text(self, new_text: str):
        self.text = new_text
        self._redraw()

    def set_accent(self, active: bool):
        self.accent_active = active
        self.configure(
            highlightbackground=ThemeConfig.ACCENT if active else ThemeConfig.DIVIDER
        )
        self._redraw()

    def _redraw(self, event=None):
        self.delete("all")
        w = self.winfo_width() if self.winfo_width() > 1 else self._width
        h = self.winfo_height() if self.winfo_height() > 1 else self._height

        if self.accent_active:
            self.create_rectangle(0, 0, 3, h, fill=ThemeConfig.ACCENT, outline="")

        fg_color = ThemeConfig.ACCENT if self.accent_active else ThemeConfig.TEXT_PRIMARY
        self.create_text(
            w // 2,
            h // 2,
            text=self.text,
            fill=fg_color,
            font=ThemeConfig.FONT_LABEL
        )

    def _on_enter(self, _):
        self.configure(bg=ThemeConfig.BG_HOVER)

    def _on_leave(self, _):
        self.configure(bg=self.bg_default)

    def _on_press(self, _):
        self.configure(bg=ThemeConfig.BG_MAIN)

    def _on_release(self, event):
        self.configure(bg=ThemeConfig.BG_HOVER)
        if 0 <= event.x <= self.winfo_width() and 0 <= event.y <= self.winfo_height():
            if self.command:
                self.command()


class StudioToggle(tk.Canvas):
    """Chave seletora booleana com indicador quadrado e tipografia limpa."""

    def __init__(
        self,
        parent,
        text: str,
        variable: tk.BooleanVar,
        command=None,
        bg=ThemeConfig.BG_SURFACE,
        height=24
    ):
        super().__init__(
            parent,
            height=height,
            bg=bg,
            bd=0,
            highlightthickness=0,
            cursor="hand2"
        )
        self.text = text
        self.variable = variable
        self.command = command
        self.bg_default = bg
        self._hover = False

        self.variable.trace_add("write", lambda *_: self._redraw())
        self.bind("<Configure>", self._redraw)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonRelease-1>", self._on_click)

    def set_text(self, new_text: str):
        self.text = new_text
        self._redraw()

    def _redraw(self, event=None):
        self.delete("all")
        h = self.winfo_height() if self.winfo_height() > 1 else 24
        cy = h // 2
        box_size = 12
        x0 = 2
        y0 = cy - (box_size // 2)
        x1 = x0 + box_size
        y1 = y0 + box_size

        ativo = bool(self.variable.get())
        borda = ThemeConfig.ACCENT if (ativo or self._hover) else ThemeConfig.DIVIDER
        self.create_rectangle(x0, y0, x1, y1, fill=ThemeConfig.BG_MAIN, outline=borda)

        if ativo:
            self.create_rectangle(x0 + 3, y0 + 3, x1 - 3, y1 - 3, fill=ThemeConfig.ACCENT, outline="")

        cor_texto = ThemeConfig.TEXT_PRIMARY if ativo else ThemeConfig.TEXT_SECONDARY
        self.create_text(
            x1 + 8,
            cy,
            text=self.text,
            fill=cor_texto,
            font=ThemeConfig.FONT_UI,
            anchor="w"
        )

    def _on_enter(self, _):
        self._hover = True
        self._redraw()

    def _on_leave(self, _):
        self._hover = False
        self._redraw()

    def _on_click(self, _):
        self.variable.set(not self.variable.get())
        if self.command:
            self.command()


class SegmentedBusSelector(tk.Canvas):
    """Seletor segmentado de 3 posições para roteamento de barramento de saída."""

    def __init__(self, parent, options: list, variable: tk.StringVar, command=None, height=28):
        super().__init__(
            parent,
            height=height,
            bg=ThemeConfig.BG_MAIN,
            bd=0,
            highlightthickness=1,
            highlightbackground=ThemeConfig.DIVIDER,
            cursor="hand2"
        )
        self.options = options
        self.variable = variable
        self.command = command
        self._height = height

        self.variable.trace_add("write", lambda *_: self._redraw())
        self.bind("<Configure>", self._redraw)
        self.bind("<ButtonRelease-1>", self._on_click)

    def set_options(self, new_options: list):
        self.options = new_options
        self._redraw()

    def _redraw(self, event=None):
        self.delete("all")
        w = max(1, self.winfo_width())
        h = max(1, self.winfo_height() if self.winfo_height() > 1 else self._height)
        n = len(self.options)
        seg_w = w / n
        valor_atual = self.variable.get()

        for i, (val, label) in enumerate(self.options):
            x0 = int(i * seg_w)
            x1 = int((i + 1) * seg_w) if i < n - 1 else w
            ativo = (val == valor_atual)

            bg_seg = ThemeConfig.BG_SURFACE if ativo else ThemeConfig.BG_MAIN
            self.create_rectangle(x0, 0, x1, h, fill=bg_seg, outline="")

            if ativo:
                self.create_rectangle(x0, 0, x1, 2, fill=ThemeConfig.ACCENT, outline="")

            if i > 0:
                self.create_line(x0, 0, x0, h, fill=ThemeConfig.DIVIDER)

            cor_txt = ThemeConfig.TEXT_PRIMARY if ativo else ThemeConfig.TEXT_SECONDARY
            self.create_text(
                (x0 + x1) // 2,
                h // 2 + 1,
                text=label,
                fill=cor_txt,
                font=ThemeConfig.FONT_LABEL
            )

    def _on_click(self, event):
        w = max(1, self.winfo_width())
        idx = int((event.x / w) * len(self.options))
        idx = max(0, min(len(self.options) - 1, idx))
        novo_valor = self.options[idx][0]
        if self.variable.get() != novo_valor:
            self.variable.set(novo_valor)
            if self.command:
                self.command()


class StudioTimelineScrubber(tk.Canvas):
    """Barra de tempo de precisão com marcadores visuais de corte (IN/OUT) e playhead."""

    def __init__(self, parent, on_seek_start, on_seek_release, height=24):
        super().__init__(
            parent,
            height=height,
            bg=ThemeConfig.BG_SURFACE,
            bd=0,
            highlightthickness=0,
            cursor="hand2"
        )
        self.on_seek_start = on_seek_start
        self.on_seek_release = on_seek_release
        self.duration = 100.0
        self.position = 0.0
        self.trim_in = 0.0
        self.trim_out = 0.0

        self.bind("<Configure>", self._redraw)
        self.bind("<ButtonPress-1>", self._press)
        self.bind("<B1-Motion>", self._drag)
        self.bind("<ButtonRelease-1>", self._release)

    def set_range(self, duration: float):
        self.duration = max(0.1, float(duration))
        self._redraw()

    def set_position(self, pos: float):
        self.position = max(0.0, min(self.duration, float(pos)))
        self._redraw()

    def set_trim_markers(self, trim_in: float, trim_out: float):
        self.trim_in = max(0.0, float(trim_in))
        self.trim_out = max(0.0, float(trim_out))
        self._redraw()

    def _x_to_sec(self, x: int) -> float:
        pad = 8
        w = max(1, self.winfo_width() - pad * 2)
        ratio = max(0.0, min(1.0, (x - pad) / w))
        return ratio * self.duration

    def _press(self, event):
        if self.on_seek_start:
            self.on_seek_start()
        self.position = self._x_to_sec(event.x)
        self._redraw()

    def _drag(self, event):
        self.position = self._x_to_sec(event.x)
        self._redraw()

    def _release(self, event):
        self.position = self._x_to_sec(event.x)
        self._redraw()
        if self.on_seek_release:
            self.on_seek_release(self.position)

    def _redraw(self, event=None):
        self.delete("all")
        w = max(20, self.winfo_width())
        h = max(16, self.winfo_height())
        cy = h // 2
        pad = 8
        track_w = max(1, w - pad * 2)

        self.create_rectangle(pad, cy - 2, w - pad, cy + 2, fill=ThemeConfig.BG_MAIN, outline=ThemeConfig.DIVIDER)

        for i in range(11):
            tx = pad + int((i / 10.0) * track_w)
            self.create_line(tx, cy + 4, tx, cy + 7, fill=ThemeConfig.DIVIDER)

        if self.duration > 0.1 and self.trim_out > self.trim_in:
            x_in = pad + int(min(1.0, self.trim_in / self.duration) * track_w)
            x_out = pad + int(min(1.0, self.trim_out / self.duration) * track_w)
            self.create_line(x_in, 2, x_in, h - 2, fill=ThemeConfig.TEXT_SECONDARY)
            self.create_line(x_out, 2, x_out, h - 2, fill=ThemeConfig.TEXT_SECONDARY)

        ratio = 0.0 if self.duration <= 0 else min(1.0, max(0.0, self.position / self.duration))
        px = pad + int(ratio * track_w)

        if px > pad:
            self.create_rectangle(pad + 1, cy - 1, px, cy + 1, fill=ThemeConfig.ACCENT, outline="")

        self.create_rectangle(px - 2, 3, px + 2, h - 3, fill=ThemeConfig.TEXT_PRIMARY, outline="")


class StudioGainFader(tk.Canvas):
    """Fader de ganho horizontal (0% a 800%) com marcação de ganho unitário (100% / 0dB)."""

    def __init__(self, parent, variable: tk.DoubleVar, command=None, width=150, height=24):
        super().__init__(
            parent,
            width=width,
            height=height,
            bg=ThemeConfig.BG_SURFACE,
            bd=0,
            highlightthickness=0,
            cursor="hand2"
        )
        self.variable = variable
        self.command = command
        self._width = width
        self._height = height

        self.variable.trace_add("write", lambda *_: self._redraw())
        self.bind("<Configure>", self._redraw)
        self.bind("<ButtonPress-1>", self._interact)
        self.bind("<B1-Motion>", self._interact)

    def _interact(self, event):
        pad = 6
        w = max(1, self.winfo_width() - pad * 2)
        ratio = max(0.0, min(1.0, (event.x - pad) / w))
        if ratio <= 0.35:
            val = (ratio / 0.35) * 100.0
        else:
            val = 100.0 + ((ratio - 0.35) / 0.65) * 700.0
        val = round(val)
        self.variable.set(val)
        if self.command:
            self.command(val)

    def _val_to_ratio(self, val: float) -> float:
        val = max(0.0, min(800.0, val))
        if val <= 100.0:
            return (val / 100.0) * 0.35
        return 0.35 + ((val - 100.0) / 700.0) * 0.65

    def _redraw(self, event=None):
        self.delete("all")
        w = max(20, self.winfo_width() if self.winfo_width() > 1 else self._width)
        h = max(16, self.winfo_height() if self.winfo_height() > 1 else self._height)
        cy = h // 2
        pad = 6
        track_w = max(1, w - pad * 2)

        self.create_rectangle(pad, cy - 2, w - pad, cy + 2, fill=ThemeConfig.BG_MAIN, outline=ThemeConfig.DIVIDER)

        ux = pad + int(0.35 * track_w)
        self.create_line(ux, 2, ux, h - 2, fill=ThemeConfig.TEXT_SECONDARY)

        val = float(self.variable.get())
        ratio = self._val_to_ratio(val)
        fx = pad + int(ratio * track_w)

        cor_barra = ThemeConfig.ACCENT if val > 100.0 else ThemeConfig.TEXT_PRIMARY
        if fx > pad:
            self.create_rectangle(pad + 1, cy - 1, fx, cy + 1, fill=cor_barra, outline="")

        self.create_rectangle(
            fx - 3, 4, fx + 3, h - 4,
            fill=ThemeConfig.ACCENT if val > 100.0 else ThemeConfig.TEXT_PRIMARY,
            outline=ThemeConfig.BG_MAIN
        )


# ==============================================================================
# 3. MOTOR FUNCIONAL DE ÁUDIO E SERVIÇOS (SEPARADO DA INTERFACE)
# ==============================================================================
class SoundboardEngine:
    """
    Camada lógica responsável pelo processamento de áudio, roteamento de placas de som,
    injeção de microfone, corte de WAV, persistência de configurações e API HTTP.
    """

    def __init__(self):
        self.preferencias_globais = self.carregar_preferencias_globais()
        self.pasta_atual = self.preferencias_globais.get("pasta_audios", PASTA_PADRAO_AUDIOS)
        self.arquivo_config = os.path.join(self.pasta_atual, "cuepad.config")
        self.arquivos_audio = {}  # {nome_arquivo: caminho_completo}
        self.duracoes_cache = {}  # {caminho_completo: duracao_em_segundos}
        self.duracoes_persistidas = {}  # {nome_arquivo: duracao_em_segundos}
        self.playlists = {PLAYLIST_TODOS: [], PLAYLIST_FAVORITOS: []}
        self.hotkeys_audios = {}  # {tecla_nome: nome_arquivo}

        self.audio_selecionado = None
        self.esta_pausado = False
        self.esta_tocando = False
        self.offset_segundo = 0.0
        self.duracao_atual = 0.0
        self.usando_audio_estourado = False

        # Pool rotativo de 4 arquivos temporários para eliminar conflitos WinError 32
        self._indice_temp = 0
        self.arquivos_temp_pool = [
            os.path.join(tempfile.gettempdir(), f"cuepad_proc_{i}.wav")
            for i in range(4)
        ]
        self.arquivo_temp_processado = self.arquivos_temp_pool[0]

        # Streams paralelos (Fone simultâneo + Injeção de Mic)
        self.stream_mic_injecao = None
        self.thread_fone_simultaneo = None
        self._evento_parar_fone_atual = None

        self.garantir_pasta_inicial()
        self.carregar_configuracoes()

        pygame.init()
        self.dispositivos_saida = self.obter_dispositivos_saida()
        self.dispositivos_entrada = self.obter_dispositivos_entrada()

        disp_call_salvo = self.preferencias_globais.get("dispositivo_call")
        self.dispositivo_call = (
            disp_call_salvo if disp_call_salvo in self.dispositivos_saida else self.escolher_dispositivo_call()
        )

        disp_fone_salvo = self.preferencias_globais.get("dispositivo_fone")
        self.dispositivo_fone = (
            disp_fone_salvo if disp_fone_salvo in self.dispositivos_saida else self.escolher_dispositivo_fone()
        )

        disp_mic_salvo = self.preferencias_globais.get("dispositivo_mic")
        if disp_mic_salvo in self.dispositivos_entrada:
            self.dispositivo_mic = disp_mic_salvo
        else:
            self.dispositivo_mic = self.dispositivos_entrada[0] if self.dispositivos_entrada else "Padrão do Sistema"

        self.dispositivo_mixer_ativo = None
        self.inicializar_mixer(self.dispositivo_call)

    @staticmethod
    def carregar_preferencias_globais() -> dict:
        """Lê as preferências em AppData\\Roaming\\CuePad\\settings.config (com migração automática do legado)."""
        for caminho in (ARQUIVO_PREFERENCIAS_GLOBAIS, ARQUIVO_PREFERENCIAS_LEGADO):
            if os.path.exists(caminho):
                try:
                    with open(caminho, "r", encoding="utf-8") as f:
                        dados = json.load(f)
                        if isinstance(dados, dict):
                            return dados
                except Exception:
                    pass
        return {}

    def salvar_preferencias_globais(self, dados: dict):
        """Salva preferências globais em AppData\\Roaming\\CuePad\\settings.config."""
        try:
            os.makedirs(PASTA_APP_DATA, exist_ok=True)
            self.preferencias_globais.update(dados)
            with open(ARQUIVO_PREFERENCIAS_GLOBAIS, "w", encoding="utf-8") as f:
                json.dump(self.preferencias_globais, f, ensure_ascii=False, indent=2)
        except Exception as erro:
            print(f"Aviso ao salvar settings.config: {erro}")

    def garantir_pasta_inicial(self):
        try:
            os.makedirs(PASTA_APP_DATA, exist_ok=True)
            if not os.path.exists(self.pasta_atual):
                os.makedirs(self.pasta_atual, exist_ok=True)
        except Exception as erro:
            print(f"Aviso ao criar pasta padrão: {erro}")

    def carregar_configuracoes(self):
        """Carrega playlists, hotkeys e cache de durações da pasta de áudios (suporta cuepad.config e legados)."""
        self.arquivo_config = os.path.join(self.pasta_atual, "cuepad.config")
        legado_1 = os.path.join(self.pasta_atual, "soundboard.config")
        legado_2 = os.path.join(self.pasta_atual, "soundboard_config.json")

        alvo_leitura = self.arquivo_config
        if not os.path.exists(alvo_leitura):
            if os.path.exists(legado_1):
                alvo_leitura = legado_1
            elif os.path.exists(legado_2):
                alvo_leitura = legado_2

        self.playlists = {PLAYLIST_TODOS: [], PLAYLIST_FAVORITOS: []}
        self.hotkeys_audios = {}
        self.duracoes_persistidas = {}

        if os.path.exists(alvo_leitura):
            try:
                with open(alvo_leitura, "r", encoding="utf-8") as f:
                    dados = json.load(f)
                    raw_pl = dados.get("playlists", {})
                    for k, lista in raw_pl.items():
                        k_limpo = k.replace("📂 ", "").replace("⭐ ", "").replace("🎵 ", "").strip()
                        if k_limpo.upper() == "TODOS":
                            self.playlists[PLAYLIST_TODOS] = lista
                        elif k_limpo.upper() == "FAVORITOS":
                            self.playlists[PLAYLIST_FAVORITOS] = lista
                        else:
                            self.playlists[k_limpo.upper()] = lista
                    self.hotkeys_audios = dados.get("hotkeys", {})
                    self.duracoes_persistidas = dados.get("durations", {})
            except Exception:
                pass

    def salvar_configuracoes(self):
        self.arquivo_config = os.path.join(self.pasta_atual, "cuepad.config")
        try:
            dados = {
                "playlists": self.playlists,
                "hotkeys": self.hotkeys_audios,
                "durations": self.duracoes_persistidas,
            }
            with open(self.arquivo_config, "w", encoding="utf-8") as f:
                json.dump(dados, f, ensure_ascii=False, indent=2)
        except Exception as erro:
            print(f"Erro ao salvar configurações: {erro}")

    def obter_dispositivos_saida(self) -> list:
        try:
            dispositivos = list(sdl2_audio.get_audio_device_names(False))
            return dispositivos if dispositivos else ["Padrão do Sistema"]
        except Exception:
            return ["Padrão do Sistema"]

    def obter_dispositivos_entrada(self) -> list:
        try:
            dispositivos = list(sdl2_audio.get_audio_device_names(True))
            return dispositivos if dispositivos else ["Padrão do Sistema"]
        except Exception:
            return ["Padrão do Sistema"]

    def escolher_dispositivo_call(self) -> str:
        for disp in self.dispositivos_saida:
            if "cable input" in disp.lower() or "vb-audio" in disp.lower():
                return disp
        return self.dispositivos_saida[0]

    def escolher_dispositivo_fone(self) -> str:
        for disp in self.dispositivos_saida:
            if "cable" not in disp.lower() and "vb-audio" not in disp.lower():
                return disp
        return self.dispositivos_saida[0]

    def inicializar_mixer(self, nome_dispositivo: str):
        if self.dispositivo_mixer_ativo == nome_dispositivo and pygame.mixer.get_init():
            return
        try:
            if pygame.mixer.get_init():
                pygame.mixer.quit()

            if nome_dispositivo == "Padrão do Sistema":
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=1024)
            else:
                pygame.mixer.init(
                    frequency=44100,
                    size=-16,
                    channels=2,
                    buffer=1024,
                    devicename=nome_dispositivo
                )
            self.dispositivo_mixer_ativo = nome_dispositivo
        except Exception as erro:
            print(f"Erro ao iniciar dispositivo '{nome_dispositivo}': {erro}")
            pygame.mixer.init()
            self.dispositivo_mixer_ativo = "Padrão do Sistema"

    def escanear_pasta_audios(self, caminho_pasta: str) -> tuple:
        if caminho_pasta:
            self.pasta_atual = caminho_pasta
        self.arquivos_audio.clear()

        if not os.path.exists(self.pasta_atual):
            return False, f"DIRETÓRIO NÃO ENCONTRADO: {self.pasta_atual}"

        try:
            nomes_arquivos = sorted(os.listdir(self.pasta_atual), key=lambda s: s.lower())
        except Exception as erro:
            return False, f"ERRO DE LEITURA: {erro}"

        for arquivo in nomes_arquivos:
            if arquivo.lower().endswith(FORMATOS_SUPORTADOS):
                caminho_completo = os.path.join(self.pasta_atual, arquivo)
                if os.path.isfile(caminho_completo):
                    self.arquivos_audio[arquivo] = caminho_completo

        return True, f"{len(self.arquivos_audio)} ARQUIVO(S) CARREGADO(S)"

    def obter_duracao_audio(self, caminho: str, permitir_decodificar: bool = True) -> float:
        """
        Retorna a duração do áudio em segundos.
        Usa cache em memória + cache persistido em cuepad.config para não travar a interface em pastas grandes.
        """
        if caminho in self.duracoes_cache:
            return self.duracoes_cache[caminho]

        nome_arq = os.path.basename(caminho)
        if nome_arq in self.duracoes_persistidas:
            dur = float(self.duracoes_persistidas[nome_arq])
            self.duracoes_cache[caminho] = dur
            return dur

        try:
            if caminho.lower().endswith(".wav"):
                with wave.open(caminho, "rb") as wf:
                    taxa = wf.getframerate()
                    if taxa > 0:
                        duracao = float(wf.getnframes()) / float(taxa)
                        self.duracoes_cache[caminho] = duracao
                        self.duracoes_persistidas[nome_arq] = round(duracao, 2)
                        return duracao

            if not permitir_decodificar:
                return 0.0

            som_temp = pygame.mixer.Sound(caminho)
            duracao = float(som_temp.get_length())
            self.duracoes_cache[caminho] = duracao
            self.duracoes_persistidas[nome_arq] = round(duracao, 2)
            return duracao
        except Exception:
            self.duracoes_cache[caminho] = 0.0
            return 0.0

    def gerar_wav_processado(
        self,
        caminho_original: str,
        porcentagem_vol: float,
        normalizar: bool,
        segundo_inicio: float = 0.0
    ) -> str:
        """
        Processa normalização de pico, ganho/distorção PCM e recorte de segundo inicial.
        Usa pool rotativo de 4 arquivos temporários para evitar bloqueios WinError 32.
        """
        som = pygame.mixer.Sound(caminho_original)
        raw_bytes = som.get_raw()

        init_info = pygame.mixer.get_init()
        frequencia = init_info[0] if init_info else 44100
        formato = init_info[1] if init_info else -16
        canais = init_info[2] if init_info else 2
        largura_bytes = abs(formato) // 8
        bytes_por_frame = max(1, canais * largura_bytes)

        sobra = len(raw_bytes) % bytes_por_frame
        if sobra:
            raw_bytes = raw_bytes[:-sobra]

        if segundo_inicio > 0.0:
            byte_offset = int(segundo_inicio * frequencia) * bytes_por_frame
            if 0 < byte_offset < len(raw_bytes):
                raw_bytes = raw_bytes[byte_offset:]

        fator_normalizacao = 1.0
        if normalizar and len(raw_bytes) >= largura_bytes:
            try:
                if np is not None and largura_bytes == 2:
                    arr_pico = np.frombuffer(raw_bytes, dtype=np.int16)
                    pico = int(np.max(np.abs(arr_pico))) if arr_pico.size > 0 else 1
                elif audioop is not None:
                    pico = max(1, audioop.max(raw_bytes, largura_bytes))
                else:
                    amostras_pico = array.array("h", raw_bytes)
                    passo = max(1, len(amostras_pico) // 5000)
                    pico = max(1, max(abs(x) for x in amostras_pico[::passo]))
                fator_normalizacao = min(6.0, 28000.0 / float(max(1, pico)))
            except Exception:
                fator_normalizacao = 1.0

        if porcentagem_vol > 100.0:
            fator_ganho = fator_normalizacao * (1.0 + ((porcentagem_vol - 100.0) / 100.0) * 2.5)
        else:
            fator_ganho = fator_normalizacao

        if abs(fator_ganho - 1.0) > 0.02 and len(raw_bytes) >= largura_bytes:
            if np is not None and largura_bytes == 2:
                amostras_np = np.frombuffer(raw_bytes, dtype=np.int16).astype(np.float32)
                amostras_np *= fator_ganho
                np.clip(amostras_np, -32768, 32767, out=amostras_np)
                raw_bytes = amostras_np.astype(np.int16).tobytes()
            elif audioop is not None:
                raw_bytes = audioop.mul(raw_bytes, largura_bytes, fator_ganho)
            elif largura_bytes == 2:
                amostras = array.array("h", raw_bytes)
                for i in range(len(amostras)):
                    val = int(amostras[i] * fator_ganho)
                    amostras[i] = 32767 if val > 32767 else (-32768 if val < -32768 else val)
                raw_bytes = amostras.tobytes()

        for tentativa in range(len(self.arquivos_temp_pool)):
            self._indice_temp = (self._indice_temp + 1) % len(self.arquivos_temp_pool)
            caminho_temp = self.arquivos_temp_pool[self._indice_temp]
            try:
                with wave.open(caminho_temp, "wb") as wf:
                    wf.setnchannels(canais)
                    wf.setsampwidth(largura_bytes)
                    wf.setframerate(frequencia)
                    wf.writeframes(raw_bytes)
                self.arquivo_temp_processado = caminho_temp
                break
            except PermissionError:
                continue

        return self.arquivo_temp_processado

    def encontrar_indice_sounddevice(self, nome_parcial: str, entrada: bool = False):
        if not SOUNDDEVICE_DISPONIVEL:
            return None
        try:
            dispositivos = sd.query_devices()
            nome_busca = nome_parcial.lower()[:18]
            for idx, d in enumerate(dispositivos):
                if entrada and d["max_input_channels"] > 0:
                    if nome_busca in d["name"].lower():
                        return idx
                elif not entrada and d["max_output_channels"] > 0:
                    if nome_busca in d["name"].lower():
                        return idx
        except Exception:
            pass
        return None

    def iniciar_reproducao_fone_simultaneo(self, caminho_wav: str, disp_fone: str, segundo_inicio: float, vol_atual: float):
        """Reproduz o áudio paralelamente no fone usando evento isolado por thread (sem condição de corrida)."""
        if not SOUNDDEVICE_DISPONIVEL:
            return
        self.parar_fone_simultaneo()
        idx_fone = self.encontrar_indice_sounddevice(disp_fone, entrada=False)
        stop_event = threading.Event()
        self._evento_parar_fone_atual = stop_event

        def _worker(ev_parar: threading.Event):
            try:
                with wave.open(caminho_wav, "rb") as wf:
                    taxa = wf.getframerate()
                    canais = wf.getnchannels()
                    frame_inicial = int(segundo_inicio * taxa)
                    if 0 < frame_inicial < wf.getnframes():
                        wf.setpos(frame_inicial)
                    bloco = 2048
                    escala_vol = 1.0 if vol_atual > 100.0 else (vol_atual / 100.0)
                    with sd.OutputStream(samplerate=taxa, channels=canais, dtype="int16", device=idx_fone) as stream:
                        while not ev_parar.is_set():
                            if self.esta_pausado:
                                sd.sleep(45)
                                continue
                            dados = wf.readframes(bloco)
                            if not dados:
                                break
                            arr = np.frombuffer(dados, dtype=np.int16)
                            if escala_vol < 0.999:
                                arr = (arr * escala_vol).astype(np.int16)
                            if canais > 1:
                                total_amostras = (arr.size // canais) * canais
                                arr = arr[:total_amostras].reshape(-1, canais)
                            stream.write(arr)
            except Exception as erro:
                print(f"Aviso na reprodução simultânea do fone: {erro}")

        self.thread_fone_simultaneo = threading.Thread(target=_worker, args=(stop_event,), daemon=True)
        self.thread_fone_simultaneo.start()

    def parar_fone_simultaneo(self):
        if self._evento_parar_fone_atual is not None:
            self._evento_parar_fone_atual.set()
            self._evento_parar_fone_atual = None
        if self.thread_fone_simultaneo is not None and self.thread_fone_simultaneo.is_alive():
            try:
                self.thread_fone_simultaneo.join(timeout=0.10)
            except Exception:
                pass
        self.thread_fone_simultaneo = None

    def configurar_injecao_mic(self, ativar: bool, disp_mic: str, disp_call: str, fn_block_voice_ativo) -> tuple:
        if self.stream_mic_injecao is not None:
            try:
                self.stream_mic_injecao.stop()
                self.stream_mic_injecao.close()
            except Exception:
                pass
            self.stream_mic_injecao = None

        if not ativar:
            return True, "INJEÇÃO DE MICROFONE DESATIVADA"

        if not SOUNDDEVICE_DISPONIVEL:
            return False, "PACOTE SOUNDDEVICE AUSENTE"

        idx_mic = self.encontrar_indice_sounddevice(disp_mic, entrada=True)
        idx_call = self.encontrar_indice_sounddevice(disp_call, entrada=False)

        taxa_padrao = 44100
        canais_tentativa = [1, 2]
        try:
            if idx_mic is not None:
                info_mic = sd.query_devices(idx_mic, "input")
                taxa_padrao = int(info_mic.get("default_samplerate", 44100))
        except Exception:
            taxa_padrao = 44100

        def _callback_mic(indata, outdata, frames, time_info, status):
            if fn_block_voice_ativo() and self.esta_tocando and not self.esta_pausado:
                outdata.fill(0)
            else:
                outdata[:] = indata

        ultimo_erro = None
        for ch in canais_tentativa:
            try:
                self.stream_mic_injecao = sd.Stream(
                    device=(idx_mic, idx_call),
                    samplerate=taxa_padrao,
                    channels=ch,
                    dtype="int16",
                    callback=_callback_mic
                )
                self.stream_mic_injecao.start()
                return True, "MICROFONE INJETADO NO CABO VIRTUAL"
            except Exception as erro:
                ultimo_erro = erro

        return False, f"ERRO DE INJEÇÃO: {ultimo_erro}"

    def exportar_corte_wav(self, caminho_orig: str, caminho_destino: str, seg_ini: float, seg_fim: float):
        som = pygame.mixer.Sound(caminho_orig)
        raw_bytes = som.get_raw()

        init_info = pygame.mixer.get_init()
        taxa = init_info[0] if init_info else 44100
        formato = init_info[1] if init_info else -16
        canais = init_info[2] if init_info else 2
        largura_bytes = abs(formato) // 8
        bytes_por_frame = canais * largura_bytes

        byte_inicio = int(seg_ini * taxa) * bytes_por_frame
        byte_fim = int(seg_fim * taxa) * bytes_por_frame
        fatia_bytes = raw_bytes[byte_inicio:byte_fim]

        with wave.open(caminho_destino, "wb") as wf:
            wf.setnchannels(canais)
            wf.setsampwidth(largura_bytes)
            wf.setframerate(taxa)
            wf.writeframes(fatia_bytes)

    @staticmethod
    def obter_ip_local() -> str:
        ips = SoundboardEngine.obter_todos_ips_locais()
        return ips[0] if ips else "127.0.0.1"

    @staticmethod
    def obter_todos_ips_locais() -> list:
        """Retorna todos os IPs IPv4 da máquina, priorizando a rede Wi-Fi/LAN real (192.168.x.x / 10.x.x.x)."""
        ips_encontrados = []
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip_principal = s.getsockname()[0]
            s.close()
            if ip_principal and not ip_principal.startswith("127."):
                ips_encontrados.append(ip_principal)
        except Exception:
            pass

        try:
            infos = socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)
            for info in infos:
                ip = info[4][0]
                if ip and not ip.startswith("127.") and not ip.startswith("169.254.") and ip not in ips_encontrados:
                    ips_encontrados.append(ip)
        except Exception:
            pass

        ips_encontrados.sort(key=lambda x: (0 if x.startswith("192.168.") else (1 if x.startswith("10.") else 2)))
        return ips_encontrados if ips_encontrados else ["127.0.0.1"]

    @staticmethod
    def liberar_porta_firewall(porta: int = PORTA_API_REMOTA) -> bool:
        """Solicita permissão de Administrador no Windows para liberar a porta TCP no Firewall."""
        if not hasattr(ctypes, "windll"):
            return False
        try:
            parametros = (
                f'advfirewall firewall add rule name="CuePad Soundboard Remote ({porta})" '
                f'dir=in action=allow protocol=TCP localport={porta} profile=any'
            )
            ret = ctypes.windll.shell32.ShellExecuteW(
                None, "runas", "netsh", parametros, None, 0
            )
            return int(ret) > 32
        except Exception:
            return False

    def encerrar(self):
        self.parar_fone_simultaneo()
        try:
            if self.stream_mic_injecao is not None:
                self.stream_mic_injecao.stop()
                self.stream_mic_injecao.close()
            pygame.mixer.music.stop()
            if hasattr(pygame.mixer.music, "unload"):
                pygame.mixer.music.unload()
            pygame.mixer.quit()
            pygame.quit()
            for caminho_tmp in self.arquivos_temp_pool:
                if os.path.exists(caminho_tmp):
                    try:
                        os.remove(caminho_tmp)
                    except Exception:
                        pass
        except Exception:
            pass


# ==============================================================================
# 4. INTERFACE GRÁFICA DE ESTÚDIO (CUEPAD)
# ==============================================================================
class CuePadApp:
    """
    Controlador principal de interface do CuePad Soundboard.
    """

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.geometry("1100x730")
        self.root.minsize(960, 630)
        self.root.configure(bg=ThemeConfig.BG_MAIN)
        self._icone_img_ref = None
        self._carregar_icone_janela()

        self.style = ThemeConfig.aplicar_estilos_ttk(self.root)
        self.engine = SoundboardEngine()

        self.arrastando_slider = False
        self.timer_reaplicar_boost = None
        self.estado_teclas_anterior = set()
        self.servidor_http = None
        self.modo_preview_ativo = False

        prefs = self.engine.preferencias_globais
        self.idioma = prefs.get("idioma", "pt")
        if self.idioma not in TRADUCOES:
            self.idioma = "pt"

        self.root.title(f"{self._t('app_title')} — {self._t('app_subtitle')}")

        modo_padrao = "ambos" if SOUNDDEVICE_DISPONIVEL else "call"
        modo_salvo = prefs.get("modo_saida", modo_padrao)
        if modo_salvo == "ambos" and not SOUNDDEVICE_DISPONIVEL:
            modo_salvo = "call"

        self.var_modo_saida = tk.StringVar(value=modo_salvo)
        self.var_injetar_mic = tk.BooleanVar(value=bool(prefs.get("injetar_mic", False)) and SOUNDDEVICE_DISPONIVEL)
        self.var_block_voice = tk.BooleanVar(value=bool(prefs.get("block_voice", True)))
        self.var_caminho_pasta = tk.StringVar(value=self.engine.pasta_atual)
        self.var_busca = tk.StringVar()
        self.var_playlist_atual = tk.StringVar(value=PLAYLIST_TODOS)
        self.var_hotkeys_ativas = tk.BooleanVar(value=bool(prefs.get("hotkeys_ativas", True)))
        self.var_normalizar = tk.BooleanVar(value=bool(prefs.get("normalizar", False)))
        self.var_segundo_inicio = tk.StringVar(value="0.0")
        self.var_segundo_fim = tk.StringVar(value="0.0")
        self.var_volume = tk.DoubleVar(value=float(prefs.get("volume", 80.0)))

        self._construir_interface()
        self._construir_menu_contexto_tabela()

        self._ao_mudar_volume(self.var_volume.get())
        if self.var_injetar_mic.get():
            self._alternar_injecao_microfone()

        self.carregar_lista_audios()

        self._iniciar_servidor_remoto()
        self._atualizar_progresso()
        self._monitorar_hotkeys_globais()

        if not prefs.get("tutorial_concluido", False):
            self.root.after(350, self.abrir_tutorial)

        self.root.protocol("WM_DELETE_WINDOW", self._ao_fechar)

    def _carregar_icone_janela(self):
        """
        Registra o AppUserModelID no Windows (para exibir o ícone próprio na Barra de Tarefas)
        e carrega o icone.ico tanto na barra de título quanto em janelas filhas.
        """
        if hasattr(ctypes, "windll"):
            try:
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID_WINDOWS)
            except Exception:
                pass

        try:
            possiveis_pastas = [
                getattr(sys, "_MEIPASS", ""),
                os.path.dirname(os.path.abspath(sys.argv[0])),
                os.path.dirname(os.path.abspath(__file__)),
            ]
            caminho_ico = None
            for pasta in possiveis_pastas:
                if pasta:
                    cand = os.path.join(pasta, "icone.ico")
                    if os.path.exists(cand):
                        caminho_ico = cand
                        break

            if not caminho_ico:
                return

            try:
                self.root.iconbitmap(default=caminho_ico)
            except Exception:
                self.root.iconbitmap(caminho_ico)

            try:
                from PIL import Image, ImageTk
                img = Image.open(caminho_ico)
                self._icone_img_ref = ImageTk.PhotoImage(img)
                self.root.iconphoto(True, self._icone_img_ref)
            except Exception:
                pass
        except Exception:
            pass

    def _t(self, chave: str) -> str:
        return TRADUCOES.get(self.idioma, TRADUCOES["pt"]).get(chave, chave)

    def alternar_idioma(self):
        self.idioma = "en" if self.idioma == "pt" else "pt"
        self._aplicar_traducao_interface()
        self._persistir_preferencias_usuario()

    def _aplicar_traducao_interface(self):
        self.root.title(f"{self._t('app_title')} — {self._t('app_subtitle')}")
        self.lbl_app_title.config(text=self._t("app_title"))
        self.lbl_app_subtitle.config(text=self._t("app_subtitle"))
        self.btn_idioma.set_text("🇧🇷 PT" if self.idioma == "pt" else "🇺🇸 EN")
        self.btn_guia.set_text(self._t("btn_guide"))
        self.btn_remote.set_text(self._t("btn_remote"))
        self.btn_win_mic.set_text(self._t("btn_win_mic"))

        self.hdr_outputs.set_title(self._t("sec_outputs"))
        self.lbl_output_mode.config(text=self._t("lbl_output_mode"))
        self.seg_modo.set_options([
            ("fone", self._t("mode_fone")),
            ("call", self._t("mode_call")),
            ("ambos", self._t("mode_ambos")),
        ])
        self.lbl_call_out.config(text=self._t("lbl_call_out"))
        self.lbl_fone_out.config(text=self._t("lbl_fone_out"))

        self.hdr_mic.set_title(self._t("sec_mic"))
        self.lbl_mic_in.config(text=self._t("lbl_mic_in"))
        self.tgl_inject_mic.set_text(self._t("chk_inject_mic"))
        self.tgl_block_voice.set_text(self._t("chk_block_voice"))

        self.hdr_hotkeys.set_title(self._t("sec_hotkeys"))
        self.tgl_hotkeys.set_text(self._t("chk_hotkeys"))
        self.btn_bind_key.set_text(self._t("btn_bind_key"))

        self.hdr_folder.set_title(self._t("sec_folder"))
        self.btn_browse.set_text(self._t("btn_browse"))
        self.btn_rescan.set_text(self._t("btn_rescan"))

        self.lbl_search.config(text=self._t("lbl_search"))
        self.lbl_enter_hint.config(text=self._t("lbl_enter_hint"))
        self.lbl_collection.config(text=self._t("lbl_collection"))
        self.btn_add_list.set_text(self._t("btn_add_list"))
        self.btn_add_track.set_text(self._t("btn_add_track"))
        self.btn_rem_track.set_text(self._t("btn_rem_track"))

        self.tabela_audios.heading("hotkey", text=self._t("col_key"), anchor=tk.W)
        self.tabela_audios.heading("nome", text=self._t("col_name"), anchor=tk.W)
        self.tabela_audios.heading("formato", text=self._t("col_fmt"), anchor=tk.CENTER)
        self.tabela_audios.heading("duracao", text=self._t("col_dur"), anchor=tk.E)

        self.lbl_selected_hdr.config(text=self._t("lbl_selected"))
        if not self.engine.audio_selecionado:
            self.lbl_faixa_ativa.config(text=self._t("lbl_no_track"))
        self.tgl_normalize.set_text(self._t("chk_normalize"))

        self.btn_tocar.set_text(self._t("btn_play"))
        self.btn_preview.set_text(self._t("btn_preview"))
        self.btn_pausar.set_text(self._t("btn_resume") if self.engine.esta_pausado else self._t("btn_pause"))
        self.btn_parar.set_text(self._t("btn_stop"))

        self.lbl_in.config(text=self._t("lbl_in"))
        self.lbl_out.config(text=self._t("lbl_out"))
        self.btn_locate.set_text(self._t("btn_locate"))
        self.btn_trim.set_text(self._t("btn_trim"))

        self._construir_menu_contexto_tabela()
        self._ao_mudar_volume(self.var_volume.get())
        self.filtrar_tabela_audios()

    # --------------------------------------------------------------------------
    # CONSTRUÇÃO DO LAYOUT ASSIMÉTRICO DE ESTÚDIO
    # --------------------------------------------------------------------------
    def _construir_interface(self):
        self._construir_barra_superior()
        HairlineDivider(self.root, orient="horizontal").pack(fill=tk.X)

        corpo = tk.Frame(self.root, bg=ThemeConfig.BG_MAIN)
        corpo.pack(fill=tk.BOTH, expand=True)

        self.sidebar = tk.Frame(
            corpo,
            bg=ThemeConfig.BG_SURFACE,
            width=ThemeConfig.SIDEBAR_WIDTH,
            padx=16,
            pady=14
        )
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        HairlineDivider(corpo, orient="vertical").pack(side=tk.LEFT, fill=tk.Y)

        self.area_principal = tk.Frame(corpo, bg=ThemeConfig.BG_MAIN)
        self.area_principal.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._construir_sidebar_esquerda()
        self._construir_area_principal_direita()

    def _construir_barra_superior(self):
        topbar = tk.Frame(self.root, bg=ThemeConfig.BG_SURFACE, height=42, padx=16)
        topbar.pack(fill=tk.X)
        topbar.pack_propagate(False)

        self.lbl_app_title = tk.Label(
            topbar,
            text=self._t("app_title"),
            bg=ThemeConfig.BG_SURFACE,
            fg=ThemeConfig.TEXT_PRIMARY,
            font=ThemeConfig.FONT_MONO_BOLD
        )
        self.lbl_app_title.pack(side=tk.LEFT)

        self.lbl_app_subtitle = tk.Label(
            topbar,
            text=self._t("app_subtitle"),
            bg=ThemeConfig.BG_SURFACE,
            fg=ThemeConfig.TEXT_SECONDARY,
            font=ThemeConfig.FONT_LABEL,
            padx=8
        )
        self.lbl_app_subtitle.pack(side=tk.LEFT)

        HairlineDivider(topbar, orient="vertical", height=18).pack(side=tk.LEFT, padx=10, pady=12)

        self.led_status = StatusIndicatorLED(topbar, size=8, bg=ThemeConfig.BG_SURFACE)
        self.led_status.pack(side=tk.LEFT, padx=(0, 8))

        self.lbl_status = tk.Label(
            topbar,
            text=self._t("status_ready"),
            bg=ThemeConfig.BG_SURFACE,
            fg=ThemeConfig.TEXT_SECONDARY,
            font=ThemeConfig.FONT_MONO
        )
        self.lbl_status.pack(side=tk.LEFT)

        self.btn_idioma = StudioButton(
            topbar,
            text="🇧🇷 PT" if self.idioma == "pt" else "🇺🇸 EN",
            width=64,
            height=24,
            command=self.alternar_idioma
        )
        self.btn_idioma.pack(side=tk.RIGHT, padx=(6, 0))

        self.btn_guia = StudioButton(
            topbar,
            text=self._t("btn_guide"),
            width=74,
            height=24,
            command=self.abrir_tutorial
        )
        self.btn_guia.pack(side=tk.RIGHT, padx=(6, 0))

        self.btn_remote = StudioButton(
            topbar,
            text=self._t("btn_remote"),
            width=112,
            height=24,
            command=self.mostrar_info_api_remota
        )
        self.btn_remote.pack(side=tk.RIGHT, padx=(6, 0))

        self.btn_win_mic = StudioButton(
            topbar,
            text=self._t("btn_win_mic"),
            width=124,
            height=24,
            command=self.abrir_config_microfone_windows
        )
        self.btn_win_mic.pack(side=tk.RIGHT, padx=(6, 0))

    def _construir_sidebar_esquerda(self):
        # SEÇÃO: SAÍDAS DE ÁUDIO
        sec1 = tk.Frame(self.sidebar, bg=ThemeConfig.BG_SURFACE)
        sec1.pack(fill=tk.X, pady=(0, 20))
        self.hdr_outputs = SectionHeader(sec1, self._t("sec_outputs"))
        self.hdr_outputs.pack(fill=tk.X, pady=(0, 10))

        self.lbl_output_mode = tk.Label(
            sec1, text=self._t("lbl_output_mode"), bg=ThemeConfig.BG_SURFACE,
            fg=ThemeConfig.TEXT_SECONDARY, font=ThemeConfig.FONT_LABEL
        )
        self.lbl_output_mode.pack(anchor="w", pady=(0, 4))

        opcoes_modo = [
            ("fone", self._t("mode_fone")),
            ("call", self._t("mode_call")),
            ("ambos", self._t("mode_ambos"))
        ]
        self.seg_modo = SegmentedBusSelector(
            sec1, opcoes_modo, self.var_modo_saida, command=self._ao_trocar_dispositivo
        )
        self.seg_modo.pack(fill=tk.X, pady=(0, 10))

        self.lbl_call_out = tk.Label(
            sec1, text=self._t("lbl_call_out"), bg=ThemeConfig.BG_SURFACE,
            fg=ThemeConfig.TEXT_SECONDARY, font=ThemeConfig.FONT_LABEL
        )
        self.lbl_call_out.pack(anchor="w", pady=(0, 3))

        self.combo_disp_call = ttk.Combobox(
            sec1, values=self.engine.dispositivos_saida, state="readonly", font=ThemeConfig.FONT_UI
        )
        self.combo_disp_call.set(self.engine.dispositivo_call)
        self.combo_disp_call.pack(fill=tk.X, pady=(0, 8))
        self.combo_disp_call.bind("<<ComboboxSelected>>", self._ao_trocar_dispositivo)

        self.lbl_fone_out = tk.Label(
            sec1, text=self._t("lbl_fone_out"), bg=ThemeConfig.BG_SURFACE,
            fg=ThemeConfig.TEXT_SECONDARY, font=ThemeConfig.FONT_LABEL
        )
        self.lbl_fone_out.pack(anchor="w", pady=(0, 3))

        self.combo_disp_fone = ttk.Combobox(
            sec1, values=self.engine.dispositivos_saida, state="readonly", font=ThemeConfig.FONT_UI
        )
        self.combo_disp_fone.set(self.engine.dispositivo_fone)
        self.combo_disp_fone.pack(fill=tk.X)
        self.combo_disp_fone.bind("<<ComboboxSelected>>", self._ao_trocar_dispositivo)

        # SEÇÃO: SEU MICROFONE
        sec2 = tk.Frame(self.sidebar, bg=ThemeConfig.BG_SURFACE)
        sec2.pack(fill=tk.X, pady=(0, 20))
        self.hdr_mic = SectionHeader(sec2, self._t("sec_mic"))
        self.hdr_mic.pack(fill=tk.X, pady=(0, 10))

        self.lbl_mic_in = tk.Label(
            sec2, text=self._t("lbl_mic_in"), bg=ThemeConfig.BG_SURFACE,
            fg=ThemeConfig.TEXT_SECONDARY, font=ThemeConfig.FONT_LABEL
        )
        self.lbl_mic_in.pack(anchor="w", pady=(0, 3))

        self.combo_disp_mic = ttk.Combobox(
            sec2, values=self.engine.dispositivos_entrada, state="readonly", font=ThemeConfig.FONT_UI
        )
        self.combo_disp_mic.set(self.engine.dispositivo_mic)
        self.combo_disp_mic.pack(fill=tk.X, pady=(0, 8))
        self.combo_disp_mic.bind("<<ComboboxSelected>>", self._ao_trocar_microfone)

        self.tgl_inject_mic = StudioToggle(
            sec2,
            text=self._t("chk_inject_mic"),
            variable=self.var_injetar_mic,
            command=self._alternar_injecao_microfone
        )
        self.tgl_inject_mic.pack(fill=tk.X, pady=(0, 4))

        self.tgl_block_voice = StudioToggle(
            sec2,
            text=self._t("chk_block_voice"),
            variable=self.var_block_voice,
            command=self._persistir_preferencias_usuario
        )
        self.tgl_block_voice.pack(fill=tk.X)

        # SEÇÃO: ATALHOS EM JOGOS
        sec3 = tk.Frame(self.sidebar, bg=ThemeConfig.BG_SURFACE)
        sec3.pack(fill=tk.X, pady=(0, 20))
        self.hdr_hotkeys = SectionHeader(sec3, self._t("sec_hotkeys"))
        self.hdr_hotkeys.pack(fill=tk.X, pady=(0, 10))

        self.tgl_hotkeys = StudioToggle(
            sec3,
            text=self._t("chk_hotkeys"),
            variable=self.var_hotkeys_ativas,
            command=self._persistir_preferencias_usuario
        )
        self.tgl_hotkeys.pack(fill=tk.X, pady=(0, 8))

        self.btn_bind_key = StudioButton(
            sec3,
            text=self._t("btn_bind_key"),
            width=278,
            height=28,
            command=self.definir_hotkey_audio
        )
        self.btn_bind_key.pack(fill=tk.X)

        # SEÇÃO: PASTA DE ÁUDIOS
        sec4 = tk.Frame(self.sidebar, bg=ThemeConfig.BG_SURFACE)
        sec4.pack(fill=tk.X)
        self.hdr_folder = SectionHeader(sec4, self._t("sec_folder"))
        self.hdr_folder.pack(fill=tk.X, pady=(0, 10))

        moldura_pasta = tk.Frame(
            sec4, bg=ThemeConfig.BG_MAIN, highlightbackground=ThemeConfig.DIVIDER, highlightthickness=1
        )
        moldura_pasta.pack(fill=tk.X, pady=(0, 8))

        self.entry_pasta = tk.Entry(
            moldura_pasta,
            textvariable=self.var_caminho_pasta,
            bg=ThemeConfig.BG_MAIN,
            fg=ThemeConfig.TEXT_SECONDARY,
            insertbackground=ThemeConfig.TEXT_PRIMARY,
            relief=tk.FLAT,
            bd=0,
            font=ThemeConfig.FONT_MONO
        )
        self.entry_pasta.pack(fill=tk.X, padx=6, pady=5)
        self.entry_pasta.bind("<Return>", lambda e: self.carregar_lista_audios())

        barra_dir = tk.Frame(sec4, bg=ThemeConfig.BG_SURFACE)
        barra_dir.pack(fill=tk.X)

        self.btn_browse = StudioButton(
            barra_dir, text=self._t("btn_browse"), width=134, height=26, command=self.escolher_nova_pasta
        )
        self.btn_browse.pack(side=tk.LEFT, padx=(0, 8))

        self.btn_rescan = StudioButton(
            barra_dir, text=self._t("btn_rescan"), width=134, height=26, command=self.carregar_lista_audios
        )
        self.btn_rescan.pack(side=tk.LEFT)

    def _construir_area_principal_direita(self):
        # 1. BARRA UNIFICADA DE BUSCA E COLEÇÕES (PLAYLISTS)
        barra_filtro = tk.Frame(self.area_principal, bg=ThemeConfig.BG_MAIN, padx=16, pady=10)
        barra_filtro.pack(fill=tk.X)

        self.lbl_search = tk.Label(
            barra_filtro,
            text=self._t("lbl_search"),
            bg=ThemeConfig.BG_MAIN,
            fg=ThemeConfig.TEXT_SECONDARY,
            font=ThemeConfig.FONT_LABEL
        )
        self.lbl_search.pack(side=tk.LEFT, padx=(0, 8))

        box_busca = tk.Frame(
            barra_filtro,
            bg=ThemeConfig.BG_SURFACE,
            highlightbackground=ThemeConfig.DIVIDER,
            highlightthickness=1
        )
        box_busca.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.var_busca.trace_add("write", lambda *_: self.filtrar_tabela_audios())
        self.entry_busca = tk.Entry(
            box_busca,
            textvariable=self.var_busca,
            bg=ThemeConfig.BG_SURFACE,
            fg=ThemeConfig.TEXT_PRIMARY,
            insertbackground=ThemeConfig.ACCENT,
            relief=tk.FLAT,
            bd=0,
            font=ThemeConfig.FONT_UI
        )
        self.entry_busca.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=8, pady=5)
        self.entry_busca.bind("<Return>", self._ao_dar_enter_na_busca)

        self.lbl_enter_hint = tk.Label(
            box_busca,
            text=self._t("lbl_enter_hint"),
            bg=ThemeConfig.BG_SURFACE,
            fg=ThemeConfig.TEXT_SECONDARY,
            font=ThemeConfig.FONT_LABEL,
            padx=6
        )
        self.lbl_enter_hint.pack(side=tk.RIGHT)

        HairlineDivider(barra_filtro, orient="vertical", height=24).pack(side=tk.LEFT, padx=12)

        self.lbl_collection = tk.Label(
            barra_filtro,
            text=self._t("lbl_collection"),
            bg=ThemeConfig.BG_MAIN,
            fg=ThemeConfig.TEXT_SECONDARY,
            font=ThemeConfig.FONT_LABEL
        )
        self.lbl_collection.pack(side=tk.LEFT, padx=(0, 6))

        self.combo_playlist = ttk.Combobox(
            barra_filtro,
            textvariable=self.var_playlist_atual,
            values=list(self.engine.playlists.keys()),
            state="readonly",
            width=13,
            font=ThemeConfig.FONT_UI
        )
        self.combo_playlist.pack(side=tk.LEFT, padx=(0, 6))
        self.combo_playlist.bind("<<ComboboxSelected>>", lambda e: self.filtrar_tabela_audios())

        self.btn_add_list = StudioButton(
            barra_filtro, text=self._t("btn_add_list"), width=62, height=26, command=self.criar_nova_playlist
        )
        self.btn_add_list.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_add_track = StudioButton(
            barra_filtro, text=self._t("btn_add_track"), width=66, height=26, command=self.adicionar_audio_na_playlist
        )
        self.btn_add_track.pack(side=tk.LEFT, padx=(0, 4))

        self.btn_rem_track = StudioButton(
            barra_filtro, text=self._t("btn_rem_track"), width=74, height=26, command=self.remover_audio_da_playlist
        )
        self.btn_rem_track.pack(side=tk.LEFT)

        self.lbl_contador = tk.Label(
            barra_filtro,
            text="00",
            bg=ThemeConfig.BG_MAIN,
            fg=ThemeConfig.TEXT_SECONDARY,
            font=ThemeConfig.FONT_MONO_BOLD,
            padx=8
        )
        self.lbl_contador.pack(side=tk.RIGHT)

        HairlineDivider(self.area_principal, orient="horizontal").pack(fill=tk.X)

        # 2. TABELA CENTRAL DE ÁUDIOS (TREEVIEW)
        frame_tabela = tk.Frame(self.area_principal, bg=ThemeConfig.BG_MAIN, padx=16, pady=8)
        frame_tabela.pack(fill=tk.BOTH, expand=True)

        colunas = ("hotkey", "nome", "formato", "duracao")
        self.tabela_audios = ttk.Treeview(
            frame_tabela,
            columns=colunas,
            show="headings",
            selectmode="browse"
        )
        self.tabela_audios.heading("hotkey", text=self._t("col_key"), anchor=tk.W)
        self.tabela_audios.heading("nome", text=self._t("col_name"), anchor=tk.W)
        self.tabela_audios.heading("formato", text=self._t("col_fmt"), anchor=tk.CENTER)
        self.tabela_audios.heading("duracao", text=self._t("col_dur"), anchor=tk.E)

        self.tabela_audios.column("hotkey", width=95, stretch=False, anchor=tk.W)
        self.tabela_audios.column("nome", width=440, stretch=True, anchor=tk.W)
        self.tabela_audios.column("formato", width=75, stretch=False, anchor=tk.CENTER)
        self.tabela_audios.column("duracao", width=90, stretch=False, anchor=tk.E)

        scrollbar = ttk.Scrollbar(
            frame_tabela,
            orient=tk.VERTICAL,
            command=self.tabela_audios.yview
        )
        self.tabela_audios.configure(yscrollcommand=scrollbar.set)

        self.tabela_audios.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tabela_audios.bind("<<TreeviewSelect>>", self._ao_selecionar_item)
        self.tabela_audios.bind("<Double-1>", lambda e: self.tocar_audio_selecionado())
        self.tabela_audios.bind("<Return>", lambda e: self.tocar_audio_selecionado())
        self.tabela_audios.bind("<Button-3>", self._exibir_menu_contexto_tabela)

        # 3. DECK INFERIOR DE TRANSPORTE, PREVIEW, CORTE E VOLUME
        HairlineDivider(self.area_principal, orient="horizontal").pack(fill=tk.X)

        deck = tk.Frame(self.area_principal, bg=ThemeConfig.BG_SURFACE, padx=16, pady=14)
        deck.pack(fill=tk.X)

        header_deck = tk.Frame(deck, bg=ThemeConfig.BG_SURFACE)
        header_deck.pack(fill=tk.X, pady=(0, 6))

        self.lbl_selected_hdr = tk.Label(
            header_deck,
            text=self._t("lbl_selected"),
            bg=ThemeConfig.BG_SURFACE,
            fg=ThemeConfig.TEXT_SECONDARY,
            font=ThemeConfig.FONT_LABEL
        )
        self.lbl_selected_hdr.pack(side=tk.LEFT)

        self.lbl_faixa_ativa = tk.Label(
            header_deck,
            text=self._t("lbl_no_track"),
            bg=ThemeConfig.BG_SURFACE,
            fg=ThemeConfig.TEXT_PRIMARY,
            font=ThemeConfig.FONT_MONO_BOLD,
            padx=6
        )
        self.lbl_faixa_ativa.pack(side=tk.LEFT)

        self.tgl_normalize = StudioToggle(
            header_deck,
            text=self._t("chk_normalize"),
            variable=self.var_normalizar,
            command=self._reaplicar_volume_em_execucao
        )
        self.tgl_normalize.pack(side=tk.RIGHT)

        linha_scrubber = tk.Frame(deck, bg=ThemeConfig.BG_SURFACE)
        linha_scrubber.pack(fill=tk.X, pady=(0, 12))

        self.lbl_tempo_atual = tk.Label(
            linha_scrubber,
            text="00:00",
            bg=ThemeConfig.BG_SURFACE,
            fg=ThemeConfig.ACCENT,
            font=ThemeConfig.FONT_TIME
        )
        self.lbl_tempo_atual.pack(side=tk.LEFT)

        self.timeline = StudioTimelineScrubber(
            linha_scrubber,
            on_seek_start=self._ao_iniciar_arraste_tempo,
            on_seek_release=self._ao_soltar_arraste_tempo
        )
        self.timeline.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        self.lbl_tempo_total = tk.Label(
            linha_scrubber,
            text="00:00",
            bg=ThemeConfig.BG_SURFACE,
            fg=ThemeConfig.TEXT_SECONDARY,
            font=ThemeConfig.FONT_TIME
        )
        self.lbl_tempo_total.pack(side=tk.RIGHT)

        HairlineDivider(deck, orient="horizontal").pack(fill=tk.X, pady=(0, 12))

        linha_controles = tk.Frame(deck, bg=ThemeConfig.BG_SURFACE)
        linha_controles.pack(fill=tk.X)

        zona_transporte = tk.Frame(linha_controles, bg=ThemeConfig.BG_SURFACE)
        zona_transporte.pack(side=tk.LEFT)

        self.btn_tocar = StudioButton(
            zona_transporte,
            text=self._t("btn_play"),
            width=64,
            height=28,
            accent=True,
            command=self.tocar_audio_selecionado
        )
        self.btn_tocar.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_preview = StudioButton(
            zona_transporte,
            text=self._t("btn_preview"),
            width=128,
            height=28,
            command=self.tocar_preview_fone
        )
        self.btn_preview.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_pausar = StudioButton(
            zona_transporte,
            text=self._t("btn_pause"),
            width=68,
            height=28,
            command=self.alternar_pausa
        )
        self.btn_pausar.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_parar = StudioButton(
            zona_transporte,
            text=self._t("btn_stop"),
            width=82,
            height=28,
            command=self.parar_audio
        )
        self.btn_parar.pack(side=tk.LEFT)

        HairlineDivider(linha_controles, orient="vertical", height=28).pack(side=tk.LEFT, padx=10)

        zona_trim = tk.Frame(linha_controles, bg=ThemeConfig.BG_SURFACE)
        zona_trim.pack(side=tk.LEFT)

        self.lbl_in = tk.Label(
            zona_trim, text=self._t("lbl_in"), bg=ThemeConfig.BG_SURFACE,
            fg=ThemeConfig.TEXT_SECONDARY, font=ThemeConfig.FONT_LABEL
        )
        self.lbl_in.pack(side=tk.LEFT, padx=(0, 3))

        self.spin_segundo = tk.Spinbox(
            zona_trim,
            from_=0, to=3600, increment=0.5,
            textvariable=self.var_segundo_inicio,
            width=4,
            bg=ThemeConfig.BG_MAIN,
            fg=ThemeConfig.TEXT_PRIMARY,
            insertbackground=ThemeConfig.TEXT_PRIMARY,
            buttonbackground=ThemeConfig.DIVIDER,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=ThemeConfig.DIVIDER,
            font=ThemeConfig.FONT_MONO,
            command=self._atualizar_marcadores_trim
        )
        self.spin_segundo.pack(side=tk.LEFT, ipady=3, padx=(0, 6))
        self.spin_segundo.bind("<KeyRelease>", lambda e: self._atualizar_marcadores_trim())

        self.lbl_out = tk.Label(
            zona_trim, text=self._t("lbl_out"), bg=ThemeConfig.BG_SURFACE,
            fg=ThemeConfig.TEXT_SECONDARY, font=ThemeConfig.FONT_LABEL
        )
        self.lbl_out.pack(side=tk.LEFT, padx=(0, 3))

        self.spin_segundo_fim = tk.Spinbox(
            zona_trim,
            from_=0, to=3600, increment=0.5,
            textvariable=self.var_segundo_fim,
            width=4,
            bg=ThemeConfig.BG_MAIN,
            fg=ThemeConfig.TEXT_PRIMARY,
            insertbackground=ThemeConfig.TEXT_PRIMARY,
            buttonbackground=ThemeConfig.DIVIDER,
            relief=tk.FLAT,
            highlightthickness=1,
            highlightbackground=ThemeConfig.DIVIDER,
            font=ThemeConfig.FONT_MONO,
            command=self._atualizar_marcadores_trim
        )
        self.spin_segundo_fim.pack(side=tk.LEFT, ipady=3, padx=(0, 6))
        self.spin_segundo_fim.bind("<KeyRelease>", lambda e: self._atualizar_marcadores_trim())

        self.btn_locate = StudioButton(
            zona_trim,
            text=self._t("btn_locate"),
            width=66,
            height=28,
            command=self.pular_para_segundo_digitado
        )
        self.btn_locate.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_trim = StudioButton(
            zona_trim,
            text=self._t("btn_trim"),
            width=92,
            height=28,
            command=self.cortar_e_salvar_audio
        )
        self.btn_trim.pack(side=tk.LEFT)

        zona_ganho = tk.Frame(linha_controles, bg=ThemeConfig.BG_SURFACE)
        zona_ganho.pack(side=tk.RIGHT)

        self.btn_estourar = StudioButton(
            zona_ganho,
            text=self._t("btn_overdrive"),
            width=82,
            height=28,
            command=self.alternar_modo_estourado
        )
        self.btn_estourar.pack(side=tk.RIGHT, padx=(6, 0))

        self.fader_vol = StudioGainFader(
            zona_ganho,
            variable=self.var_volume,
            width=105,
            height=24,
            command=self._ao_mudar_volume
        )
        self.fader_vol.pack(side=tk.RIGHT, padx=(4, 2))

        self.lbl_volume_valor = tk.Label(
            zona_ganho,
            text="080% [-1.9dB]",
            bg=ThemeConfig.BG_SURFACE,
            fg=ThemeConfig.TEXT_PRIMARY,
            font=ThemeConfig.FONT_MONO,
            width=13,
            anchor="e"
        )
        self.lbl_volume_valor.pack(side=tk.RIGHT, padx=(0, 2))

    def _construir_menu_contexto_tabela(self):
        """Menu de clique direito na tabela para acesso rápido a Play, Preview, Atalhos e Corte."""
        self.menu_contexto = tk.Menu(
            self.root,
            tearoff=0,
            bg=ThemeConfig.BG_SURFACE,
            fg=ThemeConfig.TEXT_PRIMARY,
            activebackground=ThemeConfig.ACCENT,
            activeforeground=ThemeConfig.BG_MAIN,
            bd=1,
            relief=tk.FLAT,
            font=ThemeConfig.FONT_UI
        )
        self.menu_contexto.add_command(label=self._t("ctx_play"), command=self.tocar_audio_selecionado)
        self.menu_contexto.add_command(label=self._t("ctx_preview"), command=self.tocar_preview_fone)
        self.menu_contexto.add_separator()
        self.menu_contexto.add_command(label=self._t("ctx_hotkey"), command=self.definir_hotkey_audio)
        self.menu_contexto.add_command(label=self._t("ctx_add_fav"), command=self.adicionar_audio_na_playlist)
        self.menu_contexto.add_command(label=self._t("ctx_trim"), command=self.cortar_e_salvar_audio)

    def _exibir_menu_contexto_tabela(self, event):
        iid = self.tabela_audios.identify_row(event.y)
        if iid:
            self.tabela_audios.selection_set(iid)
            self.engine.audio_selecionado = iid
            self._atualizar_info_selecao()
            try:
                self.menu_contexto.tk_popup(event.x_root, event.y_root)
            finally:
                self.menu_contexto.grab_release()

    # --------------------------------------------------------------------------
    # LÓGICA DE PASTAS, BUSCA INSTANTÂNEA E PLAYLISTS
    # --------------------------------------------------------------------------
    def _definir_status(self, texto: str, ativo: bool = None):
        self.lbl_status.config(
            text=texto.upper(),
            fg=ThemeConfig.TEXT_PRIMARY if ativo else ThemeConfig.TEXT_SECONDARY
        )
        if ativo is not None:
            self.led_status.set_active(ativo)

    def escolher_nova_pasta(self):
        pasta = filedialog.askdirectory(
            initialdir=self.engine.pasta_atual,
            title=self._t("dlg_folder_title")
        )
        if pasta:
            self.engine.pasta_atual = pasta
            self.var_caminho_pasta.set(pasta)
            self._persistir_preferencias_usuario()
            self.engine.carregar_configuracoes()
            self.combo_playlist.config(values=list(self.engine.playlists.keys()))
            self.var_playlist_atual.set(PLAYLIST_TODOS)
            self.carregar_lista_audios()

    def carregar_lista_audios(self):
        caminho_digitado = self.var_caminho_pasta.get().strip()
        ok, msg = self.engine.escanear_pasta_audios(caminho_digitado)
        if not ok:
            self._definir_status(msg, ativo=False)
            return
        self._persistir_preferencias_usuario()
        self.filtrar_tabela_audios()
        self._calcular_duracoes_pendentes_async()

    def _calcular_duracoes_pendentes_async(self):
        """Calcula em segundo plano a duração de arquivos MP3/OGG novos sem travar a interface."""
        pendentes = [
            (arq, cam)
            for arq, cam in self.engine.arquivos_audio.items()
            if cam not in self.engine.duracoes_cache and arq not in self.engine.duracoes_persistidas
        ]
        if not pendentes:
            return

        def _worker_duracoes():
            alterado = False
            for arq, cam in pendentes:
                dur = self.engine.obter_duracao_audio(cam, permitir_decodificar=True)
                if dur > 0:
                    alterado = True
                    dur_str = self._formatar_tempo(dur)
                    self.root.after(0, lambda a=arq, d=dur_str: self._atualizar_celula_duracao(a, d))
            if alterado:
                self.engine.salvar_configuracoes()

        threading.Thread(target=_worker_duracoes, daemon=True).start()

    def _atualizar_celula_duracao(self, arquivo: str, duracao_str: str):
        try:
            if self.tabela_audios.exists(arquivo):
                vals = list(self.tabela_audios.item(arquivo, "values"))
                if len(vals) == 4:
                    vals[3] = duracao_str
                    self.tabela_audios.item(arquivo, values=vals)
        except Exception:
            pass

    def filtrar_tabela_audios(self):
        for item in self.tabela_audios.get_children():
            self.tabela_audios.delete(item)

        termo_busca = self.var_busca.get().strip().lower()
        playlist_ativa = self.var_playlist_atual.get()
        arquivos_da_playlist = self.engine.playlists.get(playlist_ativa, [])

        mapa_tecla_por_arquivo = {arq: tecla for tecla, arq in self.engine.hotkeys_audios.items()}

        total_exibidos = 0
        for arquivo, caminho_completo in self.engine.arquivos_audio.items():
            if playlist_ativa != PLAYLIST_TODOS and arquivo not in arquivos_da_playlist:
                continue

            nome_sem_ext, extensao = os.path.splitext(arquivo)
            atalho_str = mapa_tecla_por_arquivo.get(arquivo, "---")

            if termo_busca and (termo_busca not in nome_sem_ext.lower() and termo_busca not in atalho_str.lower()):
                continue

            duracao_seg = self.engine.obter_duracao_audio(caminho_completo, permitir_decodificar=False)
            duracao_str = self._formatar_tempo(duracao_seg) if duracao_seg > 0 else "--:--"

            self.tabela_audios.insert(
                "",
                tk.END,
                iid=arquivo,
                values=(atalho_str, nome_sem_ext, extensao.upper().replace(".", ""), duracao_str)
            )
            total_exibidos += 1

        self.lbl_contador.config(text=self._t("tracks_count").format(n=f"{total_exibidos:02d}"))

        itens = self.tabela_audios.get_children()
        if itens:
            alvo_sel = self.engine.audio_selecionado if self.engine.audio_selecionado in itens else itens[0]
            self.tabela_audios.selection_set(alvo_sel)
            self.engine.audio_selecionado = alvo_sel
            self._atualizar_info_selecao()

        if not self.engine.esta_tocando:
            self._definir_status(self._t("status_index").format(n=total_exibidos), ativo=False)

    def _ao_dar_enter_na_busca(self, event=None):
        itens = self.tabela_audios.get_children()
        if itens:
            self.tabela_audios.selection_set(itens[0])
            self.engine.audio_selecionado = itens[0]
            self.tocar_audio_selecionado()

    def criar_nova_playlist(self):
        nome = simpledialog.askstring(self._t("dlg_new_list_title"), self._t("dlg_new_list_prompt"))
        if nome:
            nome_limpo = nome.strip().upper()
            if nome_limpo and nome_limpo not in self.engine.playlists:
                self.engine.playlists[nome_limpo] = []
                self.engine.salvar_configuracoes()
                self.combo_playlist.config(values=list(self.engine.playlists.keys()))
                self.var_playlist_atual.set(nome_limpo)
                self.filtrar_tabela_audios()

    def adicionar_audio_na_playlist(self):
        if not self.engine.audio_selecionado:
            messagebox.showwarning(self._t("dlg_warn_title"), self._t("status_select_first"))
            return

        playlist_destino = self.var_playlist_atual.get()
        if playlist_destino == PLAYLIST_TODOS:
            playlist_destino = PLAYLIST_FAVORITOS

        if self.engine.audio_selecionado not in self.engine.playlists[playlist_destino]:
            self.engine.playlists[playlist_destino].append(self.engine.audio_selecionado)
            self.engine.salvar_configuracoes()
            self._definir_status(
                self._t("status_added_list").format(arq=self.engine.audio_selecionado, lista=playlist_destino)
            )

    def remover_audio_da_playlist(self):
        playlist_atual = self.var_playlist_atual.get()
        if playlist_atual == PLAYLIST_TODOS:
            messagebox.showinfo(self._t("dlg_warn_title"), self._t("dlg_remove_list_info"))
            return
        arq = self.engine.audio_selecionado
        if arq and arq in self.engine.playlists.get(playlist_atual, []):
            self.engine.playlists[playlist_atual].remove(arq)
            self.engine.salvar_configuracoes()
            self.filtrar_tabela_audios()

    # --------------------------------------------------------------------------
    # CONTROLES DE REPRODUÇÃO, ROTEAMENTO, NORMALIZAÇÃO E GANHO
    # --------------------------------------------------------------------------
    def _ao_selecionar_item(self, event=None):
        selecao = self.tabela_audios.selection()
        if selecao:
            self.engine.audio_selecionado = selecao[0]
            self._atualizar_info_selecao()

    def _atualizar_info_selecao(self):
        if not self.engine.audio_selecionado:
            return
        caminho = self.engine.arquivos_audio.get(self.engine.audio_selecionado)
        if caminho:
            dur = self.engine.obter_duracao_audio(caminho, permitir_decodificar=True)
            self.var_segundo_fim.set(f"{dur:.1f}")
            try:
                if float(self.var_segundo_inicio.get().replace(",", ".")) >= dur:
                    self.var_segundo_inicio.set("0.0")
            except ValueError:
                self.var_segundo_inicio.set("0.0")
            self.lbl_faixa_ativa.config(text=self.engine.audio_selecionado.upper())
            if not self.engine.esta_tocando:
                self.timeline.set_range(max(0.1, dur))
                self.lbl_tempo_total.config(text=self._formatar_tempo(dur))
            self._atualizar_marcadores_trim()

    def _atualizar_marcadores_trim(self):
        try:
            t_in = max(0.0, float(self.var_segundo_inicio.get().replace(",", ".")))
        except ValueError:
            t_in = 0.0
        try:
            t_out = max(0.0, float(self.var_segundo_fim.get().replace(",", ".")))
        except ValueError:
            t_out = 0.0
        self.timeline.set_trim_markers(t_in, t_out)

    def _obter_segundo_digitado(self) -> float:
        try:
            valor = float(self.var_segundo_inicio.get().replace(",", "."))
            return max(0.0, valor)
        except ValueError:
            self.var_segundo_inicio.set("0.0")
            return 0.0

    def tocar_preview_fone(self):
        """Toca o áudio selecionado exclusivamente no fone do usuário (Preview)."""
        self.tocar_audio_selecionado(forcar_apenas_fone=True)

    def tocar_audio_selecionado(
        self,
        segundo_personalizado: float = None,
        arquivo_especifico: str = None,
        forcar_apenas_fone: bool = False
    ):
        if arquivo_especifico:
            self.engine.audio_selecionado = arquivo_especifico
        else:
            selecao = self.tabela_audios.selection()
            if selecao:
                self.engine.audio_selecionado = selecao[0]

        arq = self.engine.audio_selecionado
        if not arq or arq not in self.engine.arquivos_audio:
            self._definir_status(self._t("status_select_first"), ativo=False)
            return

        self.modo_preview_ativo = bool(forcar_apenas_fone)
        modo_saida = "fone" if forcar_apenas_fone else self.var_modo_saida.get()
        disp_call = self.combo_disp_call.get()
        disp_fone = self.combo_disp_fone.get()

        if modo_saida == "fone":
            self.engine.inicializar_mixer(disp_fone)
        else:
            self.engine.inicializar_mixer(disp_call)

        caminho = self.engine.arquivos_audio[arq]
        self.engine.duracao_atual = self.engine.obter_duracao_audio(caminho, permitir_decodificar=True)

        if self.engine.duracao_atual > 0:
            self.timeline.set_range(self.engine.duracao_atual)
            self.lbl_tempo_total.config(text=self._formatar_tempo(self.engine.duracao_atual))
            self._atualizar_marcadores_trim()

        if segundo_personalizado is not None:
            segundo_inicio = segundo_personalizado
        else:
            segundo_inicio = self._obter_segundo_digitado()

        if self.engine.duracao_atual > 0 and segundo_inicio >= self.engine.duracao_atual:
            segundo_inicio = 0.0

        try:
            vol_atual = float(self.var_volume.get())
            normalizar = self.var_normalizar.get()

            self.engine.parar_fone_simultaneo()
            try:
                pygame.mixer.music.stop()
                if hasattr(pygame.mixer.music, "unload"):
                    pygame.mixer.music.unload()
            except Exception:
                pass

            precisa_processar_pcm = (
                (vol_atual > 100.0)
                or normalizar
                or (modo_saida == "ambos" and SOUNDDEVICE_DISPONIVEL)
                or (segundo_inicio > 0.0 and caminho.lower().endswith(".wav"))
            )

            if not precisa_processar_pcm:
                caminho_para_tocar = caminho
                self.engine.usando_audio_estourado = False
                pygame.mixer.music.load(caminho_para_tocar)
                pygame.mixer.music.set_volume(vol_atual / 100.0)
                try:
                    pygame.mixer.music.play(start=segundo_inicio)
                except pygame.error:
                    caminho_para_tocar = self.engine.gerar_wav_processado(
                        caminho, vol_atual, normalizar, segundo_inicio=segundo_inicio
                    )
                    pygame.mixer.music.load(caminho_para_tocar)
                    pygame.mixer.music.set_volume(vol_atual / 100.0)
                    pygame.mixer.music.play()
            else:
                caminho_para_tocar = self.engine.gerar_wav_processado(
                    caminho, vol_atual, normalizar, segundo_inicio=segundo_inicio
                )
                self.engine.usando_audio_estourado = (vol_atual > 100.0) or normalizar
                pygame.mixer.music.load(caminho_para_tocar)
                pygame.mixer.music.set_volume(1.0 if vol_atual > 100.0 else (vol_atual / 100.0))
                pygame.mixer.music.play()

            if modo_saida == "ambos" and disp_fone != disp_call:
                self.engine.iniciar_reproducao_fone_simultaneo(
                    caminho_para_tocar, disp_fone, 0.0, vol_atual
                )

            self.engine.offset_segundo = segundo_inicio
            self.engine.esta_tocando = True
            self.engine.esta_pausado = False
            self.btn_pausar.set_text(self._t("btn_pause"))
            self.btn_pausar.set_accent(False)
            self.btn_preview.set_accent(forcar_apenas_fone)
            self.lbl_faixa_ativa.config(text=arq.upper())

            if forcar_apenas_fone:
                self._definir_status(
                    self._t("status_preview").format(arq=arq, tempo=self._formatar_tempo(segundo_inicio)),
                    ativo=True
                )
            else:
                tag_modo = {
                    "fone": self._t("mode_fone"),
                    "call": self._t("mode_call"),
                    "ambos": self._t("mode_ambos")
                }.get(modo_saida, "")
                self._definir_status(
                    self._t("status_playing").format(
                        modo=tag_modo, arq=arq, tempo=self._formatar_tempo(segundo_inicio)
                    ),
                    ativo=True
                )
        except Exception as erro:
            self._definir_status(f"ERRO: {erro}", ativo=False)

    def _alternar_injecao_microfone(self):
        ativar = self.var_injetar_mic.get()
        if ativar and not SOUNDDEVICE_DISPONIVEL:
            self.var_injetar_mic.set(False)
            messagebox.showinfo(
                self._t("dlg_warn_title"),
                "Para injetar o microfone via Python e usar o modo 'FONE + CALL', instale:\n\n"
                "pip install sounddevice numpy"
            )
            return

        ok, msg = self.engine.configurar_injecao_mic(
            ativar=ativar,
            disp_mic=self.combo_disp_mic.get(),
            disp_call=self.combo_disp_call.get(),
            fn_block_voice_ativo=lambda: self.var_block_voice.get()
        )
        if not ok:
            self.var_injetar_mic.set(False)
        self._persistir_preferencias_usuario()
        self._definir_status(msg, ativo=self.engine.esta_tocando)

    def _ao_trocar_microfone(self, event=None):
        self._persistir_preferencias_usuario()
        if self.var_injetar_mic.get():
            self._alternar_injecao_microfone()

    # --------------------------------------------------------------------------
    # SOUND EDITOR: CORTAR TRECHO (IN / OUT) E SALVAR
    # --------------------------------------------------------------------------
    def cortar_e_salvar_audio(self):
        arq = self.engine.audio_selecionado
        if not arq or arq not in self.engine.arquivos_audio:
            messagebox.showwarning(self._t("dlg_warn_title"), self._t("status_select_first"))
            return

        try:
            seg_ini = float(self.var_segundo_inicio.get().replace(",", "."))
            seg_fim = float(self.var_segundo_fim.get().replace(",", "."))
        except ValueError:
            messagebox.showerror(self._t("dlg_warn_title"), self._t("dlg_trim_err_num"))
            return

        caminho_orig = self.engine.arquivos_audio[arq]
        duracao_total = self.engine.obter_duracao_audio(caminho_orig, permitir_decodificar=True)

        if seg_fim <= 0 or seg_fim > duracao_total:
            seg_fim = duracao_total
        if seg_ini < 0 or seg_ini >= seg_fim:
            messagebox.showerror(self._t("dlg_warn_title"), self._t("dlg_trim_err_range"))
            return

        nome_base, _ = os.path.splitext(arq)
        novo_nome = simpledialog.askstring(
            self._t("btn_trim"),
            self._t("dlg_trim_prompt").format(ini=seg_ini, fim=seg_fim),
            initialvalue=f"{nome_base}_trim"
        )
        if not novo_nome:
            return

        if not novo_nome.lower().endswith(".wav"):
            novo_nome += ".wav"

        caminho_destino = os.path.join(self.engine.pasta_atual, novo_nome)

        try:
            if self.engine.esta_tocando and self.engine.audio_selecionado == novo_nome:
                self.parar_audio()
                if hasattr(pygame.mixer.music, "unload"):
                    pygame.mixer.music.unload()

            self.engine.exportar_corte_wav(caminho_orig, caminho_destino, seg_ini, seg_fim)
            self.engine.duracoes_cache.pop(caminho_destino, None)
            self.engine.duracoes_persistidas.pop(novo_nome, None)
            self.carregar_lista_audios()
            self._definir_status(self._t("status_trim_saved").format(arq=novo_nome), ativo=False)
        except Exception as erro:
            messagebox.showerror(self._t("dlg_warn_title"), str(erro))

    # --------------------------------------------------------------------------
    # HOTKEYS GLOBAIS NATIVAS DO WINDOWS (COM CAPTURA POR TECLADO OU LISTA)
    # --------------------------------------------------------------------------
    def definir_hotkey_audio(self):
        arq = self.engine.audio_selecionado
        if not arq:
            messagebox.showwarning(self._t("dlg_warn_title"), self._t("status_select_first"))
            return

        janela_hk = tk.Toplevel(self.root)
        janela_hk.title(self._t("dlg_hk_title"))
        janela_hk.geometry("360x195")
        janela_hk.configure(bg=ThemeConfig.BG_SURFACE)
        janela_hk.transient(self.root)
        janela_hk.grab_set()

        frame_modal = tk.Frame(janela_hk, bg=ThemeConfig.BG_SURFACE, padx=16, pady=16)
        frame_modal.pack(fill=tk.BOTH, expand=True)

        tk.Label(
            frame_modal,
            text=self._t("dlg_hk_target").format(arq=arq.upper()),
            bg=ThemeConfig.BG_SURFACE,
            fg=ThemeConfig.ACCENT,
            font=ThemeConfig.FONT_MONO_BOLD
        ).pack(anchor="w", pady=(0, 6))

        tk.Label(
            frame_modal,
            text=self._t("dlg_hk_prompt"),
            bg=ThemeConfig.BG_SURFACE,
            fg=ThemeConfig.TEXT_SECONDARY,
            font=ThemeConfig.FONT_LABEL
        ).pack(anchor="w", pady=(0, 4))

        nenhum_txt = self._t("dlg_hk_none")
        teclas_disponiveis = [nenhum_txt] + [k for k in MAPA_VK_WINDOWS.keys() if k != "END"]
        combo_tecla = ttk.Combobox(
            frame_modal, values=teclas_disponiveis, state="readonly", font=ThemeConfig.FONT_MONO
        )

        tecla_atual = next((k for k, v in self.engine.hotkeys_audios.items() if v == arq), "F1")
        combo_tecla.set(tecla_atual)
        combo_tecla.pack(fill=tk.X, pady=(0, 16))

        def _capturar_tecla_evento(event):
            ks = event.keysym.upper()
            if ks in MAPA_VK_WINDOWS and ks != "END":
                combo_tecla.set(ks)
            elif ks.startswith("KP_") and f"NUM{ks[3:]}" in MAPA_VK_WINDOWS:
                combo_tecla.set(f"NUM{ks[3:]}")

        janela_hk.bind("<KeyPress>", _capturar_tecla_evento)

        def _confirmar():
            escolha = combo_tecla.get()
            for k, v in list(self.engine.hotkeys_audios.items()):
                if v == arq:
                    del self.engine.hotkeys_audios[k]
            if escolha not in (nenhum_txt, "NONE", "NENHUM", "Nenhum"):
                self.engine.hotkeys_audios[escolha] = arq
            self.engine.salvar_configuracoes()
            self.filtrar_tabela_audios()
            janela_hk.destroy()

        StudioButton(
            frame_modal, text=self._t("dlg_hk_confirm"), width=150, height=28, accent=True, command=_confirmar
        ).pack(anchor="e")

    def _monitorar_hotkeys_globais(self):
        if self.var_hotkeys_ativas.get() and hasattr(ctypes, "windll"):
            widget_focado = self.root.focus_get()
            digitando_em_campo = isinstance(widget_focado, (tk.Entry, tk.Spinbox, ttk.Entry))

            user32 = ctypes.windll.user32
            teclas_ativas_agora = set()

            for nome_tecla, vk in MAPA_VK_WINDOWS.items():
                if digitando_em_campo and (
                    nome_tecla.startswith("NUM")
                    or nome_tecla in ("END", "HOME", "INSERT", "PAGEUP", "PAGEDOWN")
                ):
                    continue

                if isinstance(vk, tuple):
                    mod_ok = (user32.GetAsyncKeyState(vk[0]) & 0x8000) != 0
                    key_ok = (user32.GetAsyncKeyState(vk[1]) & 0x8000) != 0
                    pressionada = mod_ok and key_ok
                else:
                    pressionada = (user32.GetAsyncKeyState(vk) & 0x8000) != 0

                if pressionada:
                    teclas_ativas_agora.add(nome_tecla)
                    if nome_tecla not in self.estado_teclas_anterior:
                        if nome_tecla == "END":
                            self.parar_audio()
                        elif nome_tecla in self.engine.hotkeys_audios:
                            arq = self.engine.hotkeys_audios[nome_tecla]
                            self.tocar_audio_selecionado(segundo_personalizado=0.0, arquivo_especifico=arq)

            self.estado_teclas_anterior = teclas_ativas_agora

        self.root.after(45, self._monitorar_hotkeys_globais)

    # --------------------------------------------------------------------------
    # REMOTE CONTROL API (THREADING HTTP SERVER + WEB APP RESPONSIVO)
    # --------------------------------------------------------------------------
    def _iniciar_servidor_remoto(self):
        app_ref = self

        class ReusableThreadingHTTPServer(ThreadingHTTPServer):
            allow_reuse_address = True
            daemon_threads = True

        class PainelRemotoHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass

            def do_GET(self):
                parsed = urllib.parse.urlparse(self.path)
                rota = parsed.path
                params = urllib.parse.parse_qs(parsed.query)

                if rota == "/api/status":
                    self._responder_json({
                        "tocando": app_ref.engine.esta_tocando,
                        "pausado": app_ref.engine.esta_pausado,
                        "audio_atual": app_ref.engine.audio_selecionado,
                        "volume": int(app_ref.var_volume.get()),
                        "modo": app_ref.var_modo_saida.get(),
                        "audios": list(app_ref.engine.arquivos_audio.keys())
                    })
                elif rota == "/api/play":
                    nome = params.get("file", [None])[0]
                    preview = params.get("preview", ["0"])[0] == "1"
                    if nome and nome in app_ref.engine.arquivos_audio:
                        app_ref.root.after(
                            0,
                            lambda n=nome, p=preview: app_ref.tocar_audio_selecionado(
                                0.0, n, forcar_apenas_fone=p
                            )
                        )
                    self._responder_json({"ok": True})
                elif rota == "/api/volume":
                    val_str = params.get("val", [None])[0]
                    if val_str is not None:
                        try:
                            v = max(0.0, min(800.0, float(val_str)))
                            app_ref.root.after(0, lambda val=v: (app_ref.var_volume.set(val), app_ref._ao_mudar_volume(val)))
                        except ValueError:
                            pass
                    self._responder_json({"ok": True})
                elif rota == "/api/stop":
                    app_ref.root.after(0, app_ref.parar_audio)
                    self._responder_json({"ok": True})
                elif rota == "/api/pause":
                    app_ref.root.after(0, app_ref.alternar_pausa)
                    self._responder_json({"ok": True})
                elif rota == "/api/estourar":
                    app_ref.root.after(0, app_ref.alternar_modo_estourado)
                    self._responder_json({"ok": True})
                else:
                    self.send_response(200)
                    self.send_header("Content-type", "text/html; charset=utf-8")
                    self.end_headers()
                    botoes_html = "".join(
                        f'<button class="pad" data-name="{html.escape(os.path.splitext(a)[0].lower(), quote=True)}" '
                        f'data-file="{html.escape(a, quote=True)}" '
                        f'onclick="tocar(this.getAttribute(\'data-file\'))">'
                        f'{html.escape(os.path.splitext(a)[0])}</button>'
                        for a in list(app_ref.engine.arquivos_audio.keys())
                    )
                    vol_ini = int(app_ref.var_volume.get())
                    pagina_html = f"""<!DOCTYPE html><html><head><meta charset="utf-8">
                    <meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1,user-scalable=no">
                    <title>CuePad Remote</title>
                    <style>
                        *{{box-sizing:border-box;-webkit-tap-highlight-color:transparent}}
                        body{{background:#0B0B0B;color:#EAEAEA;font-family:system-ui,-apple-system,sans-serif;padding:14px;margin:0}}
                        .hdr{{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #262626;padding-bottom:10px;margin-bottom:12px;font-family:monospace;font-size:13px}}
                        .hdr b{{color:#D95726;letter-spacing:1px}}
                        .top{{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:10px}}
                        .top button{{padding:13px 6px;background:#151515;border:1px solid #262626;color:#EAEAEA;font-family:monospace;font-weight:bold;font-size:12px;cursor:pointer}}
                        .top button.accent{{border-color:#D95726;color:#D95726}}
                        .bar{{display:flex;gap:8px;align-items:center;margin-bottom:12px;background:#151515;padding:8px 10px;border:1px solid #262626}}
                        .bar input[type=search]{{flex:1;background:#0B0B0B;border:1px solid #262626;color:#EAEAEA;padding:8px;font-size:13px;outline:none}}
                        .bar label{{font-size:11px;font-family:monospace;color:#858585;display:flex;align-items:center;gap:4px;white-space:nowrap}}
                        .vol{{display:flex;align-items:center;gap:10px;margin-bottom:14px;background:#151515;padding:8px 12px;border:1px solid #262626;font-family:monospace;font-size:12px}}
                        .vol input{{flex:1;accent-color:#D95726}}
                        .grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(135px,1fr));gap:8px}}
                        .grid button{{background:#151515;color:#EAEAEA;border:1px solid #262626;padding:16px 10px;font-size:13px;text-align:left;cursor:pointer;word-break:break-word;transition:border-color .1s}}
                        .grid button:active{{border-color:#D95726;color:#D95726;background:#1C1C1C}}
                    </style></head><body>
                    <div class="hdr"><span><b>CUEPAD</b> // REMOTE</span><span id="st">ONLINE</span></div>
                    <div class="top">
                        <button onclick="fetch('/api/pause')">PAUSE</button>
                        <button onclick="fetch('/api/stop')">STOP</button>
                        <button class="accent" onclick="fetch('/api/estourar')">BOOST</button>
                    </div>
                    <div class="vol">
                        <span>VOL</span>
                        <input id="vslider" type="range" min="0" max="450" value="{vol_ini}" oninput="mudarVol(this.value)">
                        <span id="vtxt">{vol_ini}%</span>
                    </div>
                    <div class="bar">
                        <input type="search" placeholder="Buscar áudio..." oninput="filtrar(this.value)">
                        <label><input type="checkbox" id="chkPrev"> SÓ FONE</label>
                    </div>
                    <div class="grid" id="lista">{botoes_html}</div>
                    <script>
                        function tocar(f){{
                            const prev = document.getElementById('chkPrev').checked ? '1' : '0';
                            fetch('/api/play?file='+encodeURIComponent(f)+'&preview='+prev);
                        }}
                        function mudarVol(v){{
                            document.getElementById('vtxt').innerText = v + '%';
                            fetch('/api/volume?val='+v);
                        }}
                        function filtrar(q){{
                            q = q.toLowerCase().trim();
                            document.querySelectorAll('.pad').forEach(b => {{
                                b.style.display = b.getAttribute('data-name').includes(q) ? '' : 'none';
                            }});
                        }}
                    </script>
                    </body></html>"""
                    self.wfile.write(pagina_html.encode("utf-8"))

            def _responder_json(self, dados: dict):
                self.send_response(200)
                self.send_header("Content-type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps(dados).encode("utf-8"))

        def _rodar_servidor():
            try:
                self.servidor_http = ReusableThreadingHTTPServer(("0.0.0.0", PORTA_API_REMOTA), PainelRemotoHandler)
                self.servidor_http.serve_forever()
            except Exception:
                pass

        threading.Thread(target=_rodar_servidor, daemon=True).start()

    def mostrar_info_api_remota(self):
        """Abre modal com todos os IPs locais e botão para liberar a porta no Firewall do Windows."""
        janela_rem = tk.Toplevel(self.root)
        janela_rem.title(self._t("btn_remote"))
        janela_rem.geometry("460x320")
        janela_rem.configure(bg=ThemeConfig.BG_SURFACE)
        janela_rem.transient(self.root)
        janela_rem.grab_set()

        box = tk.Frame(janela_rem, bg=ThemeConfig.BG_SURFACE, padx=18, pady=16)
        box.pack(fill=tk.BOTH, expand=True)

        titulo = "CONTROLE PELO CELULAR (WI-FI)" if self.idioma == "pt" else "PHONE REMOTE CONTROL (WI-FI)"
        SectionHeader(box, titulo).pack(fill=tk.X, pady=(0, 12))

        ips = self.engine.obter_todos_ips_locais()
        links_str = "\n".join(f"http://{ip}:{PORTA_API_REMOTA}" for ip in ips)

        if self.idioma == "pt":
            explicacao = (
                "1. Conecte seu celular no mesmo Wi-Fi deste PC e abra um dos links abaixo no navegador:\n\n"
                f"{links_str}\n\n"
                "2. Não abriu no celular (Windows LTSC / Firewall)?\n"
                "Clique no botão abaixo para liberar a porta 8765 no Firewall do Windows."
            )
            txt_firewall = "LIBERAR PORTA NO FIREWALL (ADMIN)"
            txt_fechar = "FECHAR"
        else:
            explicacao = (
                "1. Connect your phone to the same Wi-Fi and open one of these links in your browser:\n\n"
                f"{links_str}\n\n"
                "2. Page not loading on your phone (Windows Firewall)?\n"
                "Click the button below to allow port 8765 in Windows Firewall."
            )
            txt_firewall = "ALLOW PORT IN FIREWALL (ADMIN)"
            txt_fechar = "CLOSE"

        tk.Label(
            box,
            text=explicacao,
            bg=ThemeConfig.BG_SURFACE,
            fg=ThemeConfig.TEXT_PRIMARY,
            font=ThemeConfig.FONT_UI,
            justify=tk.LEFT,
            wraplength=420
        ).pack(anchor="w", fill=tk.BOTH, expand=True)

        rodape = tk.Frame(box, bg=ThemeConfig.BG_SURFACE)
        rodape.pack(fill=tk.X, pady=(12, 0))

        def _liberar_fw():
            ok = self.engine.liberar_porta_firewall(PORTA_API_REMOTA)
            if ok:
                self._definir_status("PORTA 8765 LIBERADA NO FIREWALL DO WINDOWS", ativo=True)
            janela_rem.destroy()

        StudioButton(
            rodape, text=txt_firewall, width=250, height=28, accent=True, command=_liberar_fw
        ).pack(side=tk.LEFT)

        StudioButton(
            rodape, text=txt_fechar, width=90, height=28, command=janela_rem.destroy
        ).pack(side=tk.RIGHT)

    def abrir_tutorial(self):
        """Exibe o tutorial passo a passo minimalista (4 etapas) e grava conclusão no settings.config."""
        janela_tut = tk.Toplevel(self.root)
        janela_tut.title(self._t("tut_title"))
        janela_tut.geometry("520x310")
        janela_tut.configure(bg=ThemeConfig.BG_SURFACE)
        janela_tut.transient(self.root)
        janela_tut.grab_set()

        container = tk.Frame(janela_tut, bg=ThemeConfig.BG_SURFACE, padx=20, pady=18)
        container.pack(fill=tk.BOTH, expand=True)

        hdr = SectionHeader(container, self._t("tut_title"))
        hdr.pack(fill=tk.X, pady=(0, 12))

        lbl_passo_titulo = tk.Label(
            container,
            text="",
            bg=ThemeConfig.BG_SURFACE,
            fg=ThemeConfig.TEXT_PRIMARY,
            font=ThemeConfig.FONT_TITLE,
            anchor="w"
        )
        lbl_passo_titulo.pack(fill=tk.X, pady=(0, 8))

        lbl_passo_corpo = tk.Label(
            container,
            text="",
            bg=ThemeConfig.BG_SURFACE,
            fg=ThemeConfig.TEXT_SECONDARY,
            font=ThemeConfig.FONT_UI,
            justify=tk.LEFT,
            anchor="nw",
            wraplength=475
        )
        lbl_passo_corpo.pack(fill=tk.BOTH, expand=True)

        HairlineDivider(container, orient="horizontal").pack(fill=tk.X, pady=(10, 12))

        barra_nav = tk.Frame(container, bg=ThemeConfig.BG_SURFACE)
        barra_nav.pack(fill=tk.X)

        etapa_atual = [0]
        passos = self._t("tut_steps")

        def _concluir_e_fechar():
            self.engine.salvar_preferencias_globais({"tutorial_concluido": True})
            janela_tut.destroy()

        def _atualizar_etapa():
            idx = etapa_atual[0]
            titulo_p, corpo_p = passos[idx]
            lbl_passo_titulo.config(text=titulo_p)
            lbl_passo_corpo.config(text=corpo_p)
            if idx == len(passos) - 1:
                btn_prox.set_text(self._t("tut_finish"))
            else:
                btn_prox.set_text(self._t("tut_next"))

        def _anterior():
            if etapa_atual[0] > 0:
                etapa_atual[0] -= 1
                _atualizar_etapa()

        def _proximo():
            if etapa_atual[0] < len(passos) - 1:
                etapa_atual[0] += 1
                _atualizar_etapa()
            else:
                _concluir_e_fechar()

        StudioButton(
            barra_nav, text=self._t("tut_skip"), width=90, height=28, command=_concluir_e_fechar
        ).pack(side=tk.LEFT)

        btn_prox = StudioButton(
            barra_nav, text=self._t("tut_next"), width=110, height=28, accent=True, command=_proximo
        )
        btn_prox.pack(side=tk.RIGHT)

        StudioButton(
            barra_nav, text=self._t("tut_prev"), width=100, height=28, command=_anterior
        ).pack(side=tk.RIGHT, padx=(0, 8))

        janela_tut.protocol("WM_DELETE_WINDOW", _concluir_e_fechar)
        _atualizar_etapa()

    # --------------------------------------------------------------------------
    # TRANSPORTE, VOLUME, OVERDRIVE E EVENTOS DE JANELA
    # --------------------------------------------------------------------------
    def alternar_modo_estourado(self):
        if self.var_volume.get() <= 100.0:
            self.var_volume.set(450.0)
            self._ao_mudar_volume(450.0)
        else:
            self.var_volume.set(80.0)
            self._ao_mudar_volume(80.0)

    def abrir_config_microfone_windows(self):
        try:
            subprocess.Popen(["control", "mmsys.cpl,,1"])
        except Exception:
            pass

        if self.idioma == "pt":
            instrucoes = (
                "COMO USAR SEU MICROFONE JUNTO COM O CUEPAD:\n\n"
                "Opção 1 (Pelo Programa): Marque 'Juntar minha voz no Cabo Virtual' em SEU MICROFONE.\n\n"
                "Opção 2 (Pelo Windows - Zero Atraso):\n"
                "1. Na janela de Som do Windows que abriu, dê dois cliques no seu Microfone físico.\n"
                "2. Vá na aba 'Escutar' e marque 'Escutar o dispositivo'.\n"
                "3. Escolha 'CABLE Input (VB-Audio Virtual Cable)' e clique em Aplicar."
            )
        else:
            instrucoes = (
                "HOW TO USE YOUR MICROPHONE WITH CUEPAD:\n\n"
                "Option 1 (In-App): Check 'Mix my voice into Virtual Cable' under YOUR MICROPHONE.\n\n"
                "Option 2 (Native Windows - Zero Latency):\n"
                "1. In the Windows Sound window that opened, double-click your physical Microphone.\n"
                "2. Go to the 'Listen' tab and check 'Listen to this device'.\n"
                "3. Select 'CABLE Input (VB-Audio Virtual Cable)' and click Apply."
            )
        messagebox.showinfo(self._t("btn_win_mic"), instrucoes)

    def alternar_pausa(self):
        if not self.engine.esta_tocando:
            return

        if self.engine.esta_pausado:
            pygame.mixer.music.unpause()
            self.engine.esta_pausado = False
            self.btn_pausar.set_text(self._t("btn_pause"))
            self.btn_pausar.set_accent(False)
            if self.modo_preview_ativo:
                self._definir_status(
                    self._t("status_preview").format(
                        arq=self.engine.audio_selecionado,
                        tempo=self.lbl_tempo_atual.cget("text")
                    ),
                    ativo=True
                )
            else:
                tag_modo = {
                    "fone": self._t("mode_fone"),
                    "call": self._t("mode_call"),
                    "ambos": self._t("mode_ambos")
                }.get(self.var_modo_saida.get(), "")
                self._definir_status(
                    self._t("status_playing").format(
                        modo=tag_modo,
                        arq=self.engine.audio_selecionado,
                        tempo=self.lbl_tempo_atual.cget("text")
                    ),
                    ativo=True
                )
        else:
            pygame.mixer.music.pause()
            self.engine.esta_pausado = True
            self.btn_pausar.set_text(self._t("btn_resume"))
            self.btn_pausar.set_accent(True)
            self._definir_status(
                self._t("status_paused").format(arq=self.engine.audio_selecionado),
                ativo=False
            )

    def parar_audio(self):
        self.engine.parar_fone_simultaneo()
        try:
            pygame.mixer.music.stop()
        except Exception:
            pass
        self.engine.esta_tocando = False
        self.engine.esta_pausado = False
        self.modo_preview_ativo = False
        self.engine.offset_segundo = 0.0
        self.timeline.set_position(0.0)
        self.lbl_tempo_atual.config(text="00:00")
        self.btn_pausar.set_text(self._t("btn_pause"))
        self.btn_pausar.set_accent(False)
        self.btn_preview.set_accent(False)
        self._definir_status(self._t("status_stopped"), ativo=False)

    def pular_para_segundo_digitado(self):
        segundo = self._obter_segundo_digitado()
        self.tocar_audio_selecionado(
            segundo_personalizado=segundo,
            forcar_apenas_fone=self.modo_preview_ativo
        )

    def _ao_iniciar_arraste_tempo(self):
        self.arrastando_slider = True

    def _ao_soltar_arraste_tempo(self, novo_segundo: float):
        self.arrastando_slider = False
        if self.engine.audio_selecionado:
            self.tocar_audio_selecionado(
                segundo_personalizado=novo_segundo,
                forcar_apenas_fone=self.modo_preview_ativo
            )

    def _ao_mudar_volume(self, valor):
        vol = float(valor)
        db_str = "-INF dB" if vol <= 0 else f"{20.0 * math.log10(vol / 100.0):+.1f}dB"

        if vol <= 100.0:
            self.lbl_volume_valor.config(
                text=f"{int(vol):03d}% [{db_str}]",
                fg=ThemeConfig.TEXT_PRIMARY
            )
            self.btn_estourar.set_text(self._t("btn_overdrive"))
            self.btn_estourar.set_accent(False)
        else:
            self.lbl_volume_valor.config(
                text=f"{int(vol):03d}% [{db_str}]",
                fg=ThemeConfig.ACCENT
            )
            self.btn_estourar.set_text(self._t("btn_clip_on"))
            self.btn_estourar.set_accent(True)

        try:
            if not pygame.mixer.get_init():
                return

            if vol <= 100.0 and not self.engine.usando_audio_estourado and not self.var_normalizar.get():
                pygame.mixer.music.set_volume(vol / 100.0)
                return

            if self.engine.esta_tocando and not self.engine.esta_pausado:
                if self.timer_reaplicar_boost is not None:
                    self.root.after_cancel(self.timer_reaplicar_boost)
                self.timer_reaplicar_boost = self.root.after(
                    180, self._reaplicar_volume_em_execucao
                )
        except Exception:
            pass

    def _reaplicar_volume_em_execucao(self):
        self.timer_reaplicar_boost = None
        self._persistir_preferencias_usuario()
        if not self.engine.esta_tocando:
            return
        pos_ms = pygame.mixer.music.get_pos()
        segundo_atual = self.engine.offset_segundo + (max(0, pos_ms) / 1000.0)
        self.tocar_audio_selecionado(
            segundo_personalizado=segundo_atual,
            forcar_apenas_fone=self.modo_preview_ativo
        )

    def _ao_trocar_dispositivo(self, event=None):
        modo = self.var_modo_saida.get()
        if modo == "ambos" and not SOUNDDEVICE_DISPONIVEL:
            messagebox.showinfo(
                self._t("dlg_warn_title"),
                "Para reproduzir no seu Fone e no Cabo Virtual simultaneamente via software, "
                "instale no terminal:\n\n"
                "pip install sounddevice numpy"
            )
            self.var_modo_saida.set("call")
            modo = "call"

        self.parar_audio()
        alvo = self.combo_disp_fone.get() if modo == "fone" else self.combo_disp_call.get()
        self.engine.inicializar_mixer(alvo)
        self._persistir_preferencias_usuario()
        self._definir_status(self._t("status_out_changed").format(disp=alvo), ativo=False)

    def _persistir_preferencias_usuario(self):
        """Salva o estado atual de idioma, dispositivos, diretório e ajustes em AppData\\Roaming\\CuePad\\settings.config."""
        self.engine.salvar_preferencias_globais({
            "idioma": self.idioma,
            "pasta_audios": self.engine.pasta_atual,
            "modo_saida": self.var_modo_saida.get(),
            "dispositivo_call": self.combo_disp_call.get(),
            "dispositivo_fone": self.combo_disp_fone.get(),
            "dispositivo_mic": self.combo_disp_mic.get(),
            "injetar_mic": bool(self.var_injetar_mic.get()),
            "block_voice": bool(self.var_block_voice.get()),
            "hotkeys_ativas": bool(self.var_hotkeys_ativas.get()),
            "normalizar": bool(self.var_normalizar.get()),
            "volume": float(self.var_volume.get()),
        })

    def _atualizar_progresso(self):
        if self.engine.esta_tocando and not self.engine.esta_pausado:
            if pygame.mixer.get_init() and pygame.mixer.music.get_busy():
                pos_ms = pygame.mixer.music.get_pos()
                if pos_ms >= 0:
                    segundo_atual = self.engine.offset_segundo + (pos_ms / 1000.0)
                    try:
                        seg_fim = float(self.var_segundo_fim.get().replace(",", "."))
                    except ValueError:
                        seg_fim = 0.0
                    if (
                        seg_fim > 0.0
                        and self.engine.duracao_atual > 0.0
                        and seg_fim < (self.engine.duracao_atual - 0.15)
                        and segundo_atual >= seg_fim
                    ):
                        self.parar_audio()
                        self._definir_status(self._t("status_finished"), ativo=False)
                        self.root.after(120, self._atualizar_progresso)
                        return

                    if not self.arrastando_slider:
                        self.timeline.set_position(segundo_atual)
                    self.lbl_tempo_atual.config(text=self._formatar_tempo(segundo_atual))
            else:
                self.engine.parar_fone_simultaneo()
                self.engine.esta_tocando = False
                self.modo_preview_ativo = False
                self.btn_preview.set_accent(False)
                if not self.arrastando_slider:
                    self.timeline.set_position(0.0)
                self.lbl_tempo_atual.config(text="00:00")
                self._definir_status(self._t("status_finished"), ativo=False)

        self.root.after(120, self._atualizar_progresso)

    @staticmethod
    def _formatar_tempo(segundos: float) -> str:
        segundos = max(0, int(segundos))
        minutos = segundos // 60
        seg_restantes = segundos % 60
        return f"{minutos:02d}:{seg_restantes:02d}"

    def _ao_fechar(self):
        self._persistir_preferencias_usuario()
        self.engine.salvar_configuracoes()
        if self.servidor_http is not None:
            try:
                self.servidor_http.shutdown()
                self.servidor_http.server_close()
            except Exception:
                pass
        self.engine.encerrar()
        self.root.destroy()


# Alias de compatibilidade
SoundboardDiscordApp = CuePadApp


if __name__ == "__main__":
    janela = tk.Tk()
    app = CuePadApp(janela)
    janela.mainloop()