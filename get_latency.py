import datetime
import os
import re
import subprocess
import time

# --- CONFIGURAZIONE ---
TARGET_IP = "192.168.64.7"  # Sostituisci con l'IP dell'host di destinazione in Mininet
INTERVAL_SEC = 1.0  # Ogni quanti secondi fare una misura
DURATION_SEC = 30  # Durata totale raccolta in secondi (0 = infinito fino a Ctrl+C)
OUTPUT_TXT = "leo_latency_log.txt"

REPO_DIR = os.path.expanduser(
    "/LeoEMMOD2"
)  # Cartella del tuo repo Git locale (se il .txt sta lì)
AUTO_GIT_PUSH = True  # Metti False se vuoi solo generare il .txt in locale


def ping_once(ip: str) -> str:
  """Esegue un singolo ping e restituisce RTT in ms o 'TIMEOUT'."""
  try:
    res = subprocess.run(
        ["ping", "-c", "1", "-W", "1", ip],
        capture_output=True,
        text=True,
        check=False,
    )
    match = re.search(r"time=([\d.]+)\s*ms", res.stdout)
    if match:
      return f"{match.group(1)} ms"
    return "TIMEOUT/UNREACHABLE"
  except Exception as e:
    return f"ERROR: {e}"


def push_to_github(repo_dir: str, filename: str) -> None:
  """Aggiunge, committa e pusha il file su GitHub (richiede auth già configurata)."""
  commit_msg = (
      f"Add emulation metrics {datetime.datetime.now().isoformat(timespec='seconds')}"
  )
  subprocess.run(["git", "-C", repo_dir, "add", filename], check=True)
  subprocess.run(
      ["git", "-C", repo_dir, "commit", "-m", commit_msg], check=False
  )
  subprocess.run(["git", "-C", repo_dir, "push"], check=True)


def main():
  file_path = os.path.join(REPO_DIR, OUTPUT_TXT)
  start_time = time.time()
  sample_idx = 0

  print(f"Raccolta dati verso {TARGET_IP} -> {file_path}")
  with open(file_path, "a", encoding="utf-8") as f:
    f.write(
        f"=== Sessione avviata: {datetime.datetime.now().isoformat()} | Target:"
        f" {TARGET_IP} ===\n"
    )
    try:
      while True:
        if DURATION_SEC > 0 and (time.time() - start_time) >= DURATION_SEC:
          break
        sample_idx += 1
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        rtt = ping_once(TARGET_IP)
        line = f"#{sample_idx} | {ts} | RTT={rtt}\n"
        f.write(line)
        f.flush()  # Scrive subito su disco così non perdi dati se ti fermi prima
        print(line.strip())
        time.sleep(INTERVAL_SEC)
    except KeyboardInterrupt:
      print("\nRaccolta interrotta manualmente.")

  if AUTO_GIT_PUSH:
    print("Caricamento su GitHub in corso...")
    try:
      push_to_github(REPO_DIR, OUTPUT_TXT)
      print("Caricato su GitHub con successo!")
    except subprocess.CalledProcessError as e:
      print(
          f"Errore durante il push su GitHub: {e}. Controlla configurazione"
          " git/credenziali."
      )


if __name__ == "__main__":
  main()
