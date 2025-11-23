# MDpdfChat

Een eenvoudige Flask-app waarmee je een Markdown-bestand kunt uploaden en het direct kunt exporteren als HTML of PDF.

## Installatie
1. Maak een virtuele omgeving aan en activeer deze.
2. Installeer afhankelijkheden:
   ```bash
   pip install -r requirements.txt
   ```

## Gebruik
Start de ontwikkelserver:
```bash
python app.py
```

Open vervolgens [http://localhost:5000](http://localhost:5000) in je browser, kies een Markdown-bestand en selecteer het gewenste exportformaat.

## Notities
- Bestanden worden niet opgeslagen; ze worden alleen in het geheugen verwerkt voor conversie.
- PDF-export wordt gegenereerd via `xhtml2pdf` en gebruikt de HTML-output van de Markdown-parser.
