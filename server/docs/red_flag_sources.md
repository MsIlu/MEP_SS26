# Quellenbasis der Red-Flag-Regeln

## Zweck

Die Red-Flag-Regeln dienen als sicherheitsorientierte Vorprüfung vor der KI-Antwort.  
Wenn eine Red Flag erkannt wird, wird keine reguläre KI-Antwort ausgegeben. Stattdessen wird eine fest definierte Sicherheitsaktion ausgelöst.

Die Regeln stellen keine Diagnose, keine Therapieentscheidung und keinen Ersatz für eine ärztliche Einschätzung dar.

## Fachliche Grundlage

Als initiale fachliche Orientierung wurde folgende Quelle verwendet:

Gujer, D. G. (2013): *Klinische Alarmzeichen, Red Flags, für die notfallmässige Telefonkonsultation*. Anhang zur Dissertation.

Der Anhang enthält Tabellen zu Leitsymptomen, gefährlichen Differentialdiagnosen, Alarmzeichen bzw. Red Flags/Vital Flags, Nebenkriterien und Risikofaktoren mit Literaturverzeichnis.

## Ableitung für die Anwendung

Für die Anwendung wurden aus der Quelle wiederkehrende und sicherheitsrelevante Warnzeichen ausgewählt, die sich textbasiert erkennen lassen. Dazu gehören insbesondere:

- Atemnot bzw. schwere Atembeschwerden
- Brust- oder Thoraxschmerzen mit Warnzeichen
- Bewusstseinsveränderung, Kollaps oder Synkope
- neurologische Defizite
- Krampfanfall
- starke oder unstillbare Blutung
- schwere allergische Reaktion mit Atemwegsbeteiligung
- Bauchschmerzen mit Warnzeichen
- Schwindel mit Warnzeichen
- Fieber mit Warnzeichen
- Kopfschmerzen mit Warnzeichen

Nicht alle in der Quelle genannten Red Flags wurden vollständig übernommen. Für die erste Umsetzung wurden nur solche Warnzeichen ausgewählt, die im Rahmen einer textbasierten Anwendung sinnvoll und nachvollziehbar erkannt werden können.

## Technische Umsetzung

Die fachlichen Regeln werden in folgender Datei gepflegt:

`server/data/red_flags_de.json`

Die Quellenangaben und fachliche Begründung werden bewusst getrennt vom technischen Regelkatalog dokumentiert. Dadurch kann der Regelkatalog später erweitert oder auf eine andere Quellenbasis angepasst werden, ohne die technische Struktur verändern zu müssen.

## Grenzen

Die Red-Flag-Prüfung ist eine Sicherheitsfunktion. Sie dient dazu, potenziell kritische Eingaben nicht durch eine reguläre KI-Antwort weiterverarbeiten zu lassen.

Sie ist nicht dafür vorgesehen,

- Diagnosen zu stellen,
- Behandlungen vorzuschlagen,
- ärztliche Entscheidungen zu ersetzen,
- eine vollständige medizinische Notfallabfrage abzubilden,
- oder eine verbindliche medizinische Priorisierung vorzunehmen.

## Aktueller Stand

Die aktuelle Version des Regelkatalogs enthält eine erste Auswahl besonders sicherheitsrelevanter Red-Flag-Gruppen. Weitere Regeln können später ergänzt werden, wenn zusätzliche Quellen oder fachliche Anforderungen berücksichtigt werden.