# Perforce Server: Disk Space Fix (DigitalOcean)

**Stand**: 2026-01-31
**Server**: DigitalOcean Droplet mit SDP (Server Deployment Package)

## Problem

Perforce Server blockiert alle Befehle mit Error:
```
The filesystem 'P4ROOT' has only 4.4G free, but the server configuration requires at least 5G available.
```

Selbst `p4 configure set filesys.P4ROOT.min=1G` funktioniert nicht, da der Server keine Befehle akzeptiert.

## Lösung: Dateien manuell löschen

Da Server keine Befehle akzeptiert → Depot-Dateien direkt im Filesystem löschen.

### Schritt 1: SSH zum Server

```bash
ssh root@<droplet-ip>
```

### Schritt 2: Speicherverbrauch analysieren

```bash
df -h
du -sh /hxdepots/p4/1/depots/* | sort -h
du -sh /hxdepots/p4/1/depots/vw/main/* | sort -h
```

### Schritt 3: Server stoppen

```bash
sudo systemctl stop p4d_1
```

### Schritt 4: Nicht benötigte Depots löschen

```bash
rm -rf /hxdepots/p4/1/depots/vw/main/<OldDepotName>
```

### Schritt 5: Speicher prüfen

```bash
df -h
```

### Schritt 6: Server starten

```bash
sudo systemctl start p4d_1
systemctl status p4d_1
```

### Schritt 7: Datenbank aufräumen (von Client)

```bash
p4 login
p4 obliterate -y //<depot>/<path>/...
```

Dies entfernt die Referenzen in der Datenbank für die gelöschten Files.

## SDP Verzeichnisstruktur

```
/hxdepots/p4/1/
├── checkpoints/     # Checkpoint files (klein, behalten)
└── depots/          # Actual file storage (GROSS)
    └── vw/
        └── main/
            ├── Project1/    # Depot Daten
            └── Project2/    # Depot Daten

/hxmetadata/p4/1/
└── db1/             # Datenbank files
    ├── db.config    # BINÄR, nicht editieren
    ├── db.depot
    ├── db.rev
    └── ...

/p4/1/
├── root -> /hxmetadata/p4/1/db1  # Symlink
├── depots -> /hxdepots/p4/1/depots
└── bin/             # p4d Binaries
```

## Wichtige Befehle

| Befehl | Zweck |
|--------|-------|
| `sudo systemctl stop p4d_1` | Server stoppen |
| `sudo systemctl start p4d_1` | Server starten |
| `systemctl status p4d_1` | Status prüfen |
| `pkill -9 p4d` | Alle p4d Prozesse killen |
| `cat /root/perforce.password` | Original-Passwort anzeigen |

## Config ändern (wenn Server läuft)

Nach dem Aufräumen, wenn Server wieder Befehle akzeptiert:

```bash
source /p4/common/bin/p4_vars 1
p4 configure set filesys.P4ROOT.min=1G
```

## Hinweise

- `db.config` ist eine Binär-Datei, nicht mit `echo >>` editieren
- Bei SDP Installation immer `systemctl` nutzen, nicht direkt init scripts
- Vor dem Löschen: Server stoppen, sonst Datenbank-Korruption möglich
- Nach manuellem Löschen: `p4 obliterate` um DB zu cleanen

## Passwort vergessen?

Passwort steht in:
```bash
cat /root/perforce.password
```

Nach Login neues setzen:
```bash
p4 passwd
```
