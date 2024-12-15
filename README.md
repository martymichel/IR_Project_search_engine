# System zur Verarbeitung und Suche von Dokumenten

Dieses System bietet zwei Hauptfunktionalitäten:

1. Extraktion von Inhalten und Aktualisierung der Datenbank
2. Schnittstelle zur Dokumentensuche

## Vorbereitung

### Datenbank initialisieren

Um die Datenbank zu initialisieren, verbinde die DB oder starte den Server mit Docker.

Öffne das Skript `db_connector.py`...

```bash
python db_connector.py
```
...und ändere die DB-Konfiguration in folgendem Abschnitt:

```bash
class DatabaseConnector:
    def __init__(self, host="127.0.0.1", port=3306, user="root", password="rootroot", database="cas_course_data"):
        """Initialize the MySQL database connection"""
        self.db = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.db.cursor()
        self._init_database()
```

## DATEN extrahieren / parsen

Um Metadaten aus Dokumenten zu extrahieren und die Datenbank zu aktualisieren:

```bash
python content_processor.py
```

Dies wird:
- Verarbeitet alle Dokumente in der Datenbank
- Extrahiert Modul-, Themen- und Inhaltsinformationen

Nach ausführen des content_processor.py wird folgendes ausgegeben:

```bash  
CAS Content Processor
====================

Enter the directory path to process: PFAD ZU DEN DOKUMENTEN
```

trage hier den Pfad zu den Dokumenten ein. Der Vorgang wird durchgeführt und die Ergebnisse werden angezeigt:

```bash
Processing Summary
=================
Total files found: 5
Files processed: 5
Words extracted: 33898
Errors encountered: 0
Processing time: 147.01 seconds (BUG <- Stimmt nicht)
```
___

# Information Retrieval - Schulstoff suchen

Um die Dokumente zu durchsuchen öffne:

```bash
python search_documents.py
```

Folgende Ausgabe erscheint im Terminal:

```bash
Loading search index...
Indexing Documents: 100%|███████████| 478/478 [00:00<00:00, 22764.07doc/s]

Search index loaded successfully!

Search system ready! Enter search queries (Ctrl+C to exit)
Available fields: module, topic, subtopic, chapter, instructor, content

Enter search query:
```

- Gib den Suchbegriff ein und falls Gewünscht, kann auch nach spezifischen Feldern gesucht werden. 

- Drücke Enter um die Suche zu starten. Die Ergebnisse werden angezeigt:

```bash
Searching...
Calculating Scores: 100%|████████████| 166/166 [00:00<00:00, 55350.54doc/s]

Found 166 results:

1. G:\OneDrive - Flex\4.3_CAS Information Engineering\1_BD-DWH\DB-1\DB-1 2024-09-02_Folien.pdf
Module: Datenbanken & Data Warehousing
Topic: BD-DWH
Relevance Score: 1.00
--------------------------------------------------------------------------------

2. G:\OneDrive - Flex\4.3_CAS Information Engineering\1_BD-DWH\DB-1\DB-1 2024-09-02_Folien.pdf
Module: Datenbanken & Data Warehousing
Topic: BD-DWH
Relevance Score: 1.00
--------------------------------------------------------------------------------

3. G:\OneDrive - Flex\4.3_CAS Information Engineering\1_BD-DWH\DB-1\DB-1 2024-09-02_Folien.pdf
Module: Datenbanken & Data Warehousing
Topic: BD-DWH
Relevance Score: 0.00
--------------------------------------------------------------------------------

4. G:\OneDrive - Flex\4.3_CAS Information Engineering\1_BD-DWH\DB-1\DB-1 2024-09-02_Folien.pdf
Module: Datenbanken & Data Warehousing
Topic: BD-DWH
Relevance Score: 0.00
--------------------------------------------------------------------------------

5. G:\OneDrive - Flex\4.3_CAS Information Engineering\1_BD-DWH\DB-1\DB-1 2024-09-02_Folien.pdf
Module: Datenbanken & Data Warehousing
Topic: BD-DWH
Relevance Score: 0.00
``` 

# Verzeichnisstruktur
## Notwendige Dateien und ihre Rollen
### PDF auslesen und speichern
- content_processor.py
-- Kernmodul zur Verarbeitung von Dateien in einem Verzeichnis. Es verarbeitet PDFs mit Hilfe von PDFProcessor und speichert Inhalte in der Datenbank.

- processors.py
-- Enthält die Logik zur Verarbeitung von PDFs (PDFProcessor). Verantwortlich für Textextraktion und Metadatenanalyse.

- db_connector.py
-- Schnittstelle zur MySQL-Datenbank. Speichert Inhalte und Fehler.

- processing.log processing (optional):
-- Log-Datei zur Fehleranalyse bei der Verarbeitung.

### IR Suchmaschine
- search_documents.py
-- Interaktives Suchsystem. Lädt Inhalte aus der Datenbank und ermöglicht Volltext- sowie Metadatensuche.

- search_engine.py
-- Kernmodul der Suchmaschine. Indexiert Inhalte und führt Suchen basierend auf Relevanz durch.

- db_connector.py (erneut):
-- Liefert die Inhalte aus der Datenbank für die Suchmaschine.