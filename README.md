# Social Media Responder

> **Automatisch reageren op berichten van Facebook, Instagram en WhatsApp — in het Nederlands, aangedreven door Claude AI**

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![Claude](https://img.shields.io/badge/Claude-AI-orange?logo=anthropic&logoColor=white)
![Taal](https://img.shields.io/badge/Taal-Nederlands-yellow)
![License](https://img.shields.io/badge/License-MIT-green)

---

## Wat doet dit systeem?

Kleine en middelgrote bedrijven ontvangen dagelijks tientallen berichten via social media. Dit systeem verwerkt die berichten automatisch:

1. **Leest het inkomende bericht** (Facebook / Instagram / WhatsApp)
2. **Controleert op escalatiewoorden** — klachten, juridische vragen en urgente zaken worden gemarkeerd voor een menselijke medewerker
3. **Genereert een professioneel antwoord in het Nederlands** via Claude AI op basis van jouw bedrijfsprompt
4. **Logt alles** in een JSON-bestand voor rapportage en audits

---

## Functies

| Functie | Details |
|---|---|
| Taal | Altijd Nederlands (formeel, warm) |
| Platforms | Facebook, Instagram, WhatsApp (simulatie) |
| Escalatie | Automatische detectie van gevoelige trefwoorden |
| Aanpasbaar | Bedrijfsnaam, FAQ's en tone-of-voice via één tekstbestand |
| Logging | Elk bericht + antwoord opgeslagen in `logs/responses.json` |
| CLI | Interactief, demo-modus en log-viewer |

---

## Installatie

### 1. Clone de repository

```bash
git clone https://github.com/JOUW_GEBRUIKERSNAAM/social-media-responder.git
cd social-media-responder
```

### 2. Virtuele omgeving aanmaken

```bash
python -m venv venv

# Activeer
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux / macOS
```

### 3. Afhankelijkheden installeren

```bash
pip install -r requirements.txt
```

### 4. API-sleutel instellen

```powershell
# Windows PowerShell
$env:ANTHROPIC_API_KEY = "sk-ant-..."

# Linux / macOS
export ANTHROPIC_API_KEY="sk-ant-..."
```

Haal je sleutel op via [console.anthropic.com](https://console.anthropic.com).

---

## Gebruik

### Demo-modus (aanbevolen als eerste test)

```bash
python main.py --demo
```

Verwerkt 6 voorbeeldberichten inclusief escalaties.

### Interactieve modus

```bash
python main.py
```

Typ zelf berichten in en ontvang direct een antwoord.

### Log bekijken

```bash
python main.py --log
```

Toont de laatste 10 verwerkte berichten in een overzichtstabel.

---

## Escalatielogica

Berichten die een van de volgende woorden bevatten worden **niet automatisch beantwoord** maar gemarkeerd voor een menselijke medewerker:

```
klacht, klachten, juridisch, advocaat, rechtbank,
terugbetaling, terugstorten, refund,
dringend, urgent, bedreig, aangifte, schandaal, fraude
```

De lijst is volledig aanpasbaar in `config.py` → `ESCALATION_KEYWORDS`.

---

## Systeemprompt aanpassen

Het bestand `prompts/system_prompt.txt` bepaalt hoe de AI reageert. Pas het aan voor jouw organisatie:

```
prompts/system_prompt.txt
├── Identiteit van het bedrijf (naam, openingsuren, kanalen)
├── Toon & stijl (formeel/informeel, maximale berichtlengte)
├── Veelgestelde vragen (levering, betaling, garantie, retour)
└── Gedragsregels (wat de AI nooit mag doen)
```

**Voorbeeld aanpassing voor een restaurant:**

```text
Je bent een vriendelijke assistent voor Restaurant De Gouden Lepel in Brussel.
Openingsuren: di–zo 12:00–22:00, maandag gesloten.
Reservaties via: reservatie@goudenlepel.be of +32 2 123 45 67
...
```

---

## Projectstructuur

```
social-media-responder/
├── main.py          # CLI-interface (interactief, demo, log)
├── responder.py     # Kernlogica: escalatie, Claude API, logging
├── config.py        # Alle instellingen op één plek
├── prompts/
│   └── system_prompt.txt   # Bedrijfsprompt — hier pas je aan
├── logs/
│   └── responses.json      # Automatisch aangemaakt
└── requirements.txt
```

---

## Logbestand

Elk verwerkt bericht wordt opgeslagen in `logs/responses.json`:

```json
{
  "message": {
    "platform": "WhatsApp",
    "sender": "Marie Janssen",
    "text": "Hoe lang duurt de levering?",
    "timestamp": "2024-11-15T14:30:22"
  },
  "status": "AUTO",
  "reply": "Beste Marie, standaard levering duurt 2–3 werkdagen...",
  "escalation_hit": null,
  "processed_at": "2024-11-15T14:30:23"
}
```

---

## Uitbreidingsmogelijkheden

- **Echte API-integratie** — koppel de Facebook Graph API of WhatsApp Business API
- **Dashboard** — visualiseer het logbestand in een webbrowser
- **Meertalig** — voeg Frans of Engels toe voor Belgische bedrijven
- **Sentimentanalyse** — detecteer boze klanten vóór de escalatiecheck
- **Automatisch doorsturen** — stuur escalaties direct naar Slack of e-mail

---

## Licentie

MIT — vrij te gebruiken, aan te passen en te distribueren.

---

*Gebouwd met [Claude AI](https://anthropic.com) · voor Belgische ondernemers*
